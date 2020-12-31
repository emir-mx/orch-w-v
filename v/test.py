from nornir import InitNornir
from nornir.core.task import Result
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command

nr = InitNornir(config_file="config.yaml")


def hello(task):
    # host = task.host
    # with open("test.txt", "w") as f:
    #     f.write(Result(host, result="TEST {}".format(host)))
    # return Result(host, result="TEST {}".format(host))
    task.run(task=netmiko_send_command, command_string="show version | incl software")
    # return result
    # return Result(host, result=result)


result = nr.run(task=hello)

result = result["internet-rtr01"]
print(result)

# print(r)
# print(result.keys())
# print(result["internet-rtr01"][0])

# with open(f"{r.host}.txt", "w") as f:
#     f.write(r.result)

# print_result(result)
