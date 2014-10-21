# -*- coding: iso-8859-15 -*-
"""Conf FunkLoad test

$Id$
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import extract_token

class Hipaa(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    '''
    def test_simple(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        nb_time = self.conf_getInt('test_simple', 'nb_time')
        for i in range(nb_time):
            self.get(server_url, description='Get url')
        # end of test -----------------------------------------------
    '''

    def login_as(self, username, pwd):
        # The description should be set in the configuration file
        server_url = self.server_url

        self.get(server_url + "/",
            description="Get /")
        reply = self.get(server_url + "/index",
            description="Get index")

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/accounts/login/?next=/",
            params=[['csrfmiddlewaretoken', csrftoken],
            ['redirect_to', '/company/config/dashboard/'],
            ['username', username],
            ['password', pwd]],
            description="Post /accounts/login/")

    def logout(self):
        self.get(self.server_url + "/accounts/logout/",
                    description="Get /accounts/logout/")

    def test_login(self):
        self.login_as("jeanyang", "hi")
        #self.login_as("admin", "admin")
        self.logout()

if __name__ in ('main', '__main__'):
    unittest.main()
