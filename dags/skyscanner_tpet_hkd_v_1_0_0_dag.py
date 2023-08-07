from airflow.models import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from datetime import datetime,timedelta
import os

dag_location = os.path.dirname(os.path.abspath(__file__))
document_path = os.path.dirname(dag_location)

default_args = {
    'start_date': datetime(2023, 7, 28),
    #'end_date' : datetime(2023, 8, 4),
    'depends_on_past': True,
    'catchup': True
}

# 定義 DAG
dag = DAG(
    'skyscanner_tpet_hkd',
    default_args=default_args,
    max_active_runs=1,
    schedule_interval='@daily',  # 指定 DAG 的執行頻率，這裡設置為每天執行一次
)

@task(task_id = "calculate_future_date",dag=dag)
def calculate_future_date(**context):
    trigger_date_str = context['ds']
    trigger_datetime = datetime.strptime(trigger_date_str, "%Y-%m-%d")
    future_datetime = trigger_datetime + timedelta(days=30)
    scrab_date = future_datetime.strftime('%y%m%d')
    print("執行日期:", trigger_datetime)
    print("執行日+30天日期:", future_datetime)
    print("查詢日期",scrab_date)
    return scrab_date
calculate_future_date_task = calculate_future_date()

web_scrab = BashOperator(
    task_id='web_scrab',
    bash_command=f"bash {dag_location}/project/skyscanner_webscrap/web_scrap.sh tpet hkd {{{{ ti.xcom_pull(task_ids='calculate_future_date') }}}}",
    dag=dag
    )

date_bigquery = BashOperator(
    task_id='date_bigquery',
    bash_command=f"bash {dag_location}/project/skyscanner_webscrap/bigquery_insert_data.sh ",
    dag=dag
)


# 定義相依性
calculate_future_date_task >> web_scrab >> date_bigquery
