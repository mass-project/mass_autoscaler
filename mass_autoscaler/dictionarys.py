from mass_api_client.resources import AnalysisSystemInstance, ScheduledAnalysis, AnalysisRequest, AnalysisSystem


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

        sysall = AnalysisSystem.all()

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





class Services:
    #service_dict: {id1: {label1: .., label2: ...} id2: label1: ..._}
    service_dict = {}
    _instance_dict = {}

    @staticmethod
    def update_dict(client, low_client):
        Services.service_dict = {}
        id_list = []
        for service in client.services.list():
            id_list.append(service.id)
        for id in id_list:
            service_info = low_client.inspect_service(id)['Spec']

            try:
                """Services.service_dict[id] = low_client.inspect_service(id)['Spec']['Labels']
                print('uno', Services.service_dict[id])"""
                Services.service_dict[id] = service_info['Labels']
                Services.service_dict[id]['replicas'] = service_info['Mode']['Replicated']['Replicas']
            except KeyError:
                pass

    @staticmethod
    def get_ids_matching_to_run_instances(client, low_client):
        #TODO it creates a list of all services with 'anal_system' as tag but doesnt check if the analysis system is connected with the server
        #TODO it only checks if label anal_sys exists. Maybe an additional nicer named label is better
        ids = []
        all_instances = AnalysisSystemInstance.all()
        for service_id in Services.service_dict:
            if 'anal_system' in Services.service_dict[service_id]:
                if service_id not in ids:
                    ids.append(service_id)
        return ids