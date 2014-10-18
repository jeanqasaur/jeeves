# -*- coding: iso-8859-15 -*-
"""Conf FunkLoad test

$Id$
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase

class Hipaa(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def test_simple(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        nb_time = self.conf_getInt('test_simple', 'nb_time')
        for i in range(nb_time):
            self.get(server_url, description='Get url')
        # end of test -----------------------------------------------

    '''
    def test_login(self):
        # The description should be set in the configuration file
        server_url = self.server_url

        self.get(server_url + "/",
            description="Get /")
        reply = self.get(server_url + "/index",
            description="Get index")

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/accounts/manager/login/?next=/index/",
            ['csrfmiddlewaretoken', csrftoken],
            ['redirect_to', '/company/config/dashboard/'],
            ['id_username', 'jeanyang'],
            ['id_password', 'hi'],
            description="Post /accounts/login/")

        self.assert_("login" not in self.getLastUrl(), "Error in login")

        self.get(server_url + "/accounts/logout/",
            description="Get /accounts/logout/")
    '''

if __name__ in ('main', '__main__'):
    unittest.main()
