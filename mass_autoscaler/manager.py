from database import Requests, Scheduled, Services
import time


class Manager:
    history = []
    iterator = 0

    def __init__(self, id):
        self.id = id
        self.iterator = 0
        self.history = None
        self.replicas = None
        self.anal_sys = None
        self.min_inst = None
        self.max_inst = None
        self.start_demand = None
        self.requests = None
        self.scheduled = None
        self.demand_delta_threshold = None
        self.min_schedule_interval = None
        self.max_schedule_interval = None
        self.old_demand = None
        self.demand = None
        self.weighting = None
        self.next_schedule = None

    def _update_attributes(self):
        self.replicas = Services.get_replicas(self.id)
        self.anal_sys = Services.get_anal_system(self.id)
        self.min_inst = Services.get_min_instances(self.id)
        self.max_inst = Services.get_max_instances(self.id)
        self.start_demand = Services.get_start_demand(self.id)
        self.requests = Requests.get_requests_for_system(self.anal_sys)
        self.scheduled = Scheduled.get_scheduled_for_system(self.anal_sys)
        self.calculation_technique = Services.get_calculation_technique(self.id)
        self.demand_delta_threshold = Services.get_demand_delta_threshold(self.id)
        self.min_schedule_interval = Services.get_min_schedule_interval(self.id)
        self.max_schedule_interval = Services.get_max_schedule_interval(self.id)

        if self.demand is None:
            self.demand = self.start_demand
        if self.old_demand is None:
            self.old_demand = self.start_demand
        else:
            self.old_demand = self.demand

        if self.calculation_technique == 'moving average':
            self.sensitivity = Services.get_moving_averate_sensitivity(self.id)
            if self.history is None or len(self.history) != self.sensitivity:
                self.history = [self.start_demand] * self.sensitivity

        elif self.calculation_technique == 'exponential moving average':
            self.weighting = Services.get_exponential_moving_average_weighting(self.id)
            self.sensitivity = Services.get_moving_averate_sensitivity(self.id)
            if self.history is None:
                self.history = [0] * self.sensitivity

    def _calculate_demand(self):
        if self.calculation_technique == 'exponential moving average':
            self.demand = (self.requests + self.scheduled) * self.weighting + self.demand * (1 - self.weighting)
            self.history[self.iterator] = self.demand

        elif self.calculation_technique == 'moving average':
            self.history[self.iterator] = self.requests + self.scheduled
            self.demand = sum(self.history) / len(self.history)

        if self.demand < self.min_inst:
            self.demand = self.min_inst
        elif self.demand > self.max_inst:
            self.demand = self.max_inst
        self.iterator += 1
        if self.iterator >= self.sensitivity:
            self.iterator = 0

    def _calculate_schedule(self):
        now = time.time()
        if self.old_demand / self.demand < 1 - self.demand_delta_threshold or \
                                self.demand / self.old_demand < 1 - self.demand_delta_threshold:
            self.next_schedule = now + self.min_schedule_interval
            return
        self.next_schedule = now + self.max_schedule_interval

    def debug_manager(self):
        print('servID:', self.id, 'anaSys:', self.anal_sys, 'min:', self.min_inst, 'max:',
              self.max_inst, 'req:',
              self.requests, 'sched:', self.scheduled, 'startDem:',
              self.start_demand, 'repl:', self.replicas, 'hist:', self.history, 'dem:', self.demand)

    def scale_service(self):
        if self.next_schedule is None or self.next_schedule < time.time():
            self._update_attributes()
            self._calculate_demand()
            self._calculate_schedule()
            Services.scale_service(self.id, int(self.demand))
        return self
