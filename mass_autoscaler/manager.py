import subprocess
from database import Requests, Scheduled, Services


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
        self.requests = None
        self.scheduled = None
        self.start_demand = None
        self.demand = None
        self.replicas = None
        self.weighting = None

    def _update_attributes(self):
        self.replicas = Services.get_replicas(self.id)
        self.anal_sys = Services.get_anal_system(self.id)
        self.min_inst = Services.get_min_instances(self.id)
        self.max_inst = Services.get_max_instances(self.id)
        self.start_demand = Services.get_start_demand(self.id)
        self.requests = Requests.requests_for_system(self.anal_sys)
        self.scheduled = Scheduled.scheduled_for_system(self.anal_sys)
        self.calculation_technique = Services.get_calculation_technique(self.id)
        if self.calculation_technique == 'moving average':
            self.sensitivity = Services.get_moving_averate_sensitivity(self.id)
            if self._history is None or len(self._history) != self.sensitivity:
                self._history = [self.start_demand] * self.sensitivity
        elif self.calculation_technique == 'exponential moving average':
            self.weighting = Services.get_exponential_moving_average_weighting(self.id)
            if self.demand is None:
                self.demand = self.start_demand
            self.sensitivity = Services.get_moving_averate_sensitivity(self.id)
            if self._history is None:
                self._history = [0] * self.sensitivity

    def _calculate_demand(self):
        if self.calculation_technique == 'exponential moving average':
            self.demand = (self.requests + self.scheduled) * self.weighting + self.demand * (1 - self.weighting)
            self._history[self._iterator] = self.demand

        elif self.calculation_technique == 'moving average':
            self._history[self._iterator] = self.requests + self.scheduled
            self.demand = int(sum(self._history) / len(self._history))

        if self.demand < self.min_inst:
            self.demand = self.min_inst
        elif self.demand > self.max_inst:
            self.demand = self.max_inst
        self._iterator += 1
        if self._iterator >= self.sensitivity:
            self._iterator = 0

    def debug_manager(self):
        print('servID:', self.id, 'anaSys:', self.anal_sys, 'min:', self.min_inst, 'max:',
              self.max_inst, 'req:',
              self.requests, 'sched:', self.scheduled, 'startDem:',
              self.start_demand, 'repl:', self.replicas, 'hist:', self._history, 'dem:', self.demand)

    def scale_service(self):
        self._update_attributes()
        self._calculate_demand()
        Services.scale_service(self.id, int(self.demand))

        return self
