import json
import os
from datetime import datetime

LOG_FILE = "logs.json"


def log_interaction(data):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)


def log_feedback(data):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f)

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    logs.append(log_entry)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=2)