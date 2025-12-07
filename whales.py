import json
from python_on_whales import Container, DockerClient
import time

def format_bits(bits: float) -> str:
    if bits < 1_000:
        return f"{bits:.2f} bit/s"
    elif bits < 1_000_000:
        return f"{bits / 1_000:.2f} Kbit/s"
    elif bits < 1_000_000_000:
        return f"{bits / 1_000_000:.2f} Mbit/s"
    else:
        return f"{bits / 1_000_000_000:.2f} Gbit/s"

def limit_network_traffic(container: Container, rate_limit_kbits: int):
    stdout = container.execute(
        ["sh", "-lc", f"tc qdisc replace dev eth0 root tbf rate {rate_limit_kbits}kbit burst {rate_limit_kbits}kbit latency 400ms && echo SUCCESS"]
    )
    assert stdout == "SUCCESS"


docker = DockerClient(compose_files=["./docker-compose.yml"])

n_listeners = 10
talker_outbound_ratelimit_kbits = 12_500
n_measurements = 100

print("Cleaning up compose...")
docker.compose.down()

print("Starting compose...")
docker.compose.up(detach=True, scales={"listener": n_listeners}, build=True)

talker_containers = docker.compose.ps(services=["talker"])
listener_containers = docker.compose.ps(services=["listener"])
all_containers = docker.compose.ps(services=["listener", "talker"])

assert len(listener_containers) == n_listeners

for talker_container in talker_containers:
    print(f"Limiting network traffic for {talker_container.name}")
    limit_network_traffic(talker_container, talker_outbound_ratelimit_kbits)

print("Waiting 5s for connections to establish...")
time.sleep(5)

data = {
container.id: {
    "measurements": [],
    "name": container.name,
    "type": "listener" if container in listener_containers else ("talker" if container in talker_containers else (1 / 0))
}
for container in all_containers
}

for i in range(n_measurements):
    stats = docker.stats(all_containers)
    
    for stat in stats:
        data[stat.container_id]["measurements"].append({
            "outbound": stat.net_download,
            "inbound": stat.net_upload
        })
    print(f"Measurement #{i+1} taken")
    
print("Stopping docker compose...")
docker.compose.down()

print("\nResults:")
for container_id, container_data in data.items():
    if len(container_data) < 2:
        continue
    
    deltas_up = [b["outbound"] - a["outbound"] 
                for a, b in zip(container_data["measurements"], 
                                container_data["measurements"][1:])]
    deltas_down = [b["inbound"] - a["inbound"] 
                for a, b in zip(container_data["measurements"], 
                                container_data["measurements"][1:])]
    
    avg_outbound = sum(deltas_up) / len(deltas_up)
    avg_inbound = sum(deltas_down) / len(deltas_down)
    
    print(f"{container_id[:12]}:")
    print(f"  outbound (TX):   {format_bits(avg_outbound)} bytes/interval")
    print(f"  inbound (RX): {format_bits(avg_inbound)} bytes/interval")

with open(f"data/run-{n_listeners}-{n_measurements}-{talker_outbound_ratelimit_kbits}", "w", encoding="utf-8") as fw:
    json.dump({
    "metadata": {
        "n_listeners": n_listeners,
        "talker_outbound_ratelimit_kbits": talker_outbound_ratelimit_kbits,
        "n_measurements": n_measurements
    },
    "data": data
    }, fw, indent=4)

