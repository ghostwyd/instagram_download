import http.client
import requests
import requests.utils
import ssl
import argparse
import json
import sys
import urllib
from typing import Dict
import os
from user.user_profile import UserProfile
import threading
import types
import typing
import time
from threading import Thread
from queue import Queue
from urllib import parse

from util.util import print_dict
from util.exception import BadStatusCodeException, BadStatusException
from util.file import mkdir

read_begin_flag = False
global_count = 2^16
consume_count = 0
crwal_count = 0

def download_pics(queue:Queue, lock:threading.Lock):
    global consume_count
    global global_count
    global thread_running
    while True:
        lock.acquire()
        if queue.empty() and not thread_running:
            lock.release()
            break
        else:
            dict_info = queue.get()
            save_pic(dict_info['profile'], dict_info['url'], dict_info['file_name'])
            consume_count += 1
            lock.release()

class Producer:
    def __init__(self, queue: Queue, lock:threading.Lock, handler:types.FunctionType=None):
        self._queue = queue
        self._lock = lock

    def produce(self, dict_info:Dict[str, any]):
        while True:
            #acquire = self._lock.acquire(timeout=1)
            #if not acquire:
            #    continue
            print("enter queue")
            self._queue.put(dict_info)
            #self._lock.release()
            break

def default_http_header(empty_session_only:bool = False) -> Dict[str, str]:
    header = {'Accept-Encoding': 'gzip, deflate',
                  'Accept-Language': 'en-US,en;q=0.8',
                  'Connection': 'keep-alive',
                  'Content-Length': '0',
                  'Host': 'www.instagram.com',
                  'Origin': 'https://www.instagram.com',
                  'Referer': 'https://www.instagram.com/',
                  'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Safari/605.1.15',
                  'X-Instagram-AJAX': '1',
                  'X-Requested-With': 'XMLHttpRequest'}
    if empty_session_only:
        del header['Host']
        del header['Origin']
        del header['Referer']
        del header['X-Instagram-AJAX']
        del header['X-Requested-With']
    return header

def copy_session(session: requests.Session) -> requests.Session:
    """Duplicates a requests.Session."""
    new = requests.Session()
    new.cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
    new.headers = session.headers.copy() # type: ignore
    return new

def handle_edge(user_profile: UserProfile, edge:Dict[str, any]):
    global crwal_count
    url = []
    if edge['node']['__typename'] == 'GraphImage':
        url = url.append(edge_node['node']['display_url'])
        producer.produce({
                            'profile':user_profile,
                            'url': urls[-1],
                            'file_name':"{}/{}.jpg".format(user_profile._dst_dir, edge['node']['id'])})
    elif edge['node']['__typename'] == 'GraphVideo':
        if edge['node']['is_video']:
            urls = urls.append(edge['node']['video_url'])
            producer.produce({
                                'profile':user_profile,
                                'url':urls[-1],
                                'file_name':"{}/{}.mp4".format(user_profile._dst_dir, edge['node']['id'])})

        else:
            print("node is not video!")
    elif edge['node']['__typename'] == 'GraphSidecar':
        for edge in edge['node']['edge_sidecar_to_children']['edges']:
            if edge['node']['__typename'] == 'GraphImage':
                urls = urls.append(edge['node']['display_url'])
                producer.produce({
                                    'profile':user_profile,
                                    'url': urls[-1],
                                    'file_name':"{}/{}.jpg".format(user_profile._dst_dir, edge['node']['id'])})
            elif edge['node']['__typename'] == 'GraphVideo':
                urls = urls.append(edge['node']['video_url'])
                producer.produce({
                                    'profile':user_profile,
                                    'url':urls[-1],
                                    'file_name':"{}/{}.mp4".format(user_profile._dst_dir, edge['node']['id'])})

    print("download [{}/{}] {}".format(crawl_count, user_profile._post_count, ' '.join(url)))

