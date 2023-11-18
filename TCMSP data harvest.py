from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
from bs4 import BeautifulSoup
from lxml import etree
import os
import pandas as pd

os.chdir(r'C:\Users\peter\Desktop\TCMSP')
#创建文件夹
if not os.path.exists('.\成分靶点数据'):
    os.mkdir('.\成分靶点数据')

#导入数据
herb = pd.read_excel('./herb_name.xlsx',header=None)

#获取TCMSP中数据函数
def TCMSP(herb_name):
    #请求TCMSP
    fp = Options()
    fp.add_argument('-headless')

    webdriver.ChromeService('./chromedriver.exe')
    driver = webdriver.Chrome()

    #获取token
    driver.get('https://www.tcmsp-e.com/tcmspsearch.php')
    token = driver.find_element(By.XPATH,'//form[@id="SearchForm"]//input[@name="token"]').get_attribute("value")


    #获取网页数据
    try:
        driver.get(f'https://old.tcmsp-e.com/tcmspsearch.php?qs=herb_all_name&q={herb_name}&token={token}')
        link = driver.find_element(By.XPATH,'//div[@class="k-grid-content"]//td[3]/a')  #跳转到数据页面
        link.click()
    except:
        print('抱歉，没有该药物！')
        return 0
    
    
    ingredients = []  # 成分列表
    targets = []   #靶点列表

    #表头
    page_content = etree.HTML(driver.page_source)
    col = page_content.xpath('//th[@role="columnheader"]/a[2]/text()')
    col_ingredient = col[0:12] + ['Save']
    col_target = col[13:17] + ['status']


    #获取页码
    ingredients_page = int(driver.find_element(By.XPATH,'//div[@id="grid"]//div[@data-role="pager"]//a[@title="Go to the last page"]').get_attribute("data-page"))
    targets_page = int(driver.find_element(By.XPATH,'//div[@id="grid2"]//div[@data-role="pager"]//a[@title="Go to the last page"]').get_attribute("data-page"))

    
    #获取有效成分页面
    for _ in range(ingredients_page):  
        soup = BeautifulSoup(driver.page_source, 'lxml')  # 把整个页面变成lxml的格式
        content = soup.find('div', class_='k-grid-content')  # 找到内容表单
        tbody = content.find('tbody')
        trs = tbody.find_all('tr')  # 找到所有tr
        for tr in trs:
            td_text_list = []
            for td in tr.find_all('td'):  # 找到所有td
                td_text = td.text
                td_text_list.append(td_text)
            ingredients.append(td_text_list)
        btn_ing = driver.find_element(By.XPATH, '//div[@id="grid"]//div[@data-role="pager"]//a[@title="Go to the next page"]')  # 翻页
        btn_ing.click()
        time.sleep(random.uniform(2,3))  # 随机等待2-5秒


    #跳转到靶点界面
    swift = driver.find_element(By.XPATH, '//ul/li[@aria-controls="tabstrip-2"]/a')  # 翻页
    swift.click()
    time.sleep(random.uniform(2,3))


    #获取靶点
    for _ in range(targets_page-1): 
        soup1 = BeautifulSoup(driver.page_source, 'lxml')  # 把整个页面变成lxml的格式
        content1 = soup1.find('div', id='grid2')  # 找到内容表单
        tbody1 = content1.find('tbody')
        trs1 = tbody1.find_all('tr')  # 找到所有tr
        for tr in trs1:
            td_text_list = []
            for td in tr.find_all('td'):  # 找到所有td
                td_text = td.text
                td_text_list.append(td_text)
            targets.append(td_text_list)
        btn_ing1 = driver.find_element(By.XPATH, '//div[@id="grid2"]//div[@data-role="pager"]//a[@title="Go to the next page"]')  # 翻页
        btn_ing1.click()
        time.sleep(random.uniform(2,3))  # 随机等待2-5秒
    driver.quit()

    #储存ingredients与targets
    ingredients = pd.DataFrame(
        ingredients,
        columns=col_ingredient
    )
    ingredients.to_excel(f'./成分靶点数据/{herb_name}ingredients.xlsx')

    targets = pd.DataFrame(
        targets,
        columns=col_target
    )
    targets.to_excel(f'./成分靶点数据/{herb_name}targets.xlsx')



#获取每一个药物的有效成分&靶点
for i in herb[0]:
    TCMSP(i)
