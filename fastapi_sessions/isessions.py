from uuid import uuid4
from fastapi import Request, Response

class Sessions:
    def get(self, request:Request, response:Response)->any:
        session = request.cookies.get("session")
        if not self._is_session_valid(session):
            session = str(uuid4())
            self._add_session(session)
            response.set_cookie(
                key="session",
                value=session,
            )
        return self._get_session(session)

    def getifpresent(self, request:Request, response:Response)->any:
        session = request.cookies.get("session")
        if not self._is_session_valid(session):
            return None
        return self._get_session(session)

    def drop(self, request:Request)->bool:
        session = request.cookies.get("session")
        if self._is_session_valid(session):
            self._remove_session(session)
            return True
        else:
            return False
    
    def update(self, data):
        self._update_session(data)

    def _add_session(self, session:str):
        raise NotImplementedError()

    def _get_session(self, session:str):
        raise NotImplementedError()

    def _update_session(self, data):
        raise NotImplementedError()
    
    def _remove_session(self, session:str):
        raise NotImplementedError()

    def _is_session_valid(self, session:str):
        raise NotImplementedError()