def get_profile(user_profile:UserProfile):
    global thread_running
    profile_url = "https://www.instagram.com/{}/?__a=1".format(user_profile._user_name)
    with copy_session(user_profile._session) as tmpsession:
        resp = user_profile._session.get(profile_url)
        if resp.status_code != 200:
            print("unexpected status_code:{}".format(resp.status_code))
            raise BadStatusCodeException(resp.status_code)
        resp_json = resp.json()
        user_info = resp_json["graphql"]["user"]
        print("user_id:{}, follow_count:{}, follower_count:{}".format(user_info["id"], user_info["edge_follow"]["count"], user_info["edge_followed_by"]))

        post_count = user_info["edge_owner_to_timeline_media"]["count"]
        page_info = user_info["edge_owner_to_timeline_media"]["page_info"]
        has_next = page_info["has_next_page"]
        end_cursor = page_info["end_cursor"]
        print("count:{}, has_next:{}, end_cursor:{}".format(post_count, has_next, end_cursor))

        #update user_profile info
        user_profile.set_user_id(user_info["id"])
        user_profile.set_follow_count(user_info["edge_follow"]["count"])
        user_profile.set_followed_by_count(user_info["edge_followed_by"])
        user_profile.set_post_count(post_count)
        user_profile.set_end_cursor(end_cursor)

        for edge in user_info['edge_owner_to_timeline_media']['edges']:
            crwal_count += 1
            handle_edge(user_profile, edge)
        if not has_next:
            thread_running = False

def login() ->requests.Session:
    HOST = "https://www.instagram.com/"
    session = requests.Session()
    session.cookies.update({'sessionid':'', 'mid':'', 'ig_pr':'1',
                            'ig_vw':'1920', 'ig_cb':'1', 'csrftoken':'',
                            's_network':'', 'ds_user_id':''})
    session.headers.update(default_http_header(True))
    rsp = session.get('https://www.instagram.com/web/__mid/')
    session.headers.update({'X-CSRFToken':session.cookies.get_dict()["csrftoken"]})
    print("csrftoken={}".format(session.cookies.get_dict()["csrftoken"]))

    user = "yongdong.wu"
    passwd = "wudong41*"
    login = session.post('https://www.instagram.com/accounts/login/ajax/',
                             data={'password': passwd, 'username': user}, allow_redirects=True)

    if login.status_code != 200:
        print(login.reason)
        raise  BadStatusCodeException(login.status_code)

    try:
        resp_json = login.json()
    except json.decoder.JSONDecodeError:
        print("decode response error!")
        sys.exit(10)

    if resp_json["status"] != 'ok':
        raise BadStatusException(resp_json["status"])

    return session

