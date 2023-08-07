import os
from tools.data_importer import BigQueryLoader
from config.bigquery_config import schema_setting

def get_latest_file_path(prefix, folder):
    files = [f for f in os.listdir(folder) if f.startswith(prefix)]
    latest_file = sorted(files, key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)[0]
    print(f"最新創建的{prefix}檔案是: {latest_file}")
    return os.path.join(folder, latest_file)

def load_data_to_bigquery(table_name, schema, data_path):
    loader = BigQueryLoader()
    loader.set_table_schema(table_name, schema)
    loader.load_data_from_csv(data_path)
    
if __name__ == "__main__":
    main_path = os.getcwd()  # 程式所在的目錄路徑
    data_path = 'data'
    combine_path = os.path.join(main_path, data_path)  # 檔案所在的目錄路徑

    # flight_price
    table_name_flight_price = 'flight_price'
    flight_price_prefix = "flight_price"  # 檔案名稱前綴
    flight_price_data_path = get_latest_file_path(flight_price_prefix, combine_path)
    load_data_to_bigquery(table_name_flight_price, schema_setting['flight_price'], flight_price_data_path)

    # flight_memo
    table_name_flight_memo = 'flight_memo'
    flight_memo_prefix = "flight_memo"  # 檔案名稱前綴
    flight_memo_data_path = get_latest_file_path(flight_memo_prefix, combine_path)
    load_data_to_bigquery(table_name_flight_memo, schema_setting['memo'], flight_memo_data_path)

    # flight_go_plan
    table_name_flight_go_plan = 'flight_go_plan'
    flight_go_plan_prefix = "go_plan"  # 檔案名稱前綴
    flight_go_plan_data_path = get_latest_file_path(flight_go_plan_prefix, combine_path)
    load_data_to_bigquery(table_name_flight_go_plan, schema_setting['flight_go_plan'], flight_go_plan_data_path)


