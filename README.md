# 一、專題摘要
1. 專題主題 : Skyscanner網站爬蟲
2. 目標:
   * 獲得從臺灣->日本涵館的航班資訊，例如出發/抵達時間、飛行時間、價格、轉機地點/次數、航空公司...等資訊
   * 爬取的資訊寫入csv檔，再導入bigquery
   * 利用Airflow建立排程，完成前2項工作
   * 利用looker將儲存在bigquery的資料，進行資料視覺化
# 二、流程圖:
![link](images/流程圖.png)
# 三、程式說明:
序號|路徑|程式名稱|功能敘述
|:---|:----|:----|:----|
1|dags/|skyscanner_tpet_hkd_v_1_0_0_dag.py|1.Airflow的排程程式，共有3個Task:<br>a. calculate_future_date_task:依據執行日期+30日，並搭配xcom作為後續爬蟲的日期參數<br>b. web_scrab:使用Bash的方式呼叫web_scrap.sh程式。<br>c. date_bigquery:使用Bash的方式呼叫bigquery_insert_data.sh程式
2|dags/project/scanner_webscrap/|web_scrap.sh|呼叫爬蟲主程式，必需提供的參數分別為 出發地、抵達地、出發日期
3|dags/project/scanner_webscrap/|web_scrap.py|呼叫main_skyscanner_scrapper.py，進行爬取相關資訊
4|dags/project/scanner_webscrap/tools/|main_skyscanner_scrapper.py|1.爬取資訊的主要程式<br>2.分成去程&去程+回程的版本<br>3.預設:搭機人數為1人、僅查詢去程資訊
5|dags/project/scanner_webscrap/|bigquery_insert_data.sh|呼叫資料導入bigquery程式
6|dags/project/scanner_webscrap/|bigquery_insert_data.py|讀取/date目錄中的csv檔，呼叫data_importer.py，分別將最新的檔案導入bigquery
7|dags/project/scanner_webscrap/tools/|data_importer.py|1.建立bigquery連線<br>2.讀取預先建立好的schema(bigquery_config.py)<br>3.導入資料
# 四、背景資訊、程式開發流程、過程(遇到的問題&解決措施):
1. Skyscanner網站背景資訊:
   * url結構:
     - 去程: https://www.skyscanner.com.tw/transport/flights/出發地/目的地/出發日期/?成人人數
       - 例如: https://www.skyscanner.com.tw/transport/flights/tpet/hkd/230807/?adultsv2=1
     - 去程+回程: https://www.skyscanner.com.tw/transport/flights/出發地/目的地/出發日期/回程日期/?成人人數
       - 例如: https://www.skyscanner.com.tw/transport/flights/tpet/hkd/230811/230914/?adultsv2=1
     - 還有其他參數，例如艙等、小孩人數等。這邊只用了出發地、目的地、出發日期、人數等資訊。
   * 欲爬取的目標資訊:
     ![link](images/目標資訊.PNG)
2. 流程:
   * 透過undected-selenium的方式並依據url的結構進行爬蟲:
     - https://www.skyscanner.com.tw/transport/flights/tpet/hkd/{date}/?adultsv2=1
   * 將爬取到的資訊儲存至csv檔案:
     - 航班敘述
     - 航程票價
     - 航程資訊
   * 爬取的資訊都存成csv檔案後，再把資訊導入bigquery
     - skyscannerweb.pdata.flight_memo
     - skyscannerweb.pdata.flight_price
     - skyscannerweb.pdata.flight_go_plan
3. 開發過程(遇到的問題&解決措施):
   * 爬蟲:
     - 航班敘述、航程票價的資訊跟航程資訊的class_ 位置不同，為了讓之後的資料可以做對應，採用uuid.uuid4()的方式建立primary key
     - 航程資訊中的航空公司呈現方式不同，例如當航次有轉機，且搭配不同的航空公司，網頁資訊會用文字來代替，如果只有一間，會用該公司的圖片呈現。因為這個機制，在抓取時，會去判斷是否有img['alt']標籤，無則抓取text
     - 航程資訊中的轉機地點可能會有1個以上。原本都只抓到第一個轉機地點，後來發現轉機地點的問題，所以將資訊儲存到list裡面做保存
     - 航程資訊中的抵達時間處理。網頁呈現的抵達時間只會呈現時分的資訊，如果跨日會有特別的註記。為了方便處理，這邊是依據出發時間+花費時間的資訊，自行產生一個抵達時間
   * BigQuery:
     - 看到滿多人將csv檔的資料先儲存至colud storage，然後再從storage導入bigquery。這邊的作法是直接把csv導入bigquery，主要是想說儲存到storage需要一些費用，但如果直接進bigquery可以有免費額度使用。
   * Airflow:
     - 在環境建置上花了很多時間，原本是透過docker的方式進行Airflow練習，但使用docker環境部屬程式後，遇到package,程式路徑,無視窗GUI等問題，後來就改在local的方式建立Airflow環境
     - 在設計dag時，想說如果每次爬蟲時，都是去查詢當日的航班資訊，滿奇怪的，飛機可能都要飛走了XD，所以就採用執行日+30天的方式去查詢
     - 在使用BashOperator時，啟動sh程式時，有發生錯誤，經查資料後，如果你的sh程式沒有要帶任何參數進去，需要空一格，才不會發生錯誤
     - 如果想要執行多日的DAG，為了讓DAG可以一天一天有順序的執行，這邊採用'depends_on_past': True、max_active_runs=1的方式去做控制
## 五、Looker Dashboard:
.........
    
    
