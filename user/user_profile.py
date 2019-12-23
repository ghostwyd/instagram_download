import requests

__all__ = [
    #class
    'UserProfile'
        ]

class UserProfile:
    def __init__(self, user_name:str, user_id:str="", ):
        self._user_id = user_id
        self._post_count = 0
        self._user_name = user_name
        self._end_cursor = ""
        self._batch_get_count = 12
        self._follow_count = 0
        self._followed_by_count = 0
        self._session = None
        self._dst_dir = ""

    def set_user_id(self, user_id:str):
        self._user_id = user_id

    def set_dst_dir(self, dst_dir:str):
        self._dst_dir = dst_dir

    def set_end_cursor(self, end_cursor:str):
        self._end_cursor = end_cursor

    def set_follow_count(self, follow_count:int):
        self._follow_count = follow_count

    def set_followed_by_count(self, followed_by_count:int):
        self._followed_by_count = followed_by_count

    def set_session(self, session:requests.Session):
        self._session = session

    def set_post_count(self, post_count:int):
        self._post_count = post_count

    def print(self):
        print("user_name:{}, user_id:{}, follow_count:{}, followed_by_count:{},post_count:{},end_cursor:{}, dst_dir:{}".format(
                self._user_name, self._user_id, self._follow_count, self._post_count, self._post_count, self._end_cursor, self._dst_dir))

