import time
import functools
import logging

# Get the logger instance for this module
logger = logging.getLogger("logger")

def time_logger(func):
    @functools.wraps(func)  # Preserves the original function's metadata
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)  # Call the original function
        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration
        logger.info(f"Function '{func.__name__}' took {duration:.4f} seconds to execute.")
        return result  # Return the result of the original function
    return wrapper