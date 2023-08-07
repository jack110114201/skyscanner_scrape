# 一、專題摘要
1. 專題主題 : Skyscanner網站爬蟲
2. 目標:
   * 獲得班次相關資訊，例如出發/抵達時間、飛行時間、價格、航空公司...等資訊
   * 爬取的資訊寫入csv檔，再導入bigquery
   * 利用Airflow建立排程，完成前2項工作
   * 利用looker將bigquery的資料，進行資料視覺化
# 二、流程圖:
![link](images/流程圖.png)
# 三、程式說明:
序號|路徑|程式名稱|功能敘述
|:---|:----|:----|:----|
1|dags/|skyscanner_tpet_hkd_v_1_0_0_dag.py|xxxxx
2|dags/project/scanner_webscrap/|web_scrap.sh|xxxxx
3|dags/project/scanner_webscrap/|web_scrap.py|xxxxx
4|dags/project/scanner_webscrap/tools/|main_skyscanner_scrapper.py|xxxxx
5|dags/project/scanner_webscrap/|bigquery_insert_data.sh|xxxxx
6|dags/project/scanner_webscrap/|bigquery_insert_data.py|xxxxx
7|dags/project/scanner_webscrap/tools/|data_importer.py|xxxxx
