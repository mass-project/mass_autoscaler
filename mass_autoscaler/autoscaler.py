from mass_api_client import ConnectionManager
from mass_autoscaler.dictionarys import Requests, Scheduled, Services
from mass_autoscaler.manager import Manager
import mass_autoscaler.config as config
import docker
import time
import os


class Autoscaler:
    def __init__(self):
        self.managers = []

    def _debug_managers(self):
        print(time.asctime(time.localtime(time.time())))
        if len(self.managers) == 0:
            print('No running Docker-Services with MASS Analysis Systems found.')
        for manager in self.managers:
            print('servID:', manager.id, 'anaSys:', manager.anal_sys, 'min:', manager.min_inst, 'max:',
                  manager.max_inst, 'req:',
                  manager.requests, 'sched:', manager.scheduled, 'lazy:', manager.laziness, 'startDem:',
                  manager.start_demand, 'repl:', manager.replicas, 'hist:', manager._history, 'dem:', manager.demand)

    def _create_or_kill_managers(self):
        #kill unoccupied managers
        service_ids = Services.get_ids_matching_to_run_instances()
        for manager in self.managers:
            if manager.id not in service_ids:
                self.managers.remove(manager)

        # create new managers for new appeared services
        for ident in service_ids:
            found = False
            for manager in self.managers:
                if manager.id == ident:
                    found = True
                    break
            if found:
                continue
            self.managers.append(Manager(ident))

    def scale(self):
        ConnectionManager().register_connection('default', os.environ.get('API_KEY', None), config.server_addr)
        Services.client = docker.from_env()
        Services.low_client = docker.APIClient()

        while 1:
            Requests.update_dict()
            Scheduled.update_dict()
            Services.update_dict()
            self._create_or_kill_managers()
            #TODO parallelized(?)
            for manager in self.managers:
                manager.scale_service()

            self._debug_managers()
            #TODO
            time.sleep(config.scale_interval)


if __name__ == '__main__':
    scaler = Autoscaler()
    scaler.scale()
