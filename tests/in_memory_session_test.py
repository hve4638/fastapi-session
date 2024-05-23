import unittest
from fastapi_sessions import InMemorySessions, Sessions
from .mock import MockRequest, MockResponse

class Data:
    def __init__(self):
        self.name = 'unknown'

class TestInMemorySessions(unittest.TestCase):
    def setUp(self):
        self.sessions = InMemorySessions(Data)
        self.data = {}
        self.request = MockRequest(self.data)
        self.response = MockResponse(self.data)

    def test_getifpresent(self):
        data = self.sessions.getifpresent(self.request, self.response)
        self.assertIsNone(data)
    
    def test_get(self):
        data = self.sessions.get(self.request, self.response)
        self.assertIsNotNone(data)

    def test_maintain_session(self):
        data1 = self.sessions.get(self.request, self.response)
        data1.name = 'guest'
        
        data2 = self.sessions.get(self.request, self.response)
        self.assertEqual('guest', data2.name)
        
    def test_drop_and_get(self):
        expected = self.sessions.getifpresent(self.request, self.response)
        self.assertIsNone(expected)

        self.sessions.get(self.request, self.response)
        
        expected = self.sessions.getifpresent(self.request, self.response)
        self.assertIsNotNone(expected)

        self.sessions.drop(request=self.request)
        
        expected = self.sessions.getifpresent(self.request, self.response)
        self.assertIsNone(expected)
