import http.client
import requests
import requests.utils
import ssl
import argparse
import json
import sys
import urllib
from typing import Dict, Callable
import os
import threading
import types
import typing
import time
from threading import Thread
from queue import Queue
from urllib import parse
import pickle

'''user defined modules'''
from .util.util import *
from .util.exception import *
from .util.file import mkdir
from .user.user_profile import *

consume_count = 0
crawl_count = 0

def get_session_path(login_user) ->str:
    session_path = "./session/"
    return "{}/session-{}".format(session_path, login_user)

def save_session(user_profile: UserProfile):
    file_name = get_session_path(user_profile._login_user)
    with open(get_session_path(user_profile._login_user), 'wb') as f:
        pickle.dump(requests.utils.dict_from_cookiejar(user_profile._session.cookies), f)

def load_session(user_profile: UserProfile) ->bool:
    file_name = get_session_path(user_profile._login_user)

    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        return False

    with open(file_name, 'rb') as f:
        session = requests.session()
        session.cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        session.headers.update(default_http_header())
        session.headers.update({'X-CSRFToken': session.cookies.get_dict()['csrftoken']})
        user_profile._session = session
    return True

def get_password(username: str) ->str:
    print("username:{}".format(username))
    print("input password:", end='')
    password = input()
    print("passwd:{}".format(password))
    return password

def download_pics(queue:Queue, lock:threading.Lock, stop_event: threading.Event):
    global consume_count
    while True:
        if stop_event.is_set() and queue.empty():
            break
        dict_info = queue.get()
        if dict_info is None:
            print("receive None Obj")
            break
        lock.acquire()
        consume_count += 1
        print("start downloading {}th".format(consume_count))
        lock.release()
        save_pic(dict_info['profile'], dict_info['url'], dict_info['file_name'])
    print("thread exit!")


def copy_session(session: requests.Session) -> requests.Session:
    """Duplicates a requests.Session."""
    new = requests.Session()
    new.cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
    new.headers = session.headers.copy() # type: ignore
    return new

def handle_edge(user_profile: UserProfile, edge:Dict[str, any]):
    ''' declare global variables'''
    global crawl_count

    '''shortcode query pattern'''
    template_params = {
                        "child_comment_count":3,
                        "fetch_comment_count":40,
                        "parent_comment_count":24,
                        "has_threaded_comments":True}

    urls = []
    if edge['__typename'] == 'GraphImage':
        urls.append(edge['display_url'])
        file_type = get_post_format(urls[-1])
        if file_type == '':
            file_type = 'jpg'
        user_profile._producer.produce({
                            'profile':user_profile,
                            'url': urls[-1],
                            'file_name':"{}/{}.{}".format(user_profile._dst_dir, edge['id'], file_type)})
    elif edge['__typename'] == 'GraphVideo':
        if edge['is_video']:
            #print(json.dumps(edge, indent=2))
            if 'video_url' not in edge:
                template_params['shortcode'] = edge['shortcode']
                graphql_query_shortcode_video(user_profile, template_params)
                return
            urls.append(edge['video_url'])
            file_type = get_post_format(urls[-1])
            if file_type == '':
                file_type = 'mp4'

            user_profile._producer.produce({
                                'profile':user_profile,
                                'url':urls[-1],
                                'file_name':"{}/{}.{}".format(user_profile._dst_dir, edge['id'], file_type)})

        else:
            print("node is not video!")
    elif edge['__typename'] == 'GraphSidecar':
        #print(json.dumps(edge, indent=2))
        if 'edge_sidecar_to_children' not in edge:
            template_params['shortcode'] = edge['shortcode']
            graphql_query_shortcode_sidecar(user_profile, template_params)
            return
        for edge in edge['edge_sidecar_to_children']['edges']:
            if edge['node']['__typename'] == 'GraphImage':
                urls.append(edge['node']['display_url'])
                user_profile._producer.produce({
                                    'profile':user_profile,
                                    'url': urls[-1],
                                    'file_name':"{}/{}.jpg".format(user_profile._dst_dir, edge['node']['id'])})
            elif edge['node']['__typename'] == 'GraphVideo':
                #TODO:handle if video_url not exist in edge['node']
                if 'video_url' in edge['node']:
                    urls.append(edge['node']['video_url'])
                    user_profile._producer.produce({
                                    'profile':user_profile,
                                    'url':urls[-1],
                                    'file_name':"{}/{}.mp4".format(user_profile._dst_dir, edge['node']['id'])})
                elif 'display_url' in edge['node']:
                    urls.append(edge['node']['display_url'])
                    user_profile._producer.produce({
                                    'profile':user_profile,
                                    'url':urls[-1],
                                    'file_name':"{}/{}.jpg".format(user_profile._dst_dir, edge['node']['id'])})

    print("download [{}/{}] {}".format(crawl_count, user_profile._post_count, ' '.join(urls)))

