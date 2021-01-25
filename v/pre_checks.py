from db.buildDB import DataBase
from nornir_deviations.InitNornir_deviation import InitNornir
from nornir_deviations.nornir_scrapli_send_commands import (
    send__commands as send_commands,
)
import grpc
from concurrent import futures
import time
import validation_pb2 as pb2
import validation_pb2_grpc as pb2_grpc
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
        nr = InitNornir(config_file="config.yaml", devices=devices)
        platforms = [x["platform"] for x in nr.inventory.dict()["hosts"].values()]
        platforms = set(platforms)
        DB = DataBase(platforms)
        output_path = {"results": f"/{task_id}/pre"}

        def getter(task, **kwargs):
            print("IN GETTER")
            platform = task.host.platform
            commands = list(DB.get_db()[platform][kwargs["check"]].values())
            getter = task.run(task=send_commands, commands=commands, task_id=task_id)
            s = "*" * 40
            result = f"{getter.result}\n\n{s}"
            with open(f"{kwargs['check']}.txt", "a") as f:
                f.write(result)

        print("before for")
        for check in checks:
            print("getter")
            nr.run(task=getter, **{"check": check})

        # def get_health(task):
        #     print(checks)
        #     task.run(
        #         task=netmiko_send_command,
        #         command_string=DB.get_db()["ios"][checks[0]]["running"],
        #     )

        # result = nr.run(task=get_health)

        # result = result["internet-rtr01"][1]

        # output_filename = f"{task_id[0:8]}_{result.host}.txt"

        # with open(output_filename, "w") as f:
        #     f.write(result.result)
        data = json.dumps(output_path, indent=4)
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