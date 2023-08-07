from google.cloud import bigquery
import os

class BigQueryLoader:
    def __init__(self):
        self.dataset_name = 'pdata'
        self.table_name = None
        self.schema_setting = None
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/weiche/airflow/dags/project/skyscanner_webscrap/config/skyscannerweb-3dc95bba3ffb.json"
        self.client = bigquery.Client()
    def set_table_schema(self, table_name, schema_setting):
        self.table_name = table_name
        self.schema_setting = schema_setting
        self.table_ref = self.client.dataset(self.dataset_name).table(self.table_name)
        self.job_config = bigquery.LoadJobConfig(**self.schema_setting)
    def load_data_from_csv(self, file_path):
        if self.table_name is None or self.schema_setting is None:
            raise ValueError("Table name and schema setting must be set before loading data.")
        with open(file_path, 'rb') as source_file:
            job = self.client.load_table_from_file(source_file, self.table_ref, job_config=self.job_config)
            job.result()  # Wait for the job to complete
            print('Insert Data to BigQuery Done')
if __name__ == '__main__':
    BigQueryLoader()