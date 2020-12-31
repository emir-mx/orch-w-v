from pymongo import MongoClient
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
import grpc
from concurrent import futures
import time
import validation_pb2 as pb2
import validation_pb2_grpc as pb2_grpc

client = MongoClient(
    "mongodb+srv://emires:Pepies2020@cluster0.xlbgx.mongodb.net/checks?retryWrites=true&w=majority"
)
db = client["checks"]

collections = db.get_collection("collection_checks")

ios_cli = collections.find({"platform.ios.method.cli": {"$exists": "true"}})

ios_cli_dict = ios_cli[0]["platform"]["ios"]["method"]["cli"]

health = ios_cli_dict["health"]


nr = InitNornir(config_file="config.yaml")


class ValidationService(pb2_grpc.ChecksServicer):
    def __init__(self, *args, **kwargs):
        pass

    def GetChecks(self, request, context):
        devices = request.devices
        checks = request.checks
        # pre = request.pre
        # post = request.post
        #
        # print(checks)

        def get_health(task):
            print(checks)
            task.run(task=netmiko_send_command, command_string=health[checks[0]])

        result = nr.run(task=get_health)

        result = result["internet-rtr01"][1]

        with open(f"{result.host}.txt", "w") as f:
            f.write(result.result)

        result = {"message": "complete", "file": f"{result.host}.txt"}
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