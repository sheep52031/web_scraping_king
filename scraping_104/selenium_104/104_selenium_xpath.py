# 104_job_bank with Selenium (Overview)
# import packages
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv , time
import os.path
import pandas as pd
from bs4 import BeautifulSoup



# Get Driver
service = Service("./chromedriver_win32/chromedriver.exe")
chrome_options = Options()
chrome_options.page_load_strategy = 'eager'
driver = Chrome(service=service,options = chrome_options)



url = "https://www.104.com.tw/jobs/search/?ro=0&keyword=python%E5%B7%A5%E7%A8%8B%E5%B8%AB&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area=6001001000%2C6001002004&order=1&asc=0&page=1&mode=s&jobsource=2018indexpoc&langFlag=0&langStatus=0&recommendJob=1&hotJob=1"
driver.get(url)
driver.maximize_window()
time.sleep(1)


all_job_data = [] # 累積6篇釋放內容寫到csv
scroll = 0     # 爬完一篇就滾動一些
    
columns_name = ["update_date", "company", "job_title", "area", "exp", "job_content", "job_requirement", "pay", "job_url",
                "address"]  # 第一欄的名稱



# 網頁的設計方式是滑動到下方時，會自動加載新資料，在這裡透過程式送出Java語法幫我們執行「滑到下方」的動作
for j in range(25): 
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(1)


# 自動加載只會加載15次，超過之後必須要點選「手動載入」的按鈕才會繼續載入新資料（可能是防止爬蟲）
k = 1
while k != 0:
    try:
        # 手動載入新資料之後會出現新的more page，舊的就無法再使用，所以要使用最後一個物件
        driver.find_elements(By.CLASS_NAME, "js-more-page",)[-1].click() 
        # 如果真的找不到，也可以直接找中文!
        # driver.find_element(By.XPATH,"//*[contains(text(),'手動載入')]").click()
        time.sleep(2.5) # 時間設定太短的話，來不及載入新資料就會跳錯誤
        print('Click 手動載入，' + '載入第' + str(15 + k) + '頁') 
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        k = k+1
        time.sleep(1) 
    except:
        k = 0
        print('No more Job')


# 透過BeautifulSoup解析資料
soup = BeautifulSoup(driver.page_source, 'html.parser')
jobs = soup.findAll('a',{'class':'js-job-link'})
print('共有 ' + str(len(jobs)) + ' 筆資料')

count = int(len(jobs))


# 從第一篇開始爬
i = 350

