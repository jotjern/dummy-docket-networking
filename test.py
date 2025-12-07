import docker

client = docker.DockerClient(
    base_url="unix:///Users/jogramnaestjernshaugen/.docker/run/docker.sock"
)

container = client.containers.get("000dbd0d02a5")

print(container)
container.exec_run("tc qdisc replace dev eth0 root tbf rate 800kbit burst 800kbit latency 400ms")
