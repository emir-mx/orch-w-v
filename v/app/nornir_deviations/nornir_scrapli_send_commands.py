"""nornir_scrapli.tasks.send_commands"""
from typing import List, Optional, Union

from nornir.core.task import Result, Task

# from nornir_scrapli.result import ScrapliResult, process_command_result
from .nornir_scrapli_results import ScrapliResult, process_command_result


def send__commands(
    task: Task,
    commands: List[str],
    strip_prompt: bool = True,
    failed_when_contains: Optional[Union[str, List[str]]] = None,
    stop_on_failed: bool = False,
    timeout_ops: Optional[float] = None,
    task_id: str = "",
) -> Result:
    """
    Send a list of commands to device using scrapli
    Args:
        task: nornir task object
        commands: list of strings to send to device in privilege exec mode
        strip_prompt: True/False strip prompt from returned output
        failed_when_contains: string or list of strings indicating failure if found in response
        stop_on_failed: True/False stop executing commands if a command fails, returns results as of
            current execution
        timeout_ops: timeout ops value for this operation; only sets the timeout_ops value for
            the duration of the operation, value is reset to initial value after operation is
            completed. Note that this is the timeout value PER COMMAND sent, not for the total
            of the commands being sent!
    Returns:
        Result: nornir result object with Result.result value set to returned scrapli Response
            object
    Raises:
        N/A
    """
    try:
        scrapli_conn = task.host.get_connection(
            "scrapli", task.nornir.config
        )  # <class 'scrapli.driver.core.cisco_iosxe.driver.IOSXEDriver'>
    except:
        result = None
        return result
    scrapli_response = scrapli_conn.send_commands(
        commands=commands,
        strip_prompt=strip_prompt,
        failed_when_contains=failed_when_contains,
        stop_on_failed=stop_on_failed,
        timeout_ops=timeout_ops,
    )

    result = ScrapliResult(
        host=task.host,
        result=process_command_result(
            scrapli_response=scrapli_response,
            commands=commands,
            task_id=task_id,
            host=task.host.hostname,
        ),
        scrapli_response=scrapli_response,
        changed=False,
    )
    return result