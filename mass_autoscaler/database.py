from mass_api_client.resources import AnalysisSystemInstance, ScheduledAnalysis, AnalysisRequest, AnalysisSystem
import configparser
import docker
import subprocess


class Configuration:
    config = None

    @staticmethod
    def update_config():
        Configuration.config = configparser.ConfigParser()
        Configuration.config.read('config.ini')
        if not Configuration.config.has_section('Basic Properties'):
            Configuration.config.add_section('Basic Properties')
        if not Configuration.config.has_option('Basic Properties', 'Server Address'):
            Configuration.config.set('Basic Properties', 'Server Address', 'http://localhost:8000/api/')
        if not Configuration.config.has_option('Basic Properties', 'API KEY'):
            Configuration.config.set('Basic Properties', 'API KEY', '<api key>')
        if not Configuration.config.has_option('Basic Properties', 'Min Scale Interval'):
            Configuration.config.set('Basic Properties', 'Min Scale Interval', '5')
        if not Configuration.config.has_option('Basic Properties', 'Debug'):
            Configuration.config.set('Basic Properties', 'Debug', 'true')

        if not Configuration.config.has_section('Default Values'):
            Configuration.config.add_section('Default Values')
        if not Configuration.config.has_option('Default Values', 'Default Minimum'):
            Configuration.config.set('Default Values', 'Default Minimum', '3')
        if not Configuration.config.has_option('Default Values', 'Default Maximum'):
            Configuration.config.set('Default Values', 'Default Maximum', '15')
        if not Configuration.config.has_option('Default Values', 'Default Start Demand'):
            Configuration.config.set('Default Values',  'Default Start Demand', '3')
        if not Configuration.config.has_option('Default Values', 'Default Calculation Technique'):
            Configuration.config.set('Default Values', 'Default Calculation Technique', 'moving average')
        if not Configuration.config.has_option('Default Values', 'Default Min Schedule Interval'):
            Configuration.config.set('Default Values', 'Default Min Schedule Interval', '5')
        if not Configuration.config.has_option('Default Values', 'Default Max Schedule Interval'):
            Configuration.config.set('Default Values', 'Default Max Schedule Interval', '30')
        if not Configuration.config.has_option('Default Values', 'Default Demand Delta Threshold'):
            Configuration.config.set('Default Values', 'Default Demand Delta Threshold', '0.5')

        if not Configuration.config.has_section('Moving Average Defaults'):
            Configuration.config.add_section('Moving Average Defaults')
        if not Configuration.config.has_option('Moving Average Defaults', 'Default sensitivity'):
            Configuration.config.set('Moving Average Defaults', 'Default sensitivity', '15')

        if not Configuration.config.has_section('Exponential Moving Average Defaults'):
            Configuration.config.add_section('Exponential Moving Average Defaults')
        if not Configuration.config.has_option('Exponential Moving Average Defaults', 'Default Weighting'):
            Configuration.config.set('Exponential Moving Average Defaults', 'Default Weighting', '0.3')
        with open('config.ini', 'w') as configfile:
            Configuration.config.write(configfile)


class Requests:
    request_dict = {}

    @staticmethod
    def update_dict(system_dict):
        Requests.request_dict = {}
        all_requests = AnalysisRequest.all()
        for request in all_requests:
            if request.analysis_system in Requests.request_dict:
                Requests.request_dict[request.analysis_system] += 1
            else:
                Requests.request_dict[request.analysis_system] = 1

        Requests.request_dict = dict((system_dict[key], value) for (key, value) in Requests.request_dict.items())

    @staticmethod
    def get_requests_for_system(name):
        if name in Requests.request_dict:
            return Requests.request_dict[name]
        return 0


class Scheduled:
    _all_scheduled_dict = {}
    _instance_dict = {}
    scheduled_dict = {}

    @staticmethod
    def update_dict(system_dict):
        Scheduled._all_scheduled_dict = {}
        Scheduled._instance_dict = {}
        Scheduled.scheduled_dict = {}
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

        Scheduled.scheduled_dict = dict((system_dict[key], value) for (key, value) in Scheduled.scheduled_dict.items())

    @staticmethod
    def get_scheduled_for_system(name):
        if name in Scheduled.scheduled_dict:
            return Scheduled.scheduled_dict[name]
        return 0


class Services:
    client = None
    service_dict = {}

    @staticmethod
    def get_anal_system(service_id):
        return Services.service_dict[service_id]['Labels']['com.mass.anal_system']

    @staticmethod
    def get_replicas(service_id):
        return int(Services.service_dict[service_id]['Mode']['Replicated']['Replicas'])

    @staticmethod
    def get_calculation_technique(service_id):
        if 'com.mass.calculation_technique' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.calculation_technique'])
        return Configuration.config.get('Default Values', 'default calculation technique')

    @staticmethod
    def get_moving_averate_sensitivity(service_id):
        if 'com.mass.m_a_sensitivity' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.m_a_sensitivity'])
        return Configuration.config.getint('Moving Average Defaults', 'default sensitivity')

    @staticmethod
    def get_exponential_moving_average_weighting(service_id):
        if 'com.mass.e_m_a_weighting' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.e_m_a_sensitivity'])
        return Configuration.config.getfloat('Exponential Moving Average Defaults', 'default weighting')

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
    def get_start_demand(service_id):
        if 'com.mass.start_demand' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.start_demand'])
        return Configuration.config.getint('Default Values', 'default start demand')

    @staticmethod
    def get_min_schedule_interval(service_id):
        if 'com.mass.min_schedule_interval' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.min_schedule_interval'])
        return Configuration.config.getint('Default Values', 'Default Min Schedule Interval')

    @staticmethod
    def get_max_schedule_interval(service_id):
        if 'com.mass.max_schedule_interval' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.max_schedule_interval'])
        return Configuration.config.getint('Default Values', 'Default Max Schedule Interval')

    @staticmethod
    def get_demand_delta_threshold(service_id):
        if 'com.mass.demand_delta_threshold' in Services.service_dict[service_id]['Labels']:
            return int(Services.service_dict[service_id]['Labels']['com.mass.demand_delta_threshold'])
        return Configuration.config.getfloat('Default Values', 'Default Demand Delta Threshold')

    @staticmethod
    def scale_service(service_id, demand):
        try:
            subprocess.run('docker service scale ' + str(service_id) + '=' + str(int(demand)) + ' -d=true', shell=True,
                           check=True, stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print('WARNING: Cannot scale Service with ID=' + str(service_id) + '. Maybe it was removed.')

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

    @staticmethod
    def init_client():
        Services.client = docker.from_env()


def update_database():
    system_dict = {}
    all_systems = AnalysisSystem.all()
    for system in all_systems:
        system_dict[system.url] = system.identifier_name
    Requests.update_dict(system_dict)
    Scheduled.update_dict(system_dict)
    Services.update_dict()