while (i < count):

    try:
    
        # id: js-job-content 出現才開始Xpath定位否則就等最多10秒
        # wait = WebDriverWait(driver, 10)
        # element = wait.until(EC.element_to_be_clickable((By.ID, "js-job-content")))


        # 公司名稱
        cursor = driver.find_element(By.XPATH,f"//*[@id=\"js-job-content\"]/article[{i}]")
        company = cursor.get_attribute("data-cust-name")
        print(company)
    

        # 職位
        cursor = driver.find_element(By.XPATH,f"//*[@id=\"js-job-content\"]/article[{i}]/div[1]/h2/a")
        job_title = cursor.text
        print(job_title)
        
        # 104職缺網址
        job_url = cursor.get_attribute('href')

        # 地區
        cursor = driver.find_element(By.XPATH, f"//*[@id=\"js-job-content\"]/article[{i}]/div[1]/ul[2]/li[1]")
        area = cursor.text

        # 工作內容(尚未抓關鍵字)
        cursor = driver.find_element(By.XPATH, f"//*[@id=\"js-job-content\"]/article[{i}]/div[1]/p")
        content = cursor.text
        job_content = ""
        
        if len(content) > 500:                    # 太多內容就得去內文看(排版乾淨)
            job_content = "詳見網站，內容不全"
            for w, letter in enumerate(content[:500]):
                if (w % 60 == 0 and w != 0):
                    job_content += '\n'
                job_content += letter

        else:
            for w, letter in enumerate(content):  # 每60個字換行(排版)
                if (w % 60 == 0 and i != 0):
                    job_content += '\n'
                job_content += letter



        # get into detail job content
        driver.get(job_url)
        time.sleep(3)



        # 其他條件
        cursor = driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[2]/div/div[1]/div[2]/div[3]/div/div[2]/div/div/p")
        requirement = cursor.text
        job_requirement = ""
        for w, letter in enumerate(requirement):    # 每60個字換行(排版)
                if (w % 60 == 0 and w != 0):
                    job_requirement += '\n'
                job_requirement += letter


        # 工作經歷
        cursor = driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div")
        exp = cursor.text

        # 公司地址
        cursor = driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[2]/div/div[1]/div[1]/div[2]/div[5]/div[2]/div/div")
        address = cursor.text[5:]

    

        # pay
        cursor = driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[2]/div/div[1]/div[1]/div[2]/div[3]/div[2]/div/p")
        pay = cursor.text  

        # 職缺更新時間
        cursor = driver.find_element(By.XPATH, "//*[@id=\"app\"]/div/div[1]/div[2]/div/div/div[1]/h1/span/span")
        update_date = cursor.text
        
        
        # 爬內文緩慢的滑動 
        driver.execute_async_script(
                """
            count = 400;
            let callback = arguments[arguments.length - 1];
            t = setTimeout(function scrolldown(){
                console.log(count, t);
                window.scrollTo(0, count);
                if(count < (document.body.scrollHeight || document.documentElement.scrollHeight)){
                count+= 400;
                t = setTimeout(scrolldown, 1000);
                }else{
                callback((document.body.scrollHeight || document.documentElement.scrollHeight));
                }
            }, 1000);"""
            )
        time.sleep(1)
        
        # 回上一頁
        driver.back()
        time.sleep(3)

        job_data = {"update_date": update_date, "company": company, "job_title": job_title, "area": area, "exp": exp, "job_content": job_content, 
                    "job_requirement": job_requirement, "pay": pay, "job_url": job_url,"address": address}


        all_job_data.append(job_data)


        # # 下滑下一篇
        # driver.execute_script(f"window.scrollTo({scroll}, {scroll+240})")  
        # scroll += 240
        # time.sleep(2)
        
    except Exception as e:                      # Xpath有定位抓不到就捨棄那篇 列出那間公司
        print(company)
        print(e.args)
        print("====這間抓失敗====")
        driver.back()
        time.sleep(3)

    
    if (len(all_job_data) > 5 and i == 6) :             # 前6篇寫入多做檔案存在判斷 避免複寫
        file_exists = os.path.exists('104人力銀行.csv')   

        if file_exists:                                 
            with open('104人力銀行.csv', 'a', newline='', encoding='utf-8-sig') as csvFile:  # 定義CSV的寫入檔,並且每次寫入完會換下一行
                dictWriter = csv.DictWriter(csvFile, fieldnames=columns_name)  
                for each_job in all_job_data:
                    dictWriter.writerow(each_job)

        if not file_exists:    
            with open('104人力銀行.csv', 'w', newline='', encoding='utf-8-sig') as csvFile:  
                dictWriter = csv.DictWriter(csvFile, fieldnames=columns_name)  
                dictWriter.writeheader()                 # 寫入第一列的欄位名稱
                for each_job in all_job_data:
                    dictWriter.writerow(each_job)
        all_job_data = []

    elif (len(all_job_data)> 5 and i != 6):                         
        with open('104人力銀行.csv', 'a', newline='', encoding='utf-8-sig') as csvFile:  
            dictWriter = csv.DictWriter(csvFile, fieldnames=columns_name)  
            for each_job in all_job_data:
                dictWriter.writerow(each_job)
        all_job_data = []
        
        
    # if i == (max-1):                                   # 最後不到6篇也要寫入
    #     with open('104人力銀行.csv', 'a', newline='', encoding='utf-8-sig') as csvFile:  
    #         dictWriter = csv.DictWriter(csvFile, fieldnames=columns_name)  
    #         for each_job in all_job_data:
    #             dictWriter.writerow(each_job)

    # 爬完一篇就+1 爬下一篇
    i += 1 
    print(f"====已爬取{i}篇職缺=====")


print(f"======共爬取{i}篇職缺======")
driver.quit()