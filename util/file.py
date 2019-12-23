import os
import sys

def mkdir(dir_name: str):
    if os.path.exists(dir_name):
        if not os.path.isdir(dir_name):
            raise PathIsDirException("{} is not dir!".format(dir_name))
    else:
        os.mkdir(dir_name, 0o744)