def graphql_query_shortcode_sidecar(user_profile: UserProfile, variables: Dict[str, any]):
    edges = graphql_query_shortcode(user_profile, variables,
                                    lambda b:b['data']['shortcode_media']['edge_sidecar_to_children']['edges'])
    for edge in edges:
        print(json.dumps(edge, indent=2))
        handle_edge(user_profile, edge['node'])

def graphql_query_shortcode_video(user_profile: UserProfile, variables: Dict[str, any]):
    video  = graphql_query_shortcode(user_profile, variables, lambda b:b['data']['shortcode_media'])
    print(json.dumps(video, indent=2))
    handle_edge(user_profile, video)

def graphql_query_shortcode(user_profile: UserProfile,
                            variables: Dict[str, any],
                            extractor: Callable[[Dict[str,any]], Dict[str,any]]) ->Dict[str, any]:
    grapql_query_template = "https://www.instagram.com/graphql/query/?{}"
    with copy_session(user_profile._session) as tmpsession:
        tmpsession.headers.update(default_http_header(empty_session_only=True))
        tmpsession.headers['authority'] = 'www.instagram.com'
        tmpsession.headers['scheme'] = 'https'
        tmpsession.headers['accept'] = '*/*'
        tmpsession.headers['referer'] = "https://www.instagram.com/{}/".format(user_profile._user_name)
        tmpsession.headers['X-CSRFToken'] = user_profile._session.cookies.get_dict()["csrftoken"]

        if 'shortcode' not in variables:
            raise ParamInvalidException("shortcode not in parmas")

        query_params = {'query_hash': '109cdd03d7468e12222ad164fbea3ca3', 'variables': variables}
        print(grapql_query_template.format(parse_dict_2_query_params(query_params)))

        with tmpsession.get(grapql_query_template.format(parse_dict_2_query_params(query_params))) as resp:
            if resp.status_code != 200:
                raise BadStatusCodeException("bad status_code:{}".format(resp.status_code))
            resp_json = resp.json()
            if resp_json['status'] != 'ok':
                raise BadStatusException("status:{}".format(resp_json['status']))
            return extractor(resp_json)

def get_profile(user_profile:UserProfile):
    '''declare global variables'''
    global crawl_count

    profile_url = "https://www.instagram.com/{}/?__a=1".format(user_profile._user_name)
    print(profile_url)
    with copy_session(user_profile._session) as tmpsession:
        resp = user_profile._session.get(profile_url)
        if resp.status_code == 404:
            print("user {} not exist".format(user_profile._user_name))
            raise UserNotExistException(resp.status_code)
            sys.exit(404)
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
            crawl_count += 1
            handle_edge(user_profile, edge['node'])

