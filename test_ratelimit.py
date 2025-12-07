import docker

client = docker.DockerClient(
    base_url="unix:///Users/jogramnaestjernshaugen/.docker/run/docker.sock"
)
