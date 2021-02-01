from __future__ import absolute_import
import os
import sys

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_PATH)

from db.buildDB import DataBase
from nornir_deviations.InitNornir_deviation import InitNornir
from nornir_deviations.nornir_scrapli_send_commands import (
    send__commands as send_commands,
)
from exceptions import status
from exceptions.exceptions import ConnectionException, DBException
import grpc
from concurrent import futures
import time
from . import validation_pb2 as pb2
from . import validation_pb2_grpc as pb2_grpc
import requests
import json


validation_endpoint = "http://127.0.0.1:8000/api/v1/validations"
headers = {
    "Content-Type": "application/json",
}


class ValidationService(pb2_grpc.ChecksServicer):
    def __init__(self, *args, **kwargs):
        pass

    def GetChecks(self, request, context):
        task_id = request.task_id
        devices = request.devices
        checks = request.checks
        nr = InitNornir(
            config_file="/Users/emires/Desktop/DevNet/orch-w-v/v/config.yaml",
            devices=devices,
        )
        platforms = [x["platform"] for x in nr.inventory.dict()["hosts"].values()]
        platforms = set(platforms)
        DB = DataBase(platforms)
        global task_status
        task_status = 200
        global result
        result = {"results": f"/{task_id}/"}

        def getter(task, **kwargs):
            platform = task.host.platform
            # commands = list(DB.get_db()[platform][kwargs["check"]].values())
            commands = DB.get_commands(db=DB, platform=platform, check=kwargs)
            if commands:
                print("COMMANDS")
                getter = task.run(
                    task=send_commands, commands=commands, task_id=task_id
                )
                if not getter.result:
                    global result
                    global task_status
                    task_status = status.VALIDATION_COMPLETE_WITH_ERRORS
                    result = {"results": f"Complete with errors /{task_id}/"}
                    with open("Error.txt", "a") as f:
                        f.write(f"Connection fail to {task.host.hostname}\n")
                    raise ConnectionException(
                        status_code=status.SSH_255_CONNECTION_FAIL,
                        host=task.host.hostname,
                    )
                # if getter.result:
                #     task_status = 500
            else:
                # global task_status
                task_status = status.DB_CONNECTION_ERROR
                raise DBException(
                    status_code=status.DB_CONNECTION_ERROR,
                    db_url="cluster0.xlbgx.mongodb.net/checks",
                )

        for check in checks:
            print("BEFORE RUN TASK")
            nr.run(task=getter, **{"check": check})

        data = json.dumps(result, indent=4)
        print(task_status)
        requests.patch(
            url=f"{validation_endpoint}/{task_id}?q={task_status}",
            headers=headers,
            data=data,
        )
        result = {"message": "complete", "file": "output_filename.txt"}
        print(f"received {devices}{checks}")
        return pb2.MessageResponse(**result)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_ChecksServicer_to_server(ValidationService(), server)
    server.add_insecure_port("[::]:50052")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()