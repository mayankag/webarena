import os
import argparse
import json
from typing import Any

import tiktoken
from beartype import beartype

from agent.prompts import *
from browser_env import Trajectory
from browser_env.actions import (
    Action,
    ActionParsingError,
    create_id_based_action,
    create_none_action,
    create_playwright_action,
)
from browser_env.utils import Observation, StateInfo
from llms import (
    call_llm,
    generate_from_huggingface_completion,
    generate_from_openai_chat_completion,
    generate_from_openai_completion,
    lm_config,
)
from llms.tokenizers import Tokenizer
from openai import OpenAI
import base64
import numpy as np
from PIL import Image
import io

from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from enum import Enum

class Agent:
    """Base class for the agent"""

    def __init__(self, *args: Any) -> None:
        pass

    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: Any
    ) -> Action:
        """Predict the next action given the observation"""
        raise NotImplementedError

    def reset(
        self,
        test_config_file: str,
    ) -> None:
        raise NotImplementedError





class ActionType(str, Enum):
    CLICK = "click"
    TYPE = "type"
    HOVER = "hover"
    SCROLL = "scroll"
    KEY_PRESS = "press"
    GOTO_URL = "goto"
    NEW_TAB = "new_tab"
    CLOSE_TAB = "close_tab"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"
    TAB_FOCUS = "tab_focus"
    STOP = "stop"
class LLMAction(BaseModel):
    element_id: Optional[str] = Field(None, description="The ID of the element to interact with")
    text: Optional[str] = Field(None, description="Text to type or URL to navigate to")
    direction: Optional[Literal["up", "down"]] = Field(None, description="Scroll direction")
    key_comb: Optional[str] = Field(None, description="Key combination to press")
    press_enter_after: Optional[bool] = Field(None, description="Whether to press Enter after typing")
    tab_index: Optional[int] = Field(None, description="Index of the tab to focus on")
    answer: Optional[str] = Field(None, description="Answer for the stop action")

class LLMResponse(BaseModel):
    thought: str = Field(..., description="Chain of thought reasoning")
    action: ActionType = Field(..., description="The chosen action type")
    action_args: Optional[LLMAction] = Field(None, description="Arguments for the chosen action")
    #memory: Optional[str] = Field(None, description="Information to commit to memory")
    class Config:
        use_enum_values = True


class TeacherForcingAgent(Agent):
    """Agent that follows a pre-defined action sequence"""

    def __init__(self) -> None:
        super().__init__()

    def set_action_set_tag(self, tag: str) -> None:
        self.action_set_tag = tag

    def set_actions(self, action_seq: str | list[str]) -> None:
        if isinstance(action_seq, str):
            action_strs = action_seq.strip().split("\n")
        else:
            action_strs = action_seq
        action_strs = [a.strip() for a in action_strs]

        actions = []
        for a_str in action_strs:
            try:
                if self.action_set_tag == "playwright":
                    cur_action = create_playwright_action(a_str)
                elif self.action_set_tag == "id_accessibility_tree":
                    cur_action = create_id_based_action(a_str)
                else:
                    raise ValueError(
                        f"Unknown action type {self.action_set_tag}"
                    )
            except ActionParsingError as e:
                cur_action = create_none_action()

            cur_action["raw_prediction"] = a_str
            actions.append(cur_action)

        self.actions: list[Action] = actions

    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: Any
    ) -> Action:
        """Predict the next action given the observation"""
        return self.actions.pop(0)

    def reset(
        self,
        test_config_file: str,
    ) -> None:
        with open(test_config_file) as f:
            ref_actions = json.load(f)["reference_action_sequence"]
            tag = ref_actions["action_set_tag"]
            action_seq = ref_actions["action_sequence"]
            self.set_action_set_tag(tag)
            self.set_actions(action_seq)


class PromptAgent(Agent):
    """prompt-based agent that emits action given the history"""

    @beartype
    def __init__(
        self,
        action_set_tag: str,
        lm_config: lm_config.LMConfig,
        prompt_constructor: PromptConstructor,
    ) -> None:
        super().__init__()
        self.lm_config = lm_config
        self.prompt_constructor = prompt_constructor
        self.action_set_tag = action_set_tag

    def set_action_set_tag(self, tag: str) -> None:
        self.action_set_tag = tag

    @beartype
    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: dict[str, Any]
    ) -> Action:
        prompt = self.prompt_constructor.construct(
            trajectory, intent, meta_data
        )
        lm_config = self.lm_config
        n = 0
        while True:
            response = call_llm(lm_config, prompt)
            force_prefix = self.prompt_constructor.instruction[
                "meta_data"
            ].get("force_prefix", "")
            response = f"{force_prefix}{response}"
            n += 1
            try:
                parsed_response = self.prompt_constructor.extract_action(
                    response
                )
                if self.action_set_tag == "id_accessibility_tree":
                    action = create_id_based_action(parsed_response)
                elif self.action_set_tag == "playwright":
                    action = create_playwright_action(parsed_response)
                else:
                    raise ValueError(
                        f"Unknown action type {self.action_set_tag}"
                    )
                action["raw_prediction"] = response
                break
            except ActionParsingError as e:
                if n >= lm_config.gen_config["max_retry"]:
                    action = create_none_action()
                    action["raw_prediction"] = response
                    break

        return action

    def reset(self, test_config_file: str) -> None:
        pass


