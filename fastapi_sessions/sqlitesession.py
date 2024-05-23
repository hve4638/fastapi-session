import sqlite3
from datetime import datetime, timedelta
from .isessions import Sessions
from .exceptions import InvalidSchema

class SQLiteSessions(Sessions):
    __reversed_schema = set(['sessionid'])

    def __init__(self, datadef, *, database:str=':memory:', timeout=86400):
        self.connect = sqlite3.connect(database)
        self.schema_template = datadef
        self.schemas = self.__parse_schema(self.schema_template)
        
        self.timeout = timeout
        if timeout:
            self.timeout_td = timedelta(seconds=timeout)
        
        self.__init_db()
    
    def __init_db(self):
        cur = self.connect.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS Session(id TEXT PRIMARY KEY, expired FLOAT)')
        
        text_schemas = self.__get_schema_texts()
        text_fullschemas = ['sessionid TEXT PRIMARY KEY'] + text_schemas
        query_schema = ', '.join(text_fullschemas)

        query = f'CREATE TABLE IF NOT EXISTS UserData({query_schema})'
        cur.execute(query)
        self.connect.commit()

    def __get_schema_texts(self)->list[str]:
        return [ f'{key} {value}' for key, value in self.schemas ]
    
    def __get_schema_names(self)->list[str]:
        return [ key for key, value in self.schemas ]

    def __parse_schema(self, schema_template):
        schemas = []
        names = [ (name, type_) for name, type_ in vars(schema_template()).items() if not name.startswith("__") ]
        for name, type_ in names:
            if name in self.__reversed_schema:
                raise InvalidSchema(f'This keyword is reversed. (\'{name}\')')
            elif type_ is int:
                schemas.append((name, 'INT'))
            elif type_ is float:
                schemas.append((name, 'FLOAT'))
            elif type_ is str:
                schemas.append((name, 'TEXT'))
            elif type_ is bytes:
                schemas.append((name, 'BLOB'))
            elif type_ is None:
                schemas.append((name, 'NULL'))
            else:
                raise InvalidSchema(f'Invalid type (\'{name}\')')
        return schemas

    def _add_session(self, session:str):
        expired = (datetime.now() + self.timeout_td).timestamp() if self.timeout else None

        cur = self.connect.cursor()
        cur.execute('INSERT INTO Session(id, expired) VALUES (?, ?)', [session, expired])
        cur.execute('INSERT INTO UserData(sessionid) VALUES (?)', [session])
        self.connect.commit()

    def _get_session(self, session:str):
        schema_names = self.__get_schema_names()
        schema_text = ','.join(schema_names)

        cur = self.connect.cursor()
        cur.execute(f'SELECT {schema_text} FROM UserData WHERE sessionid = ?', [session])
        result = cur.fetchone()

        obj = self.schema_template()
        obj.sessionid = session
        for key, value in zip(schema_names, result):
            setattr(obj, key, value)

        return obj

    def _update_session(self, data):
        schema_names = self.__get_schema_names()
        query_update = ','.join(f'{names} = ?' for names in schema_names)

        params = []
        for name in schema_names:
            params.append(getattr(data, name, None))

        cur = self.connect.cursor()
        cur.execute(f'UPDATE UserData SET {query_update} WHERE sessionid = ?', params + [data.sessionid])
        self.connect.commit()
    
    def _remove_session(self, session:str):
        cur = self.connect.cursor()
        cur.execute('DELETE FROM Session WHERE id = ?', [session])
        cur.execute('DELETE FROM UserData WHERE sessionid = ?', [session])
        self.connect.commit()

    def _is_session_valid(self, session:str):
        cur = self.connect.cursor()
        cur.execute(f'SELECT expired FROM Session WHERE id = ?', [session])
        result = cur.fetchone()

        if session is None or result is None:
            return False
        else:
            expired = result[0]
            ts = datetime.now().timestamp()
            return expired is None or ts <= expired

