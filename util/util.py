from typing import Dict
import json

__all__ = [
        'print_dict',
        'parse_dict_2_query_params'
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

