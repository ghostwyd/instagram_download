#!/usr/bin/python
# -*- coding: UTF-8 -*-

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
str_data = '''query_hash=e769aa130647d2354c40ea6a439bfc08&variables=%7B%22id%22%3A%224491871332%22%2C%22first%22%3A12%2C%22after%22%3A%22QVFBV3RnT0dwbXlQMXlGNDVjU3JKM2lwTWRIOFB3V0x3eXJyZU5GbGxQZlJWcUhXZHlqYkFQbkMxc3B1aGlwRV9tYXE2TEpIaDUwZ3RqOWZ5VHB5V2dDRg%3D%3D%22%7D'''
print(parse.unquote(str_data))
