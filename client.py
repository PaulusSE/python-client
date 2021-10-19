import time
import socket
import re


class ClientError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class Client:
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.timestamp = int(time.time())

    def put(self, metric_name, metric_value, timestamp=False):
        if not timestamp:
            timestamp = self.timestamp
        sock = socket.create_connection((self.host, self.port))
        sock.sendall(str.encode("put {0} {1} {2}\n".format(metric_name, metric_value, timestamp)))
        data = sock.recv(1024)
        respose_proc(data)
        sock.close()

    def get(self, metric_value):
        sock = socket.create_connection((self.host, self.port))
        sock.sendall(str.encode("get {}\n".format(metric_value)))
        data = sock.recv(1024)
        dict = respose_proc(data)
        sock.close()
        return dict


def respose_proc(data):
    result1 = re.match(r'^b\'ok\\n\w+.\w+ \d+', str(data))
    result2 = re.match(r'^b\'ok\\n\\n', str(data))
    if not result1 and not result2:
        raise ClientError("ClientError")
    data = str(data).split('\\n')
    data.pop(0)
    dict = {}
    for i in range(len(data)):
        if data[i] != '' and data[i] != "'":
            metrics = data[i].split(" ")
            try:
                metrics[1] = float(metrics[1])
                metrics[2] = int(metrics[2])
                if metrics[0] not in dict:
                    dict[metrics[0]] = list()
                    dict[metrics[0]].append((metrics[2], metrics[1]))
                else:
                    dict[metrics[0]].append((metrics[2], metrics[1]))
            except:
                raise ClientError("ClientError")
    for value in dict:
        dict[value].sort()
    return dict
