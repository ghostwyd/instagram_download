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
#        break
    #做一些其它的事情
    print("do something.")
    print("end.")

def call(i):
    print("**********")
    return i*2

#使用for循环
for i in yield_test(5):
    print(i,",")

import json
import html
from urllib import parse
import sys
import requests
import requests.utils
import pickle
