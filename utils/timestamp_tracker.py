from datetime import datetime, timezone
import os

# Define a path for the timestamp file
TIMESTAMP_FILE = "last_run_time.txt"


def save_last_run_time(timestamp: int = None):
    """
    Save the current Unix timestamp to a file. 
    
    Optionally accepts a custom timestamp.
    """
    if timestamp is None:
        timestamp = int(datetime.now(timezone.utc).timestamp())
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(timestamp))


def load_last_run_time():
    """
    Load the last saved Unix timestamp from a file.
    Returns 0 if the file doesn't exist.
    """
    if not os.path.exists(TIMESTAMP_FILE):
        return 0
    with open(TIMESTAMP_FILE, "r") as f:
        return int(f.read().strip())


def update_last_run_time():
    current_ts = int(datetime.now(timezone.utc).timestamp())
    with open(TIMESTAMP_FILE, "w") as f:
        f.write(str(current_ts))
