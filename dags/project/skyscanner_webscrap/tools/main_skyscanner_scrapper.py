import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import uuid
import csv
from datetime import timedelta
import datetime
import time
import os

class SkyscannerScrapper_plan():
    def __init__(self):
        self.uuid_list = []
        self.url = 'https://www.skyscanner.com.tw/transport/flights'
        self.script_dir = os.path.dirname(os.path.abspath('__file__'))
        self.current_datetime = datetime.datetime.now()
        self.current_date = self.current_datetime.date()
        self.flight_memo = {
                       'flight_uuid' : ''
                      ,'memo' : ''
                      ,'check_date' : ''
                      }
        self.flight_price = {
                             'flight_uuid' : ''
                            ,'single_price' : ''
                            ,'check_date' : ''
                            }
        self.go_plan = {
                         'flight_uuid' : ''
                        ,'company' : ''
                        ,'trans_plan':[]
                        ,'trans_cnt' : ''
                        ,'takeoff_time' : ''
                        ,'land_time' :''
                        ,'takeoff_location' : ''
                        ,'land_location' : ''
                        ,'spend_time' : ''
                        ,'spend_hr' : ''
                        ,'spend_min' : ''
                        ,'check_date' : ''
                        }  
        self.bk_plan = {
                        'flight_uuid' : ''
                        ,'company' : ''
                        ,'trans_plan': []
                        ,'trans_cnt' : ''
                        ,'takeoff_time' : ''
                        ,'land_time': ''
                        ,'takeoff_location' : ''
                        ,'land_location' : ''
                        ,'spend_time' : ''
                        ,'spend_hr' : ''
                        ,'spend_min' : ''
                        ,'check_date' : ''
                       }
    def scrape_trip_plan(self,takeoff_location,land_location,go_plan_date,people = 1,bk_plan_date = None):
        options = uc.ChromeOptions()
        options.headless=True  
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        browser = uc.Chrome(options=options)
        if bk_plan_date == None:
            scrap_url = f'{self.url}/{takeoff_location}/{land_location}/{go_plan_date}/?adultsv2={people}'
        else:
            scrap_url = f'{self.url}/{takeoff_location}/{land_location}/{go_plan_date}/{bk_plan_date}/?adultsv2={people}'
        print(scrap_url)
        browser.get(scrap_url)
        time.sleep(35) #等待網頁搜尋
        # 點擊顯示更多結果
        browser.find_element(By.XPATH, '//*[@id="app-root"]/div[1]/div/div/div/div[1]/button').click()
        
        past_height = ''
        current_height = ''
        while True:
            browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            time.sleep(5)
            current_height = browser.execute_script("return document.body.scrollHeight")
            print('current_height:',current_height)
            print('past_height:',past_height)
            if past_height == current_height:
                print('Closed for now') #網頁已經滑到底部了
                break
            else:
                past_height = current_height
                print('網頁更新中...')
        html_source = browser.page_source
        soup = BeautifulSoup(html_source, "html.parser")
        trip_info = soup
        browser.quit()
        return trip_info

    def trip_plan_memo(self,trip_info,createtime,bk_plan_date= None):
        if bk_plan_date == None:
            flight_memo_path = os.path.join(self.script_dir,f'data/flight_memo_{createtime}.csv')
            flight_price_path = os.path.join(self.script_dir,f'data/flight_price_{createtime}.csv')
        else:
           flight_memo_path = os.path.join(self.script_dir,f'data/round_flight_memo_{createtime}.csv')
           flight_price_path = os.path.join(self.script_dir,f'data/round_flight_price_{createtime}.csv')
        with open(flight_memo_path,'w',newline='', encoding="utf8") as flight_memo_file,\
             open(flight_price_path,'w',newline='', encoding="utf8") as flight_price_file:
            flight_memo_writer = csv.DictWriter(flight_memo_file, fieldnames=[*self.flight_memo.keys()], delimiter="|")
            flight_price_writer = csv.DictWriter(flight_price_file, fieldnames=[*self.flight_price.keys()], delimiter="|")
            flight_memo_writer.writeheader()
            flight_price_writer.writeheader()
            memo = trip_info.find_all("div",class_ = 'UpperTicketBody_screenReaderOnly__YTY2Z') #敘述整體航班資訊
            for i in memo:
                flight_uuid = uuid.uuid4() #建立航班的PK用
                self.uuid_list.append(flight_uuid)
                # 處理memo資訊
                self.flight_memo['flight_uuid'] = flight_uuid
                self.flight_memo['memo'] = i.text.split('：')[1]
                self.flight_memo['check_date'] = self.current_date
                flight_memo_writer.writerow(self.flight_memo)
    
                # 處理航班價格資訊
                self.flight_price['flight_uuid'] = flight_uuid
                self.flight_price['single_price'] = ''.join(filter(str.isdigit, i.text.split('：')[1].split('。')[0].split('；')[0])) #單人費用
                self.flight_price['check_date'] = self.current_date
                flight_price_writer.writerow(self.flight_price)
                print('memo:',self.flight_memo)
                print('flight_price:',self.flight_price)
    def trip_plan_detail(self,round_trip_info,go_plan_date,createtime,bk_plan_date = None):
        if bk_plan_date == None:
            go_plan_path = os.path.join(self.script_dir,f'data/go_plan_{createtime}.csv')
            with open(go_plan_path,'w',newline='', encoding="utf8") as go_plan_file:
                go_plan_writer = csv.DictWriter(go_plan_file, fieldnames=[*self.go_plan.keys()], delimiter="|")
                go_plan_writer.writeheader()
                products = round_trip_info.find_all("div",class_ = 'UpperTicketBody_legsContainer__ZjcyZ') #航班去回程時間/轉機等資訊
                cnt = 0 #取uuid_list用
                for k in products:
                    uuid_pk = self.uuid_list[cnt]
                    self.go_plan['flight_uuid'] = uuid_pk
                    print('開始處理去程資訊:')
                    go_info = k.find_all("div",class_ = 'LegDetails_container__MTkyZ UpperTicketBody_leg__MmNkN')[0] #去程
                    #去程航空公司(如果有2班以上的航空公司,以文字呈現,一間以圖片呈現,抓alt文字)
                    company = go_info.find("div",class_ = 'LogoImage_container__MDU0Z LegLogo_logoContainer__ODdkM UpperTicketBody_legLogo__ZjYwM')
                    try:
                        self.go_plan['company'] = company.find("div",class_ = 'BpkImage_bpk-image__YTkyO BpkImage_bpk-image--no-background__NGMyN').img['alt']
                    except:
                        self.go_plan['company'] = company.text
                    #去程轉機地點
                    trans_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopStation__M2E5N')
                    for location in trans_location:
                        self.go_plan['trans_plan'].append(location.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY').text)
                    if not self.go_plan['trans_plan']:
                        no_trans = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelGreen__YWM4M')
                        self.go_plan['trans_plan'].append(no_trans.text) #直飛
                    #去程轉機次數
                    try:
                        trans_cnt = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelRed__NTY2Y')
                        self.go_plan['trans_cnt'] = re.search(r'\d+', trans_cnt.text).group()
                    except:
                        self.go_plan['trans_cnt'] = 0
                    #去程花費時間
                    go_spend = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY Duration_duration__NmUyM').text
                    self.go_plan['spend_time'] = go_spend
                    try:
                        spend_hr = int(''.join(filter(str.isdigit, go_spend.split('小時')[0])))
                        self.go_plan['spend_hr'] = spend_hr
                    except:
                        self.go_plan['spend_hr'] = 0
                    try:
                        spend_min = int(''.join(filter(str.isdigit, go_spend.split('小時')[1])))
                        self.go_plan['spend_min'] = spend_min
                    except:
                        self.go_plan['spend_min'] = 0
                    #去程出發、抵達時間
                    takeoff_time = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--subheading__NzkwO')[0].text
                    takeoff_datetime_tmp = go_plan_date + ' ' + takeoff_time
                    takeoff_datetime = datetime.datetime.strptime(takeoff_datetime_tmp, '%y%m%d %H:%M')
                    land_datetime = takeoff_datetime + timedelta(hours = spend_hr) + timedelta(minutes = spend_min)
                    self.go_plan['takeoff_time'] = takeoff_datetime
                    self.go_plan['land_time'] = land_datetime
                    #去程的出發地&目的地
                    takeoff_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[0]
                    land_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[1]
                    self.go_plan['takeoff_location'] = takeoff_location.text
                    self.go_plan['land_location'] = land_location.text
                    self.go_plan['check_date'] = self.current_date
                    go_plan_writer.writerow(self.go_plan)
                    print('go_plan:',self.go_plan)
                    self.go_plan['trans_plan'].clear()
                    print('去程資訊處理完成')
                    cnt += 1               
        else:
            go_plan_path = os.path.join(self.script_dir,f'data/round_go_plan_{createtime}.csv')
            bk_plan_path = os.path.join(self.script_dir,f'data/round_bk_plan_{createtime}.csv')
            with open(go_plan_path,'w',newline='', encoding="utf8") as go_plan_file,\
                 open(bk_plan_path,'w',newline='', encoding="utf8") as bk_plan_file:
                go_plan_writer = csv.DictWriter(go_plan_file, fieldnames=[*self.go_plan.keys()], delimiter="|")
                bk_plan_writer = csv.DictWriter(bk_plan_file, fieldnames=[*self.bk_plan.keys()], delimiter="|")
                go_plan_writer.writeheader()
                bk_plan_writer.writeheader()
                products = round_trip_info.find_all("div",class_ = 'UpperTicketBody_legsContainer__ZjcyZ') #航班去回程時間/轉機等資訊
                cnt = 0 #取uuid_list用
                for k in products:
                    uuid_pk = self.uuid_list[cnt]
                    self.go_plan['flight_uuid'] = uuid_pk
                    print('開始處理去程資訊:')
                    go_info = k.find_all("div",class_ = 'LegDetails_container__MTkyZ UpperTicketBody_leg__MmNkN')[0] #去程
                    #去程航空公司(如果有2班以上的航空公司,以文字呈現,一間以圖片呈現,抓alt文字)
                    company = go_info.find("div",class_ = 'LogoImage_container__MDU0Z LegLogo_logoContainer__ODdkM UpperTicketBody_legLogo__ZjYwM')
                    try:
                        self.go_plan['company'] = company.find("div",class_ = 'BpkImage_bpk-image__YTkyO BpkImage_bpk-image--no-background__NGMyN').img['alt']
                    except:
                        self.go_plan['company'] = company.text
                    #去程轉機地點
                    trans_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopStation__M2E5N')
                    for location in trans_location:
                        self.go_plan['trans_plan'].append(location.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY').text)
                    if not self.go_plan['trans_plan']:
                        no_trans = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelGreen__YWM4M')
                        self.go_plan['trans_plan'].append(no_trans.text) #直飛
                    #去程轉機次數
                    try:
                        trans_cnt = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelRed__NTY2Y')
                        self.go_plan['trans_cnt'] = re.search(r'\d+', trans_cnt.text).group()
                    except:
                        self.go_plan['trans_cnt'] = 0
                    #去程花費時間
                    go_spend = go_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY Duration_duration__NmUyM').text
                    self.go_plan['spend_time'] = go_spend
                    try:
                        spend_hr = int(''.join(filter(str.isdigit, go_spend.split('小時')[0])))
                        self.go_plan['spend_hr'] = spend_hr
                    except:
                        self.go_plan['spend_hr'] = 0
                    try:
                        spend_min = int(''.join(filter(str.isdigit, go_spend.split('小時')[1])))
                        self.go_plan['spend_min'] = spend_min
                    except:
                        self.go_plan['spend_min'] = 0
                    #去程出發、抵達時間
                    takeoff_time = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--subheading__NzkwO')[0].text
                    takeoff_datetime_tmp = go_plan_date + ' ' + takeoff_time
                    takeoff_datetime = datetime.datetime.strptime(takeoff_datetime_tmp, '%y%m%d %H:%M')
                    land_datetime = takeoff_datetime + timedelta(hours = spend_hr) + timedelta(minutes = spend_min)
                    self.go_plan['takeoff_time'] = takeoff_datetime
                    self.go_plan['land_time'] = land_datetime
                    #去程的出發地&目的地
                    takeoff_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[0]
                    land_location = go_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[1]
                    self.go_plan['takeoff_location'] = takeoff_location.text
                    self.go_plan['land_location'] = land_location.text
                    self.go_plan['check_date'] = self.current_date
                    go_plan_writer.writerow(self.go_plan)
                    print('go_plan:',self.go_plan)
                    self.go_plan['trans_plan'].clear()
                    print('去程資訊處理完成')
                    print('開始處理回程資訊:')
                    self.bk_plan['flight_uuid'] = uuid_pk
                    back_info = k.find_all("div",class_ = 'LegDetails_container__MTkyZ UpperTicketBody_leg__MmNkN')[1] #回程
                    #回程航空公司(如果有2班以上的航空公司,以文字呈現,一間以圖片呈現,抓alt文字)
                    company = back_info.find("div",class_ = 'LogoImage_container__MDU0Z LegLogo_logoContainer__ODdkM UpperTicketBody_legLogo__ZjYwM')
                    try:
                        self.bk_plan['company'] = company.find("div",class_ = 'BpkImage_bpk-image__YTkyO BpkImage_bpk-image--no-background__NGMyN').img['alt']
                    except:
                        self.bk_plan['company'] = company.text
                    #回程轉機地點
                    trans_location = back_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopStation__M2E5N')
                    for location in trans_location:
                        self.bk_plan['trans_plan'].append(location.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY').text)
                    if not self.bk_plan['trans_plan']:
                        no_trans = back_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelGreen__YWM4M')
                        self.bk_plan['trans_plan'].append(no_trans.text) #直飛
                    #回程轉機次數
                    try:
                        trans_cnt = back_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY LegInfo_stopsLabelRed__NTY2Y')
                        self.bk_plan['trans_cnt'] = re.search(r'\d+', trans_cnt.text).group()
                    except:
                        self.bk_plan['trans_cnt'] = 0
                    #回程花費時間
                    go_spend = back_info.find("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY Duration_duration__NmUyM').text
                    self.bk_plan['spend_time'] = go_spend
                    try:
                        spend_hr = int(''.join(filter(str.isdigit, go_spend.split('小時')[0])))
                        self.bk_plan['spend_hr'] = spend_hr
                    except:
                        self.bk_plan['spend_hr'] = 0
                    try:
                        spend_min = int(''.join(filter(str.isdigit, go_spend.split('小時')[1])))
                        self.bk_plan['spend_min'] = spend_min
                    except:
                        self.bk_plan['spend_min'] = 0
                    #去程出發、抵達時間
                    takeoff_time = back_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--subheading__NzkwO')[0].text
                    takeoff_datetime_tmp = bk_plan_date + ' ' + takeoff_time
                    takeoff_datetime = datetime.datetime.strptime(takeoff_datetime_tmp, '%y%m%d %H:%M')
                    land_datetime = takeoff_datetime + timedelta(hours = spend_hr) + timedelta(minutes = spend_min)
                    self.bk_plan['takeoff_time'] = takeoff_datetime
                    self.bk_plan['land_time'] = land_datetime
                    #回程的出發地&目的地
                    takeoff_location = back_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[0]
                    land_location = back_info.find_all("span",class_ = 'BpkText_bpk-text__MWZkY BpkText_bpk-text--body-default__Y2M3Z LegInfo_routePartialCityTooltip__NTE4Z')[1]
                    self.bk_plan['takeoff_location'] = takeoff_location.text
                    self.bk_plan['land_location'] = land_location.text
                    self.bk_plan['check_date'] = self.current_date
                    bk_plan_writer.writerow(self.bk_plan)
                    print('bk_plan:',self.bk_plan)
                    self.bk_plan['trans_plan'].clear()
                    print('回程資訊處理完成')                                                                   
                    cnt += 1
if __name__ == '__main__':
    SkyscannerScraper = SkyscannerScrapper_plan()
    takeoff_location = 'tpet'
    land_location = 'hkd'
    go_plan_date = '231201'
    bk_plan_date = '231231'
    people = '2'
    createtime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    trip_info = SkyscannerScraper.scrape_trip_plan(takeoff_location,land_location,go_plan_date,people,bk_plan_date)
    SkyscannerScraper.trip_plan_memo(trip_info,createtime,bk_plan_date)
    SkyscannerScraper.trip_plan_detail(trip_info,go_plan_date,createtime,bk_plan_date)















            








        
        
        

