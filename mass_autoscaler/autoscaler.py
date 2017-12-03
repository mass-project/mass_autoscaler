from mass_api_client import ConnectionManager
from database import Services, Configuration, update_database
from manager import Manager
from multiprocessing import Pool
import docker
import time
import os


def wrap_debug(manager):
    return manager.debug_manager()


def wrap_scale(manager):
    return manager.scale_service()


class Autoscaler:
    def __init__(self):
        self.managers = []

    def _create_or_kill_managers(self):
        # kill unoccupied managers
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
        api_key = os.environ.get('MASS_API_KEY', Configuration.config.get('Basic Properties', 'api key'))
        server_address = os.environ.get('MASS_SERVER_ADDRESS', Configuration.config.get('Basic Properties', 'server address'))
        ConnectionManager().register_connection('default', api_key, server_address)
        Services.client = docker.from_env()
        Services.low_client = docker.APIClient()

        while 1:
            update_database()
            self._create_or_kill_managers()

            print(time.asctime(time.localtime(time.time())))
            if len(self.managers) == 0:
                print('No running Docker-Services with MASS Analysis Systems found.')
            else:
                with Pool() as p:
                    self.managers = p.map(wrap_scale, self.managers)
                    p.map(wrap_debug, self.managers)

            time.sleep(Configuration.config.getint('Basic Properties', 'Scale Interval'))


if __name__ == '__main__':
    Configuration.update_config()
    scaler = Autoscaler()
    scaler.scale()
