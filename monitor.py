import threading
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import docker
import json
import time

from docker.models.containers import Container

client = docker.DockerClient(
    base_url="unix:///Users/jogramnaestjernshaugen/.docker/run/docker.sock"
)

client

# network = [net for net in client.networks.list() if net.attrs["Labels"].get("com.docker.compose.project") == "dummydockernetworking"][0]
network = client.networks.get("8d1f35c43884")

containers = {}

def format_bytes(num, _pos=None):
  for unit in ["B", "KB", "MB", "GB", "TB"]:
    if abs(num) < 1024.0 or unit == "TB":
      return f"{num:.1f}{unit}"
    num /= 1024.0

def container_logger(container: Container):
  global containers

  containers[container.name] = []
  for stat_bytes in container.stats():
    stat = json.loads(stat_bytes.decode())
    network_stats = stat["networks"]["eth0"]
    containers[container.name].append({"outbound": network_stats["tx_bytes"], "inbound": network_stats["rx_bytes"], "timestamp": time.time()})

print(len(network.containers), "containers in network")
for container in network.containers:
  print(container.name)

  threading.Thread(target=container_logger, args=(container,)).start()

plt.ion()
fig, ax = plt.subplots()
manager = plt.get_current_fig_manager()
if hasattr(manager, "window"):
  window = manager.window
  if hasattr(window, "raise_"):
    window.raise_ = lambda *_, **__: None
  if hasattr(window, "activateWindow"):
    window.activateWindow = lambda *_, **__: None

for rate_limit_kb in [100, 75, 50, 25, 10, 5, 3, 2, 1]:
  for container in network.containers:
    if "talker" in container.name:
     print("Output from tc command in", container.name,":", container.exec_run(f"/bin/sh -c 'tc qdisc replace dev eth0 root tbf rate {rate_limit_kb * 8}kbit burst {rate_limit_kb * 8}kbit latency 400ms && echo Success!'").output)
     # print("Output from tc command in", container.id,":", container.exec_run(f"/bin/sh -c 'echo {rate_limit_kb * 8}kbit > /tmp/file'").output)
  
  print(f"TESTING RATE LIIMT OF {rate_limit_kb}kbits")

  for x in range(100):
      # print(f"\tStep #{x+1}:")
      if not plt.fignum_exists(fig.number):
        break
      for container_name, data in containers.items():
        if not data:
          continue
        latest = data[-1]
        # print(f"\t\t{container_name}: inbound={format_bytes(latest['inbound'])} outbound={format_bytes(latest['outbound'])}")

      ax.clear()
      ax.set_title("Container Network Traffic")
      ax.set_xlabel("Time (s)")
      ax.set_ylabel("Bytes")
      ax.yaxis.set_major_formatter(FuncFormatter(format_bytes))
      ax.grid(True, linestyle="--", linewidth=0.5)
      plotted = False
      for container_name, data in containers.items():
        if not data:
          continue
        start_time = data[0]["timestamp"]
        times = [stat["timestamp"] - start_time for stat in data]
        inbound_values = [stat["inbound"] for stat in data]
        outbound_values = [stat["outbound"] for stat in data]
        inbound_deltas = [0] + [curr - prev for prev, curr in zip(inbound_values, inbound_values[1:])]
        outbound_deltas = [0] + [curr - prev for prev, curr in zip(outbound_values, outbound_values[1:])]
        ax.plot(times, inbound_deltas, label=f"{container_name} inbound")
        ax.plot(times, outbound_deltas, label=f"{container_name} outbound", linestyle="--")
        plotted = True
      fig.tight_layout()
      plt.pause(0.1)
