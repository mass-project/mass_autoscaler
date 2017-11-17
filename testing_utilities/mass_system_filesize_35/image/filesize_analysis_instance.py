import time
import os
from mass_api_client import ConnectionManager
from mass_api_client.utils import process_analyses, get_or_create_analysis_system_instance


def size_analysis(scheduled_analysis):
   sample = scheduled_analysis.get_sample()
   with sample.temporary_file() as f:
       sample_file_size = os.path.getsize(f.name)

   size_report = {'sample_file_size': sample_file_size}
   print('sleep start')
   time.sleep(35)
   print('sleep')
   print('sleep over')
   scheduled_analysis.create_report(
        json_report_objects={'size_report': ('size_report', size_report)},
        )


if __name__ == "__main__":
    ConnectionManager().register_connection('default', 'IjVhMDc1ODQzNjEzYmM2NzUzNWNiYjI0ZiI.t1ThLvNRAP-B7xvUcxDYNVhjNU8', ' http://192.168.0.108:8000/api/')
    print('start')

    analysis_system_instance = get_or_create_analysis_system_instance(identifier='size35',
                                                                      verbose_name= 'Size Analysis Client35',
                                                                     tag_filter_exp='sample-type:filesample',
                                                                      )
    process_analyses(analysis_system_instance, size_analysis, sleep_time=7)
