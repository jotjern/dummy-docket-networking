import json
import os

def format_bits(bytes_value: float) -> str:
    bits = bytes_value * 8
    
    if bits < 1_000_000:
        return f"{bits / 1_000:.2f} Kbit/s"
    elif bits < 1_000_000_000:
        return f"{bits / 1_000_000:.0f} Mbit/s"
    else:
        return f"{bits / 1_000_000_000:.0f} Gbit/s"


all_run_data = []

for file in os.listdir("data"):
  all_run_data.append(json.load(open("data/" + file)))

for run_data in sorted(all_run_data, key=lambda run_data: run_data["metadata"]["talker_outbound_ratelimit_kbits"], reverse=True):
  container_data = [
    {
      "outbound": container_data["measurements"][-1]["outbound"] - container_data["measurements"][0]["outbound"],
      "inbound": container_data["measurements"][-1]["inbound"] - container_data["measurements"][0]["inbound"]
    }
    for _, container_data in run_data["data"].items()
    if container_data["type"] == "listener"
  ]

  print(f'{format_bits(run_data["metadata"]["talker_outbound_ratelimit_kbits"]):>16}', sum([data["inbound"] for data in container_data]) / len(container_data))
