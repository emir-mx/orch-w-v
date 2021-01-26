from typing import List, Any
import datetime


def write_legacy_format(
    task_id: str, commands: List[str], response: Any, host: str
) -> None:
    print("IN W RESULTS")
    for command, response in zip(commands, response):
        timestamp = f"{datetime.datetime.now()}\n\n"
        with open(f"{task_id}_{host}_{command}.txt", "w") as f:
            f.write(timestamp + response.result)
