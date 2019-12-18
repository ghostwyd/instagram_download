import http.client
import requests
import requests.utils
import ssl
import json
import sys
import urllib
from typing import Dict
import os

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

def print_dict(dict_cookie:Dict[str, str]):
    '''
        print key/value in dict
    '''
    for key in dict_cookie:
        print("{0}:{1}".format(key, dict_cookie[key]))
    print("-------------------------")

def get_profile(user_name:str, session:requests.Session):
    profile_url = "https://www.instagram.com/{}/?__a=1".format(user_name)
    with copy_session(session) as tmpsession:
        resp = tmpsession.get(profile_url)
        if resp.status_code != 200:
            print("unexpected status_code:{}".format(resp.status_code))
            sys.exit(100)
        resp_json = resp.json()
        #print(json.dumps(resp_json, indent=2))
        user_info = resp_json["graphql"]["user"]
        print("user_id:{}, follow_count:{}, follower_count:{}".format(user_info["id"], user_info["edge_follow"]["count"], user_info["edge_followed_by"]))
        pic_count = user_info["edge_owner_to_timeline_media"]["count"]
        page_info = user_info["edge_owner_to_timeline_media"]["page_info"]
        has_next = page_info["has_next_page"]
        end_cursor = page_info["end_cursor"]
        print("count:{}, has_next:{}, end_cursor:{}".format(pic_count, has_next, end_cursor))

def login() ->requests.Session:
    HOST = "https://www.instagram.com/"
    session = requests.Session()
    session.cookies.update({'sessionid':'', 'mid':'', 'ig_pr':'1',
                            'ig_vw':'1920', 'ig_cb':'1', 'csrftoken':'',
                            's_network':'', 'ds_user_id':''})
    session.headers.update(default_http_header(True))
    #print_dict(session.cookies.get_dict())
    rsp = session.get('https://www.instagram.com/web/__mid/')
    session.headers.update({'X-CSRFToken':session.cookies.get_dict()["csrftoken"]})

    user = "ghostwyd"
    passwd = "Wudong41+"
    login = session.post('https://www.instagram.com/accounts/login/ajax/',
                             data={'password': passwd, 'username': user}, allow_redirects=True)
    if login.status_code != 200:
        print("unexpected status_code:%d"%login.status_code)
        sys.exit(9)

    try:
        resp_json = login.json()
    except json.decoder.JSONDecodeError:
        print("decode response error!")
        sys.exit(10)

    if resp_json["status"] != 'ok':
        print("unexpected status:%s"%(resp_json["status"]))
        sys.exit(11)

    return session

def get_user_id() -> str:
    return ""

def crawl_urls(session :requests.Session, str_userId :str):
    with copy_session(session) as tmpsession:
        tmpsession.headers.update(default_http_header(empty_session_only=True))
        print_dict(tmpsession.cookies.get_dict())
        del tmpsession.headers['Connection']
        del tmpsession.headers['Content-Length']
        tmpsession.headers['authority'] = 'www.instagram.com'
        tmpsession.headers['scheme'] = 'https'
        tmpsession.headers['accept'] = '*/*'
        tmpsession.headers['referer'] = "https://www.instagram.com/ghostwyd/"

        print_dict(tmpsession.headers)
        first_json_variable = {"user_id":"1625638499","include_chaining":True,"include_reel":True,"include_suggested_users":False,"include_logged_out_extras":False,"include_highlight_reels":False,"include_related_profiles":False}
        query_data = {"query_hash":"c9100bf9110dd6361671f113dd02e7d6", "variables":json.dumps(first_json_variable, separators=(',', ': '))}
        resp = tmpsession.get("https://www.instagram.com/graphql/query/", params=query_data, allow_redirects=False)

        print("is_redirect:{}".format(resp.is_redirect))
        print("status_code:{}".format(resp.status_code))
        if resp.status_code != 200:
            sys.exit(-9)

        resp_json = resp.json()
        if resp_json["status"] != "ok":
            print("unexpected status:{} in resp_json".format(resp_json["status"]))
            sys.exit(10)
        else:
            print("status ok!")

        print(json.dumps(resp_json, indent=2))
        #resp_node = lambda b:b["data"]["user"]["edge_owner_to_timeline_media"]["edges"]["node"](resp_json)
        pic_count = resp_json["data"]["user"]["edge_owner_to_timeline_media"]["count"]
        page_info = resp_json["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]
        has_next = page_info["has_next_page"]
        end_cursor = page_info["end_cursor"]
        print("count:{0}, hash_next:{1}, end_cursor:{2}".format(pic_count, hash_next, end_cursor))

if __name__ == "__main__":
    session = login()
    print_dict(session.cookies.get_dict())
    #crawl_urls(session, "177650381")
    get_profile("liyaya.kicker", session)
