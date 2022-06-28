# Create your tests here.
from django.test import RequestFactory, TestCase
from  middleware import UserIPBlocker
from mock import patch, Mock
import unittest
import os

class TestMiddleware(unittest.TestCase):

    @patch('middle.MyMiddleware')
    def test_init(self, my_middleware_mock):
        my_middleware = UserIPBlocker('response')
        assert(my_middleware.get_response) == 'response'

    def test_mymiddleware(self):
        request = Mock()
        my_middleware = UserIPBlocker(Mock())
        # CALL MIDDLEWARE ON REQUEST HERE
        my_middleware(request)
        assert request.new_attribute == 'OK'
