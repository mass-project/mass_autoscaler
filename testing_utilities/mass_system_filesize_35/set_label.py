from docker import types
import docker

client = docker.APIClient()
s = client.services(filters={'id': 'ncjg26qpluge'})[0]
task_template = s["Spec"]["TaskTemplate"]
mode = types.ServiceMode(mode='replicated', replicas=4)
client.update_service(s["ID"], version=s["Version"]["Index"], task_template=task_template, name=s["Spec"]["Name"],
                          labels={'start_demand': '3', 'lazyness': '12', 'min_inst': '4', 'max_inst': '10',
                                  'anal_system':'http://localhost:8000/api/analysis_system/size35/'}, mode=mode)