def graphql_query_post(user_profile:UserProfile):
    global thread_running

    #judge if user has any post
    if user_profile._post_count == 0:
        print("{} has not post anything yet!".format(user_profile._user_name))
        return
    global global_count
    global_count = user_profile._post_count

    with copy_session(user_profile._session) as tmpsession:
        tmpsession.headers.update(default_http_header(empty_session_only=True))
        del tmpsession.headers['Connection']
        del tmpsession.headers['Content-Length']
        tmpsession.headers['authority'] = 'www.instagram.com'
        tmpsession.headers['scheme'] = 'https'
        tmpsession.headers['accept'] = '*/*'
        tmpsession.headers['referer'] = "https://www.instagram.com/{}/".format(user_profile._user_name)
        tmpsession.headers['X-CSRFToken'] = user_profile._session.cookies.get_dict()["csrftoken"]

        print_dict(tmpsession.cookies.get_dict())
        print_dict(tmpsession.headers)


        for i in range(5):
            threads.append(Thread(target=download_pics, args=(queue, lock)))
        for i in range(5):
            threads[i].start()

        has_next = True
        while has_next:
            json_variable = {"id":user_profile._user_id, "after":user_profile._end_cursor, 'first':50}
            query_data = {"query_hash":"e769aa130647d2354c40ea6a439bfc08", "variables":json.dumps(json_variable, separators=(',', ':'))}
            str_params = ""
            first = True
            for key in query_data:
                if first:
                    first = False
                    str_params = "{}={}".format(key, query_data[key])
                else:
                    str_params = "{}&{}={}".format(str_params, key, query_data[key])

            str_html = "https://www.instagram.com/graphql/query/?{}".format(str_params)
            print(str_html)
            print(json.dumps(query_data,indent=2))
            resp = tmpsession.get(str_html)

            if resp.status_code != 200:
                raise BadStatusCodeException(resp.status_code)

            resp_json = resp.json()
            if resp_json["status"] != "ok":
                raise BadStatusException("unexpected status:{} in resp_json".format(resp_json["status"]))
            else:
                print("status ok!")

            resp_edges = lambda b:b["data"]["user"]["edge_owner_to_timeline_media"]["edges"](resp_json)
            page_info = resp_json["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]
            has_next = page_info["has_next_page"]
            end_cursor = page_info["end_cursor"]
            post_count = resp_json["data"]["user"]["edge_owner_to_timeline_media"]["count"]
            user_profile._end_cursor = end_cursor
            print("count:{0}, hash_next:{1}, end_cursor:{2}, edge count:{3}".format(post_count, has_next, end_cursor, len(resp_json['data']['user']['edge_owner_to_timeline_media']['edges'])))
            display_urls = [edge['node']['display_url'] for edge in resp_json["data"]['user']['edge_owner_to_timeline_media']['edges']]

            '''handle edge '''
            for edge in resp_json["data"]["user"]["edge_owner_to_timeline_media"]["edges"]:
                crawl_count +=1

            if not has_next:
                thread_running = False


def save_pic(user_profile: UserProfile, url: str, file_name: str) ->bool:
    if os.path.exists(file_name):
        print("{} already exist!".format(file_name))
        return False

    #default header
    header = {
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://www.instagram.com/{}/".format(user_profile._user_name),
        #"Sec-Fetch-Mode": "no-cors",
        #"Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36"}
    with requests.get(url,headers=header) as resp:
        if resp.status_code != 200:
            print("unuexpected status_code:{} in save_pic".format(resp.status_code))
            return True
        with open(file_name, 'wb') as file:
            content = resp._content
            file.write(content)

def get_chain(user_profile: UserProfile):
    variables = {
                    "user_id":user_profile._user_id,
                    "include_chaining":True,
                    "include_reel":True,
                    "include_suggested_users":False,
                    "include_logged_out_extras":False,
                    "include_highlight_reels":False,
                    "include_related_profiles":False}
    query_data = {"query_hash":"c9100bf9110dd6361671f113dd02e7d6", "variables":json.dumps(variables,separators=(',', ': '))}
    resp = user_profile._session.get("https://www.instagram.com/graphql/query/", params=query_data)
    print(json.dumps(resp.json(), indent=2))


def get_dst_dir(base_dir: str, user_name: str) ->str:
    if base_dir.endswith("/"):
        base_dir = base_dir.rstrip("/")
    return "{}/{}".format(base_dir, user_name)

if __name__ == "__main__":
    '''get pararmeters from user'''
    parser = argparse.ArgumentParser(description='download user\'s posts from instagram',
                                    epilog='the abave specifices how to use this tool')
    parser.add_argument('--user', help="specifice the user you want to download posts", type=str, required=True, metavar="ghostwyd")
    parser.add_argument('--download-dir', help="the dir where you want to save the posts", type=str, required=False, metavar="./", default='./')
    parser.add_argument('--thread-num', help="download thread num", type=int, required=False, metavar="./", default=5)
    #parser.print_help()
    args = parser.parse_args()
    dict_args = vars(args)

    user_name = dict_args["user"]
    user_profile = UserProfile(user_name)
    user_profile.set_dst_dir(get_dst_dir(dict_args["download_dir"], user_name))
    thread_num = dict_args['thread_num']
    mkdir(user_profile._dst_dir)

    '''concurrent parmas'''
    threads = []
    queue = Queue()
    lock = threading.Lock()
    producer = Producer(queue, lock)

    '''action'''
    user_profile.set_session(login())
    print("begin get_profile")
    get_profile(user_profile)
    print("begin graphql_query_post")
    graphql_query_post(user_profile)

    '''stop  threads'''
    time.sleep(20)
    for i in range(5):
        threads[i].join
    print("finish all threads")
