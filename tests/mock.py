class MockRequest:
    class ResponseCookie:
        def __init__(self, data):
            self.data = data
        
        def get(self, text):
            if text in self.data:
                return self.data[text]
            else:
                return None
    
    def __init__(self, data):
        self.__cookie = self.ResponseCookie(data)
    
    @property
    def cookies(self):
        return self.__cookie
    
class MockResponse:
    def __init__(self, data):
        self.data = data
    
    def set_cookie(self, key, value):
        self.data[key] = value