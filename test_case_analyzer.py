import json


with open("config_files/test.raw.json", "r") as file:
    data = json.load(file)


template_dict = {}

for item in data:
    intent_template_id = item["intent_template_id"]
    if intent_template_id not in template_dict:
        template_dict[intent_template_id] = {"intent_template": item["intent_template"], "task_ids": [item["task_id"]]}
    else:
        template_dict[intent_template_id]["task_ids"].append(item["task_id"])


import csv

# Prepare data for CSV
csv_data = [["intent_template_id", "intent_template", "task_ids", "num_tasks"]]
for intent_template_id, data in template_dict.items():
    intent_template = data['intent_template'].replace('"', '""')  # Escape double quotes
    task_ids = ','.join(map(str, data['task_ids']))
    csv_data.append([intent_template_id, intent_template, task_ids, len(data["task_ids"])])

# Write to CSV file
with open('template_analysis.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    csv_writer.writerows(csv_data)

print("Data has been written to template_analysis.csv")
