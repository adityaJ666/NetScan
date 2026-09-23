import json
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

HISTORY_FILE = os.path.join(
    DATA_DIR,
    "scan_history.json"
)


def load_history():
    """Load all saved scan records."""

    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def save_scan(result):
    """Save a completed scan."""

    os.makedirs(
        DATA_DIR,
        exist_ok=True
    )

    history = load_history()

    record = {
        "timestamp": result.get(
            "timestamp",
            ""
        ),
        "target": result.get(
            "target",
            ""
        ),
        "ip": result.get(
            "ip",
            ""
        ),
        "start_port": result.get(
            "start_port",
            0
        ),
        "end_port": result.get(
            "end_port",
            0
        ),
        "total_ports": result.get(
            "total_ports",
            0
        ),
        "open_ports": result.get(
            "open_ports",
            len(result.get("results", []))
        ),
        "scan_duration": result.get(
            "scan_duration",
            0
        ),
        "results": result.get(
            "results",
            []
        )
    }

    history.append(record)

    with open(
        HISTORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            history,
            file,
            indent=4
        )


def get_history():
    """Return saved scan history."""

    return load_history()