from mass_api_client import ConnectionManager
from mass_autoscaler.dictionarys import Requests, Scheduled, Services
from docker import types
import mass_autoscaler.config as config
import docker
import time
import os


class Manager:
    _history = []
    _iterator = 0

    def __init__(self, id):
        self.id = id
        self._iterator = 0
        self._history = None
        self.anal_sys = None
        self.min_inst = None
        self.max_inst = None
        self.lazyness = None
        self.requests = None
        self.scheduled = None
        self.start_demand = None
        self.demand = None
        self.replicas = None

    def _update_attributes(self, service_info, request_dict, scheduled_dict):
        #TODO hide service info in dictionary.py an create methods to work on this ressources
        self.replicas = int(service_info[self.id]['replicas'])
        self.anal_sys = service_info[self.id]['com.mass.anal_system']
        self.min_inst = int(service_info[self.id]['com.mass.min_inst'])
        self.max_inst = int(service_info[self.id]['com.mass.max_inst'])
        self.lazyness = int(service_info[self.id]['com.mass.laziness'])
        self.start_demand = int(service_info[self.id]['com.mass.start_demand'])
        if self._history is None:
            self._history = [self.start_demand] * self.lazyness
        elif len(self._history) != int(service_info[self.id]['com.mass.laziness']):
            self._history = [self.start_demand] * self.lazyness
        if service_info[self.id]['com.mass.anal_system'] in Requests.request_dict:
            self.requests = request_dict[service_info[self.id]['com.mass.anal_system']]
        else:
            self.requests = 0
        if service_info[self.id]['com.mass.anal_system'] in Scheduled.scheduled_dict:
            self.scheduled = scheduled_dict[service_info[self.id]['com.mass.anal_system']]
        else:
            self.scheduled = 0

    def _calculate_demand(self):
        self._history[self._iterator] = self.requests + self.replicas + self.scheduled
        self.demand = int(sum(self._history) / len(self._history))

        if self.demand < self.min_inst:
            self.demand = self.min_inst
        elif self.demand > self.max_inst:
            self.demand = self.max_inst
        self._iterator += 1
        if self._iterator >= self.lazyness:
            self._iterator = 0



    def scale_service(self, low_client):

        """self._calculate_demand()
        #TODO Optimierung: ganze Liste der Services cachen, filtern und die einzelnen Manager den jew.Service übergeben
        #TODO in dictionarys.py auslagern
        #TODO exception tritt auf wenn service im falschen moment von aussen beendet wird. service = low_client.services(filters={'id': self.id})[0] out of range + weitere zeilen müssen exceptions abgefangen werden
        service = low_client.services(filters={'id': self.id})[0]
        task_template = service['Spec']['TaskTemplate']
        #curr_replicas = service['Spec']['Mode']['Replicated']['Replicas']
        curr_labels = service["Spec"]["Labels"]
        mode = types.ServiceMode(mode='replicated', replicas=self.demand)
        low_client.update_service(service["ID"], version=service["Version"]["Index"], task_template=task_template,
                                  name=service["Spec"]["Name"], labels=curr_labels, mode=mode)"""

        #placeholder for testing
        self._calculate_demand()
        service = low_client.services(filters={'id': self.id})[0]
        task_template = service['Spec']['TaskTemplate']
        curr_replicas = service['Spec']['Mode']['Replicated']['Replicas']
        curr_labels = service["Spec"]["Labels"]
        mode = types.ServiceMode(mode='replicated', replicas=curr_replicas)
        low_client.update_service(service["ID"], version=service["Version"]["Index"], task_template=task_template,
                                  name=service["Spec"]["Name"], labels=curr_labels, mode=mode)


class JobSpooler:
    def __init__(self):
        self.managers = []

    def update_managers(self, client, low_client):
        #kill unoccupied managers
        Requests.update_dict()
        Scheduled.update_dict()
        Services.update_dict(client, low_client)
        service_ids = Services.get_ids_matching_to_run_instances(client, low_client)
        service_info = Services.service_dict
        for manager in self.managers:
            if manager.id not in service_ids:
                self.managers.remove(manager)

        # create new managers for new appeared services
        for id in service_ids:
            found = False
            for manager in self.managers:
                if manager.id == id:
                    found = True
                    break
            if found:
                break
            self.managers.append(Manager(id))

        #update manager data
        request_dict = Requests.request_dict
        scheduled_dict = Scheduled.scheduled_dict
        for manager in self.managers:
            manager._update_attributes(service_info, request_dict, scheduled_dict)

    def spool(self):
        ConnectionManager().register_connection('default', os.environ.get('API_KEY', None), config.server_addr)
        client = docker.from_env()
        low_client = docker.APIClient()

        while 1:
            # TODO parallelized(?)
            self.update_managers(client, low_client)
            for manager in self.managers:
                manager.scale_service(low_client)

            print(time.asctime(time.localtime(time.time())))
            if len(self.managers) == 0:
                print('No running Docker-Services with MASS Analysis Systems found.')
            for manager in self.managers:
                print('servID:', manager.id, 'anaSys:', manager.anal_sys, 'min:', manager.min_inst, 'max:', manager.max_inst, 'req:',
                      manager.requests, 'sched:', manager.scheduled, 'lazy:', manager.lazyness, 'startDem:',
                      manager.start_demand, 'repl:', manager.replicas, 'hist:', manager._history, 'dem:', manager.demand)
            #TODO
            time.sleep(config.scale_interval)


if __name__ == '__main__':
    spooler = JobSpooler()
    spooler.spool()