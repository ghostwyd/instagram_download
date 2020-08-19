import requests
import requests.utils
import sys
import os
import time
from html.parser import HTMLParser
from bs4 import BeautifulSoup
from queue import Queue
import threading
import socket
import queue

concurr_queue = Queue(4096)

class UriInfo():
    def __init__(self, url, download_dir):
        self._url = url
        self._download_dir = download_dir
    def get_url(self):
        return self._url
    def get_download_dir(self):
        return self._download_dir

def mkdir_p(dir_path):
    print("dir:{}", dir_path)
    if os.path.exists(dir_path):
        return
    os.mkdir(dir_path, 0o744)

def get_request_with_retry(url):
    cnt = 0
    while cnt < 3:
        rsp = requests.get(url)
        try:
            rsp = requests.get(url)
            return rsp, None
        except:
            print("here")
            cnt += 1
            time.sleep(1)
    return None, "get request fail!"

def download_and_save_item(url, download_dir):
    rsp, errmsg = get_request_with_retry(url)
    if errmsg != None or rsp.status_code != 200:
        print("get %s fail!"%(url))
        return
    #get item's name
    index = url.rfind("/")
    file_name = url
    if index != -1:
        file_name  = url[index+1:]
    print(file_name)
    save_path = "%s/%s"%(download_dir, file_name)
    f = open(save_path, "wb+")
    f.write(rsp._content)
    f.close()
    rsp.close()

def get_interest_detail(str_page_id, download_dir):
    url= "http://www.dgtle.com/inst-%s-1.html"%(str_page_id)
    rsp, errmsg = get_request_with_retry(url)
    if errmsg != None or rsp.status_code != 200:
        print("get %s fail!"%(url))
        sys.exit(2)
    soup = BeautifulSoup(rsp.text, "lxml")

    img_list = soup.find_all('div', class_="bg-img")
    print(soup.title)
    mkdir_p(download_dir)

    for info in img_list:
        print(info.img['src'])
        #download_and_save_item(info.img['src'], download_dir)
        concurr_queue.put(UriInfo(info.img['src'], download_dir))
    rsp.close()

def get_user_interest_list(user_id):
    index = 1
    while True:
        url = "http://www.dgtle.com/inst/getInstList?page=%d&uid=%s"%(index, user_id)
        print(url)
        rsp, errmsg = get_request_with_retry(url)
        if errmsg != None or rsp.status_code != 200:
            print("getInstList fail!")
            sys.exit(1)
        json_data = rsp.json()
        if json_data["status"] != 'success':
            print("getInstList fail!")
            sys.exit(1)
        # handle url
        for data in json_data['data']['dataList']:
            print(data['id'])
            get_interest_detail(data['id'], "./"+data['user_name'])

        #close response
        rsp.close()

        # check if we have get all the posts
        if json_data['data']['is_last_page']:
            break
        index += 1
    concurr_queue.join()

def download_worker(concurr_queue):
    print(threading.current_thread().getName())
    while True:
        try:
            url_info = concurr_queue.get(True, 50)
            print("url:{}, download_dir:{}", url_info.get_url(), url_info.get_download_dir())
            download_and_save_item(url_info.get_url(), url_info.get_download_dir())
            concurr_queue.task_done()
        except queue.Empty:
            print("receive no data!")
            return

if __name__ == "__main__":
    print(socket.gethostbyname('www.baidu.com'))

    user_id = "4ydqrw74"
    worker_cnt = 40

    thread_list = []
    for i in range(worker_cnt):
        thread_list.append(threading.Thread(None, download_worker, None, (concurr_queue,), None))

    for thread in thread_list:
        thread.start()

    get_user_interest_list(user_id)

    for thread in thread_list:
        thread.join()
