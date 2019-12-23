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
str_url = '''https://www.instagram.com/graphql/query/?                                                                   query_hash=e769aa130647d2354c40ea6a439bfc08&variables=%7B%22id%22%3A%226998411785%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFCbEVIbzNoNGR     tUVNzTXl1VGdsNkQ5ZVZpa3Roa0c0YVJucVRQREpING40MDV0V2dIZUtfS25LOG91bXZNUWlKbmxOM1Z0ZTN4RFZpTXlYd25NaklZcw%3D%3D%22%7D'''
print(str_url)
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
