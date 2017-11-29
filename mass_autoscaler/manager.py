from mass_autoscaler.database import Requests, Scheduled, Services
from docker import types


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
        self.laziness = None
        self.requests = None
        self.scheduled = None
        self.start_demand = None
        self.demand = None
        self.replicas = None

    def _update_attributes(self):
        self.replicas = Services.get_replicas(self.id)
        self.anal_sys = Services.get_anal_system(self.id)
        self.min_inst = Services.get_min_instances(self.id)
        self.max_inst = Services.get_max_instances(self.id)
        self.laziness = Services.get_laziness(self.id)
        self.start_demand = Services.get_start_demand(self.id)
        if self._history is None or len(self._history) != Services.get_laziness(self.id):
            self._history = [self.start_demand] * self.laziness

        if self.anal_sys in Requests.request_dict:
            self.requests = Requests.requests_for_system(self.anal_sys)
        else:
            self.requests = 0
        if self.anal_sys in Scheduled.scheduled_dict:
            self.scheduled = Scheduled.scheduled_for_system(self.anal_sys)
        else:
            self.scheduled = 0

    def _calculate_demand(self):
        #placeholder
        self._history[self._iterator] = self.requests + self.replicas + self.scheduled
        self.demand = int(sum(self._history) / len(self._history))

        if self.demand < self.min_inst:
            self.demand = self.min_inst
        elif self.demand > self.max_inst:
            self.demand = self.max_inst
        self._iterator += 1
        if self._iterator >= self.laziness:
            self._iterator = 0

    def debug_manager(self):
        print('servID:', self.id, 'anaSys:', self.anal_sys, 'min:', self.min_inst, 'max:',
              self.max_inst, 'req:',
              self.requests, 'sched:', self.scheduled, 'lazy:', self.laziness, 'startDem:',
              self.start_demand, 'repl:', self.replicas, 'hist:', self._history, 'dem:', self.demand)

    def scale_service(self):
        # TODO Optimierung: ganze Liste der Services cachen, filtern und die einzelnen Manager den jew.Service übergeben
        # TODO in database.py auslagern
        # TODO exception tritt auf wenn service im falschen moment von aussen beendet wird. service = low_client.services(filters={'id': self.id})[0] out of range + weitere zeilen müssen exceptions abgefangen werden
        """self._update_attributes()
        self._calculate_demand()
        service = low_client.services(filters={'id': self.id})[0]
        task_template = service['Spec']['TaskTemplate']
        #curr_replicas = service['Spec']['Mode']['Replicated']['Replicas']
        curr_labels = service["Spec"]["Labels"]
        mode = types.ServiceMode(mode='replicated', replicas=self.demand)
        low_client.update_service(service["ID"], version=service["Version"]["Index"], task_template=task_template,
                                  name=service["Spec"]["Name"], labels=curr_labels, mode=mode)"""

        #placeholder for testing
        self._update_attributes()
        self._calculate_demand()
        service = Services.low_client.services(filters={'id': self.id})[0]
        task_template = service['Spec']['TaskTemplate']
        curr_replicas = service['Spec']['Mode']['Replicated']['Replicas']
        curr_labels = service["Spec"]["Labels"]
        mode = types.ServiceMode(mode='replicated', replicas=curr_replicas)
        Services.low_client.update_service(service["ID"], version=service["Version"]["Index"],
                                           task_template=task_template, name=service["Spec"]["Name"],
                                           labels=curr_labels, mode=mode)
        return self
