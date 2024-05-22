from datetime import datetime, timedelta
from .isessions import Sessions

class InMemorySessions(Sessions):
    def __init__(self, data_constructor, *, timeout=86400):
        self.session_data:dict[int, dict] = {}
        self.userdata:dict[int, any] = {}
        self.data_constructor = data_constructor
        
        self.timeout = timeout
        if timeout:
            self.timeout_td = timedelta(seconds=timeout)

    def _add_session(self, session:str):
        self.session_data[session] = {
            'expired' : datetime.now() + self.timeout_td if self.timeout else None,
        }
        self.userdata[session] = self.data_constructor()

    def _get_session(self, session:str):
        return self.userdata.get(session)

    def _remove_session(self, session:str):
        self.session_data.pop(session)
        self.userdata.pop(session)

    def _is_session_valid(self, session:str):
        if session is None or session not in self.session_data:
            return False
        else:
            expired = self.session_data[session]['expired']
            return expired is None or datetime.now() <= expired