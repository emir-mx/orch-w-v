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
from exceptions.exceptions import ConnectionException
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
        global result
        result = {"results": f"/{task_id}/"}

        def getter(task, **kwargs):
            platform = task.host.platform
            commands = list(DB.get_db()[platform][kwargs["check"]].values())
            getter = task.run(task=send_commands, commands=commands, task_id=task_id)
            if not getter.result:
                global result
                result = {"results": f"Complete with errors /{task_id}/"}
                with open("Error.txt", "a") as f:
                    f.write(f"Connection fail to {task.host.hostname}\n")
                raise ConnectionException(
                    status_code=status.SSH_255_CONNECTION_FAIL, host=task.host.hostname
                )

        for check in checks:
            nr.run(task=getter, **{"check": check})

        data = json.dumps(result, indent=4)
        requests.patch(
            url=f"{validation_endpoint}/{task_id}",
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