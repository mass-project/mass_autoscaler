from docker import types
import docker

client = docker.from_env()
low_client = docker.APIClient()


service = low_client.services(filters={'id': <SERVICE ID>})[0]
task_template = service['Spec']['TaskTemplate']
curr_replicas = service['Spec']['Mode']['Replicated']['Replicas']
curr_labels = service["Spec"]["Labels"]
mode = types.ServiceMode(mode='replicated', replicas=curr_replicas)
low_client.update_service(service["ID"], version=service["Version"]["Index"], task_template=task_template,name=service["Spec"]["Name"], labels=curr_labels, mode=mode)
