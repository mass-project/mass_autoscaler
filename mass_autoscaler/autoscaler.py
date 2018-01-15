from mass_api_client import ConnectionManager
from database import Services, Configuration, update_database
from manager import Manager
from multiprocessing import Pool
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
        server_address = os.environ.get('MASS_SERVER_ADDRESS', Configuration.config.get('Basic Properties',
                                                                                        'server address'))
        ConnectionManager().register_connection('default', api_key, server_address)
        Services.init_client()
        while 1:

            update_database()
            self._create_or_kill_managers()
            if Configuration.config.getboolean('Basic Properties', 'Debug'):
                print(time.asctime(time.localtime(time.time())))
            if len(self.managers) == 0:
                if Configuration.config.getboolean('Basic Properties', 'Debug'):
                    print('No running Docker-Services with MASS-Analysis-Systems found.')
            else:
                with Pool() as p:
                    self.managers = p.map(wrap_scale, self.managers)
                    if Configuration.config.getboolean('Basic Properties', 'Debug'):
                        p.map(wrap_debug, self.managers)

            now = time.time()
            next_scale = Configuration.config.getint('Basic Properties', 'Base Scale Interval') + now
            for manager in self.managers:
                if manager.next_schedule < next_scale:
                    next_scale = manager.next_schedule
            min_next_scale = Configuration.config.getint('Basic Properties', 'Min Scale Interval') + now
            if next_scale < min_next_scale:
                next_scale = min_next_scale

            if next_scale - now > 0:
                time.sleep(next_scale - now)


if __name__ == '__main__':
    Configuration.update_config()
    scaler = Autoscaler()
    scaler.scale()
