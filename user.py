class UserProfile:
    def __init__(self, user_name:str, user_id:str="", ):
        self._user_id = user_id
        self._count = 0
        self._user_name = user_name
        self._end_cursor = ""
        self._first_get_count = 12
        self._batch_get_count = 50

    def set_user_id(self, user_id:str):
        self._user_id = user_id

    def set_end_cursor(self, user_id:str):
        self._user_id = user_id
