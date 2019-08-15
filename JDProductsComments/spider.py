from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from pyquery import PyQuery as pq
from selenium.webdriver.support import expected_conditions as EC
from config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)
wait = WebDriverWait(browser, 10)
browser.set_window_size(1400, 900)
maxCount = 3

def search(count=1):
    if count > maxCount:
        print('等会儿再爬吧')
        return None
    try:
        print('正在搜索')
        browser.get('https://item.jd.com/100002795959.html#none')
        #button = browser.find_element_by_xpath('//*[@id="detail"]/div[1]/ul/li[5]')
        # button = wait.until(
        #      EC.element_to_be_clickable((By.CSS_SELECTOR, '#detail > div.tab-main.large.pro-detail-hd-fixed > ul > li.current'))
        # )
        button = wait.until(
             EC.element_to_be_clickable((By.XPATH, '//*[@id="detail"]/div[1]/ul/li[5]'))
        )
        button.click()
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > strong')
            )
        )
        print('评论加载完成')
        get_comments()
    except TimeoutException:
        count += 1
        search(count)

def next_page():
    print('正在翻页')
    try:
        button_tool_bar = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#J-global-toolbar > div > div.jdm-toolbar.J-toolbar > div.jdm-toolbar-footer > div.J-trigger.jdm-toolbar-tab.jdm-tbar-tab-qrcode > a > i'))
        )
        button_tool_bar.click()
        tool_bar = browser.find_element_by_id('toolbar-qrcode')
        if tool_bar.is_displayed():
             print('tool-bar展开了')
        try:
            button_close = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#toolbar-qrcode > span'))
            )
            button_close.click()
        except TimeoutException:
            print('Already Fuck Off')
        button_next_page = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#comment-0 > div.com-table-footer > div > div > a:nth-child(2)'))
        )
        button_next_page.click()

        # wait.until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, '#comment > div.mc > div.comment-info.J-comment-info > div.comment-percent > strong')
        #     )
        # )
        print('完成翻页')
        get_comments()
    except TimeoutException:
        #print('翻页失败')
        next_page()

def get_comments():
    print('正在获取评论')
    html = browser.page_source
    doc = pq(html)
    items = doc('.comment-item').items()
    for item in items:
        comment = {
            'user': item.find('.user-column').text(),
            'com': item.find('.comment-con').text()
        }
        print(comment)
        save_to_mongodb(comment)
    '''
    try:
        with open('comment.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            #writer.writerow(['user_name', 'comment'])  # 写第一行

            user = browser.find_elements_by_xpath("//div[@class='user-info']")
            lis = browser.find_elements_by_xpath("//p[@class='comment-con']")
            for i in range(len(user)):
                writer.writerow([user[i].text, lis[i].text])
                print('存储成功')
    except Exception as e:
        print(e)
        print('存储失败')
    '''


def save_to_mongodb(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MONGODB成功', result)
    except Exception:
        print('存储到MONGODB失败', result)

def main():
    search()
    next_page()

if __name__ == '__main__':
    main()


'''
try:


    with open('comment.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['user_name', 'comment']) # 写第一行
        for i in range(99):
            num = i + 1
            user = browser.find_elements_by_xpath("//div[@class='user-info']")
            lis = browser.find_elements_by_xpath("//p[@class='comment-con']")
            for i in range(len(user)):
                writer.writerow([user[i].text, lis[i].text])
            button_next_page = browser.find_element_by_class_name('ui-pager-next')
            print(button_next_page.text)
            sleep(1)
            print("第%d页" %num)
            button_next_page.click()
            sleep(5)
finally:
    browser.close()
'''