def login(user_profile: UserProfile):
    HOST = "https://www.instagram.com/"
    session = requests.Session()
    session.cookies.update({'sessionid':'', 'mid':'', 'ig_pr':'1',
                            'ig_vw':'1920', 'ig_cb':'1', 'csrftoken':'',
                            's_network':'', 'ds_user_id':''})
    session.headers.update(default_http_header(True))
    rsp = session.get('https://www.instagram.com/web/__mid/')
    session.headers.update({'X-CSRFToken':session.cookies.get_dict()["csrftoken"]})
    print("csrftoken={}".format(session.cookies.get_dict()["csrftoken"]))

    user = user_profile._login_user
    password = get_password(user)
    login = session.post('https://www.instagram.com/accounts/login/ajax/',
                             data={'password': password, 'username': user}, allow_redirects=True)

    if login.status_code != 200:
        print(login.reason)
        raise  BadStatusCodeException(login.status_code)

    try:
        resp_json = login.json()
    except json.decoder.JSONDecodeError:
        print("decode response error!")
        sys.exit(10)

    print(json.dumps(resp_json, indent=2))

    if resp_json["status"] != 'ok':
        raise BadStatusException(resp_json["status"])

    if not resp_json['authenticated']:
        raise LoginFailedException(resp_json['authenticated'])

    user_profile.set_session(session)

def graphql_query_post(user_profile:UserProfile):
    global global_count
    global crawl_count

    #judge if user has any post
    if user_profile._post_count == 0:
        print("{} has not post anything yet!".format(user_profile._user_name))
        return
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

        has_next = True
        while has_next:
            json_variable = {"id":user_profile._user_id, "after":user_profile._end_cursor, 'first':50}
            query_data = {"query_hash":"e769aa130647d2354c40ea6a439bfc08", "variables":json_variable}
            str_html = "https://www.instagram.com/graphql/query/?{}".format(parse_dict_2_query_params(query_data))
            try:
                resp = tmpsession.get(str_html)
            #except ConnectionResetError:
            except:
                time.sleep(10)
                continue

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
            edges = resp_json['data']['user']['edge_owner_to_timeline_media']['edges']
            print("count:{0}, hash_next:{1}, end_cursor:{2}, edge count:{3}".format(post_count, has_next, end_cursor, len(edges)))

            '''handle edge '''
            for edge in edges:
                #print(json.dumps(edge, indent=2))
                crawl_count +=1
                handle_edge(user_profile, edge['node'])

            '''too much request will case 429'''
            time.sleep(2)

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

def main():
    '''get pararmeters from user'''
    parser = argparse.ArgumentParser(description='download user\'s posts from instagram',
                                    epilog='the abave specifices how to use this tool')
    parser.add_argument('--user', help="specifice the user you want to download posts", type=str, required=True, metavar="ghostwyd")
    parser.add_argument('--download-dir', help="the dir where you want to save the posts", type=str, required=False, metavar="./", default='./')
    parser.add_argument('--thread-num', help="download thread num", type=int, required=False, metavar="./", default=5)
    parser.add_argument('--login-user', help="specifice which accounter you want to log in", type=str, required=True, metavar="ghostwyd")
    #parser.print_help()

    args = parser.parse_args()
    dict_args = vars(args)

    user_name = dict_args["user"]
    thread_num = dict_args['thread_num']
    login_user = dict_args['login_user']
    download_dir = dict_args['download_dir']

    '''create UserProfile'''
    lock = threading.Lock()
    queue = Queue()
    producer = Producer(queue, lock)
    user_profile = UserProfile(login_user, user_name, producer)
    user_profile.set_dst_dir(get_dst_dir(dict_args["download_dir"], user_name))
    mkdir(user_profile._dst_dir)

    '''start dowonlad thread'''
    threads = []
    stop_event = threading.Event()
    for i in range(thread_num):
        threads.append(Thread(target=download_pics, args=(queue, lock, stop_event)))
    for i in range(thread_num):
        threads[i].start()

    '''action'''
    if not load_session(user_profile):
        login(user_profile)
    save_session(user_profile)
    print("begin get_profile")
    get_profile(user_profile)
    print("begin graphql_query_post")
    graphql_query_post(user_profile)

    '''stop  threads'''
    stop_event.set()
    for i in range(thread_num):
        threads[i].join()
    print("finish all threads")

if __name__ == "__main__":
    main()
