from typing import Dict

__all__ = [
        'print_dict'
        ]

def print_dict(dict_cookie:Dict[str, str]):
    '''
        print key/value in dict
    '''
    for key in dict_cookie:
        print("{0}:{1}".format(key, dict_cookie[key]))
    print("-------------------------")
