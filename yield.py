#!/usr/bin/python

from urllib.parse import urlparse
#def fab(max):
#    n, a, b = 0, 0, 1
#    while n < max:
#        yield b      # 使用 yield
#        a, b = b, a + b
#        n = n + 1
#
#for n in fab(10):
#    print(n)

#encoding:UTF-8
def yield_test(n):
    for i in range(n):
        print("---------")
        yield call(i)
        print("i=",i)
    #做一些其它的事情
    print("do something.")
    print("end.")

def call(i):
    print("**********")
    return i*2

#使用for循环
#for i in yield_test(5):
#    print(i,",")


import json
import html
from urllib import parse
import sys
str_url = '/graphql/query/?query_hash=109cdd03d7468e12222ad164fbea3ca3&variables=%7B%22shortcode%22%3A%22B6a4bLBh3hT%22%2C%22child_comment_count%22%3A3%2C%22fetch_comment_count%22%3A40%2C%22parent_comment_count%22%3A24%2C%22has_threaded_comments%22%3Atrue%7D'
str_url = 'https://www.instagram.com/graphql_query?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables={"child_comment_count":3,"fetch_comment_count":40,"parent_comment_count":24,"has_threaded_comments":true,"shortcode":"B6bEZIPBVPY"}'
print(parse.unquote(str_url))
sys.exit(0)
print(parse.quote(parse.unquote(str_url)))


import requests
import requests.utils
import pickle

sessionfile = "./session-ghostwyd"
session = requests.Session()
with open(sessionfile, 'rb') as fp:
    session.cookies = requests.utils.cookiejar_from_dict(pickle.load(fp))

for key in session.cookies.get_dict():
    print("{}:{}".format(key, session.cookies.get_dict()[key]))


str_json = '{"a":1, "b":2}'
import json
print(type(json.loads(str_json)))
