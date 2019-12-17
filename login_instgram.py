import http.client
import requests
import requests.utils
import ssl
from typing import Dict

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

def print_cookie(dict_cookie:Dict[str, str]):
    for key in dict_cookie:
        print("{0}:{1}".format(key, dict_cookie[key]))

if __name__ == "__main__":
    HOST = "https://www.instagram.com/"
    session = requests.Session()
    session.cookies.update({'sessionid':'', 'mid':'', 'ig_pr':'1',
                            'ig_vw':'1920', 'ig_cb':'1', 'csrftoken':'',
                            's_network':'', 'ds_user_id':''})
    session.headers.update(default_http_header(True))
    print_cookie(session.cookies.get_dict())
    rsp = session.get('https://www.instagram.com/web/__mid/')
    print("---------------")
    print_cookie(session.cookies.get_dict())

