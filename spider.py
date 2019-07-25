import requests
import re, json
from requests.exceptions import HTTPError, RequestException, ProxyError, ConnectTimeout
from concurrent.futures import ThreadPoolExecutor
import csv, pymongo, threading
from config import *

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

class JDSpider(object):
    def __init__(self, start_url):
        self.start_url = start_url

        self.csv_file = open('jd.csv', 'a+')
        fileNames = ['nickName', 'userLevelName', 'content', 'publishTime']
        self.writer = csv.DictWriter(self.csv_file, fieldnames=fileNames)
        self.writer.writeheader()

        self.myLock = threading.Lock()
        self.start_request(self.start_url)

    def start_request(self, start_url):
        product_id = re.search('\d+', start_url).group()
        firstComUrl = "https://sclub.jd.com/comment/productPageComments.action?callback=&productId=%s&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1" % product_id
        response_text = self.send_request(firstComUrl)
        if response_text:
            #print('获取到了数据', response_text)
            json_data = json.loads(response_text)
            maxPage = int(json_data['maxPage'])
            print('能获取到的最大页码数量', maxPage)
            pool = ThreadPoolExecutor(10)
            for page in range(20):
                comUrl = "https://sclub.jd.com/comment/productPageComments.action?callback=&productId=%s&score=0&sortType=5&page=%s&pageSize=10&isShadowSku=0&fold=1" % (product_id, str(page))
                result = pool.submit(self.send_request, comUrl)
                result.add_done_callback(self.parse_comments)
            pool.shutdown()
        else:
            print("没有数据")

    def send_request(self, url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36', 'Referer': 'https://item.jd.com/5089253.html'}):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print('请求成功', response.status_code)
                return response.text
        except (HTTPError, TimeoutError, RequestException, ProxyError, ConnectTimeout) as err:
            print(err)
            return None

    def parse_comments(self, future):
        print('开始解析')
        response_text = future.result()
        if response_text:
            comments = json.loads(response_text)['comments']

            for comment in comments:
                commentInfo = {
                    'nickName': comment['nickname'],
                    'content': comment['content'],
                    'publishTime': comment['creationTime'],
                    'userLevelName': comment['userLevelName']
                }
                print(commentInfo)
                #self.save_to_mongo(commentInfo)

                self.save_db_to_csv(commentInfo)

    def save_db_to_csv(self, commentInfo):
        self.myLock.acquire()
        self.writer.writerow(commentInfo)
        self.myLock.release()

    def save_to_mongo(self, result):
        #print(self.myLock)
        self.myLock.acquire()
        try:
            if db[MONGO_TABLE].insert(result):
                print('存储到MONGODB成功', result)
        except Exception as e:
            print(e)
            print('存储到MONGODB失败', result)
        self.myLock.release()

if __name__ == "__main__":
    start_url = 'https://item.jd.com/5089253.html'
    jdSpider = JDSpider(start_url)