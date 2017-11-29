from mass_api_client.resources import AnalysisSystemInstance, ScheduledAnalysis, AnalysisRequest
import configparser


class Configuration:
    config = None

    @staticmethod
    def update_config():
        Configuration.config = configparser.ConfigParser()
        Configuration.config.read('config.ini')
        if not Configuration.config.has_section('Default Values'):
            Configuration.config.add_section('Default Values')
        if not Configuration.config.has_option('Default Values', 'Scale Interval'):
            Configuration.config.set('Default Values', 'Scale Interval', '15')
        if not Configuration.config.has_option('Default Values', 'Default Minimum'):
            Configuration.config.set('Default Values', 'Default Minimum', '3')
        if not Configuration.config.has_option('Default Values', 'Default Maximum'):
            Configuration.config.set('Default Values', 'Default Maximum', '15')
        if not Configuration.config.has_option('Default Values', 'Default Start Demand'):
            Configuration.config.set('Default Values',  'Default Start Demand', '3')
        if not Configuration.config.has_option('Default Values', 'Default Laziness'):
            Configuration.config.set('Default Values', 'Default Laziness', '20')
        if not Configuration.config.has_section('Basic Properties'):
            Configuration.config.add_section('Basic Properties')
        if not Configuration.config.has_option('Basic Properties', 'Server Address'):
            Configuration.config.set('Basic Properties', 'Server Address', 'http://localhost:8000/api/')
        if not Configuration.config.has_option('Basic Properties', 'Scale Interval'):
            Configuration.config.set('Basic Properties', 'Scale Interval', '30')
        with open('config.ini', 'w') as configfile:
            Configuration.config.write(configfile)


class Requests:
    request_dict = {}

    @staticmethod
    def update_dict():
        Requests.request_dict = {}
        all_requests = AnalysisRequest.all()
        for request in all_requests:
            if request.analysis_system in Requests.request_dict:
                Requests.request_dict[request.analysis_system] += 1
            else:
                Requests.request_dict[request.analysis_system] = 1

    @staticmethod
    def requests_for_system(name):
        if name in Requests.request_dict:
            return Requests.request_dict[name]
        return 0


    #creates a dict of all analyse systems and their counts of scheduled analysis
    #offline systems are ignored
class Scheduled:
    _all_scheduled_dict = {}
    _instance_dict = {}
    scheduled_dict = {}

    @staticmethod
    def update_dict():
        Scheduled._all_scheduled_dict = {}
        Scheduled._instance_dict = {}
        Scheduled.scheduled_dict = {}
        Scheduled.url_list = []
        all_scheduled = ScheduledAnalysis.all()
        all_instances = AnalysisSystemInstance.all()

        for scheduled in all_scheduled:
            if scheduled.analysis_system_instance in Scheduled._all_scheduled_dict:
                Scheduled._all_scheduled_dict[scheduled.analysis_system_instance] += 1
            else:
                Scheduled._all_scheduled_dict[scheduled.analysis_system_instance] = 1
        for instance in all_instances:
            if instance.is_online:
                Scheduled._instance_dict[instance.url] = instance.analysis_system

        for instance_address in Scheduled._all_scheduled_dict:
            if instance_address in Scheduled._instance_dict:
                if Scheduled._instance_dict[instance_address] not in Scheduled.scheduled_dict:
                    Scheduled.scheduled_dict[Scheduled._instance_dict[instance_address]] = \
                    Scheduled._all_scheduled_dict[instance_address]
                else:
                    Scheduled.scheduled_dict[Scheduled._instance_dict[instance_address]] += \
                    Scheduled._all_scheduled_dict[instance_address]

    @staticmethod
    def scheduled_for_system(name):
        if name in Scheduled.scheduled_dict:
            return Scheduled.scheduled_dict[name]
        return 0


class Services:
    client = None
    low_client = None
    #service_dict: {id1: {label1: .., label2: ...} id2: label1: ..._}
    service_dict = {}

    @staticmethod
    def get_anal_system(service_id):
        return Services.service_dict[service_id]['Labels']['com.mass.anal_system']

    @staticmethod
    def get_replicas(service_id):
        return int(Services.service_dict[service_id]['Mode']['Replicated']['Replicas'])

    @staticmethod
    def get_min_instances(service_id):
        if 'com.mass.min_inst' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.min_inst'])
        return Configuration.config.getint('Default Values', 'default minimum')

    @staticmethod
    def get_max_instances(service_id):
        if 'com.mass.max_inst' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.max_inst'])
        return Configuration.config.getint('Default Values', 'default maximum')

    @staticmethod
    def get_laziness(service_id):
        if 'com.mass.laziness' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.laziness'])
        return Configuration.config.getint('Default Values', 'default laziness')

    @staticmethod
    def get_start_demand(service_id):
        if 'com.mass.start_demand' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.start_demand'])
        return Configuration.config.getint('Default Values', 'default start demand')

    @staticmethod
    def update_dict():
        Services.service_dict = {}
        _services = Services.client.services.list()
        for service in _services:
            Services.service_dict[service.id] = service.attrs['Spec']

    @staticmethod
    def get_ids_matching_to_run_instances():
        ids = []
        for service_id in Services.service_dict:
            if 'com.mass.anal_system' in Services.service_dict[service_id]['Labels']:
                if service_id not in ids:
                    ids.append(service_id)
        return ids


def update_database():
    Requests.update_dict()
    Scheduled.update_dict()
    Services.update_dict()