class CustomAgent(Agent):
    """my custom agent that emits action given the history"""

    @beartype
    def __init__(
        self,
        # action_set_tag: str,
        # lm_config: lm_config.LMConfig,
        # prompt_constructor: PromptConstructor,
    ) -> None:
        super().__init__()
        OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        #self.lm_config = lm_config
        #self.prompt_constructor = prompt_constructor
        #self.action_set_tag = action_set_tag


    def _system_prompt(self) -> str:
        with open("agent/prompts/custom_agent_instructions.md", "r") as f:
            return f.read()


    # def encode_image(self, image_array: np.ndarray) -> str:
    #     pil_image = Image.fromarray(image_array)
    #     byte_io = io.BytesIO()
    #     pil_image.save(byte_io, format="PNG")
    #     byte_io.seek(0)
    #     return base64.b64encode(byte_io.read()).decode("utf-8")

    @beartype
    def next_action(
        self, trajectory: Trajectory, intent: str, meta_data: dict[str, Any]
    ) -> Action:

        prompt = self.construct_prompt(trajectory, intent, meta_data)
        # image = trajectory[-1]["observation"]["image"]
        # image_str = self.encode_image(image)
        response = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": self._system_prompt()},
                {"role": "user", "content": prompt},
            ],
            response_format=LLMResponse,
        )

        llm_response = response.choices[0].message.parsed
        # Convert LLMResponse to Action
        action = self.convert_llm_response_to_action(llm_response)
        action["raw_prediction"] = llm_response.model_dump_json()
        return action

    def construct_prompt(self, trajectory: Trajectory, intent: str, meta_data: dict[str, Any]) -> str:
        state_info: StateInfo = trajectory[-1]
        obs = state_info["observation"]["text"]
        url = state_info["info"]["page"].url
        previous_action_str = meta_data["action_history"][-1]
        context = f"""
        Objective: {intent}
        URL: {self.map_url_to_real(url)}
        Observation: {obs}
        Previous Action: {previous_action_str}
        """
        return context
        # if self.past_responses:
        #     context += "\nPast Actions:\n"
        #     for response in self.past_responses:
        #         context += f"Thought: {response.thought}\nAction: {response.action} {response.action_args}\n"
        # if self.memory:
        #     context += "\nMemory:\n"
        #     for item in self.memory:
        #         context += f"- {item}\n"
        # return context


    def convert_llm_response_to_action(self, llm_response: LLMResponse) -> Action:
        if llm_response.action == ActionType.CLICK:
            return create_id_based_action(f"click[{llm_response.action_args.element_id}]")
        elif llm_response.action == ActionType.TYPE:
            return create_id_based_action(f"type[{llm_response.action_args.element_id}][{llm_response.action_args.text}][{int(llm_response.action_args.press_enter_after)}]")
        elif llm_response.action == ActionType.HOVER:
            return create_id_based_action(f"hover[{llm_response.action_args.element_id}]")
        elif llm_response.action == ActionType.KEY_PRESS:
            return create_id_based_action(f"press[{llm_response.action_args.key_comb}]")
        elif llm_response.action == ActionType.SCROLL:
            return create_id_based_action(f"scroll[{llm_response.action_args.direction}]")
        elif llm_response.action == ActionType.NEW_TAB:
            return create_id_based_action("new_tab")
        elif llm_response.action == ActionType.TAB_FOCUS:
            return create_id_based_action(f"tab_focus[{llm_response.action_args.tab_index}]")
        elif llm_response.action == ActionType.CLOSE_TAB:
            return create_id_based_action("close_tab")
        elif llm_response.action == ActionType.GOTO_URL:
            return create_id_based_action(f"goto[{llm_response.action_args.url}]")
        elif llm_response.action == ActionType.GO_BACK:
            return create_id_based_action("go_back")
        elif llm_response.action == ActionType.GO_FORWARD:
            return create_id_based_action("go_forward")
        elif llm_response.action == ActionType.STOP:
            return create_id_based_action(f"stop[{llm_response.action_args.answer}]")
        else:
            return create_none_action()

    def map_url_to_real(self, url: str) -> str:
        for local, real in URL_MAPPINGS.items():
            if local in url:
                return url.replace(local, real)
        return url


    def reset(self, test_config_file: str) -> None:
        pass


def construct_agent(args: argparse.Namespace) -> Agent:
    llm_config = lm_config.construct_llm_config(args)

    agent: Agent
    if args.agent_type == "teacher_forcing":
        agent = TeacherForcingAgent()
    elif args.agent_type == "custom":
        # TODO: build the agent based on the custom instructions
        agent = CustomAgent()
    elif args.agent_type == "prompt":
        with open(args.instruction_path) as f:
            constructor_type = json.load(f)["meta_data"]["prompt_constructor"]
        tokenizer = Tokenizer(args.provider, args.model)
        prompt_constructor = eval(constructor_type)(
            args.instruction_path, lm_config=llm_config, tokenizer=tokenizer
        )
        agent = PromptAgent(
            action_set_tag=args.action_set_tag,
            lm_config=llm_config,
            prompt_constructor=prompt_constructor,
        )
    else:
        raise NotImplementedError(
            f"agent type {args.agent_type} not implemented"
        )
    return agent
