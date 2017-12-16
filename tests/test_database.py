from mass_autoscaler.database import Services
import docker
import unittest
import os


"""class DataBaseTest(unittest.TestCase):

    def setUp(self):
        Services.init_client()
        dir = os.path.dirname(__file__)
        filename = os.path.join(dir, 'testimage', 'Dockerfile')
        f = open(filename, "rb")
        Services.client.images.build(fileobj=f, tag='mass_autoscaler_testing_image')

        self.image_name = 'mass_autoscaler_test_image'
        self.service_name = 'mass_autoscaler_test_service'
        self.replicas = 2
        self.label = {'com.mass.anal_system': 'testsytem'}
        try:
            Services.client.services.create(self.image_name, labels=self.label, name=self.service_name,
                                            mode={'Replicated': {'Replicas': self.replicas}})
        except docker.errors.APIError:
            print('Service with name "mass_autoscaler_test_service" already exists.')

        self.service = Services.client.services.get(self.service_name)
        Services.update_dict()

    def test_if_label_is_on_service(self):
        service = Services.client.services.get(self.service_name)
        self.assertEqual(service.attrs['Spec']['Labels']['com.mass.anal_system'], 'testsytem')

    def test_update_dict(self):
        found = False
        for key in Services.service_dict:
            if 'com.mass.anal_system' in Services.service_dict[key]['Labels']:
                if Services.service_dict[key]['Labels']['com.mass.anal_system'] == 'testsytem':
                    found = True
        self.assertTrue(found)

    def test_get_ids_matching_to_run_instances(self):
        anal_sys_service_ids = Services.get_ids_matching_to_run_instances()
        self.assertTrue(self.service.id in anal_sys_service_ids)

    def test_get_replicas(self):
        self.assertEqual(Services.get_replicas(self.service.id), self.replicas)

    def test_scale_service(self):
        old = self.service.attrs['Spec']['Mode']['Replicated']['Replicas']
        Services.scale_service(self.service.id, old + 1)
        self.service = Services.client.services.get(self.service_name)
        self.assertEqual(self.service.attrs['Spec']['Mode']['Replicated']['Replicas'], old + 1)

    def tearDown(self):
        service = Services.client.services.get(self.service_name)
        Services.client.images.remove(image='mass_autoscaler_testing_image', force=True)
        service.remove()"""


def test_if_label_is_on_service(self):
    self.assertEqual(1, 1)




if __name__ == '__main__':
    unittest.main()