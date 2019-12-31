from typing import Dict
import json

__all__ = [
        'print_dict',
        'parse_dict_2_query_params',
        'default_http_header',
        'get_post_format'
        ]

def print_dict(dict_cookie: Dict[str, str]):
    '''
        print key/value in dict
    '''
    for key in dict_cookie:
        print("{0}:{1}".format(key, dict_cookie[key]))
    print("-------------------------")

def parse_dict_2_query_params(dict_params: Dict[str, any]) ->str:
    pairs = []
    for key in dict_params:
        if type(dict_params[key]).__name__ != 'dict':
            pairs.append("{}={}".format(key, dict_params[key]))
        else:
            pairs.append("{}={}".format(key, json.dumps(dict_params[key], separators=(', ', ': '))))

    return "&".join(pairs)

def get_post_format(url: str) ->str:
    index1 = url.rfind('?')
    if index1 == -1:
        return  ''
    index2 = url.rfind('.', 0, index1-1)
    if index2 == -1:
        return  ''
    return url[index2+1:index1]

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
