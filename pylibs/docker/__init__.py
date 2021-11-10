import docker


docker_client = docker.from_env()
docker_images = [image for image in docker_client.images.list()]
docker_containers = [container for container in docker_client.containers.list()]



