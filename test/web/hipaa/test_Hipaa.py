# -*- coding: iso-8859-15 -*-
"""Conf FunkLoad test

$Id$
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.Lipsum import Lipsum
from funkload.utils import extract_token
from funkload.utils import xmlrpc_get_credential

class Hipaa(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        self.lipsum = Lipsum()

    def login_as(self, username, password, pageURL="/index", descr="Get index"):
        # The description should be set in the configuration file
        server_url = self.server_url

        reply = self.get(server_url + "/index",
            description="Get index")

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/accounts/login/?next=" + pageURL,
            params=[['csrfmiddlewaretoken', csrftoken],
            ['redirect_to', pageURL],
            ['username', username],
            ['password', password]],
            description="Post /accounts/login/")

    def logout(self):
        self.get(self.server_url + "/accounts/logout/",
                    description="Get /accounts/logout/")

    def test_simple(self):
        # The description should be set in the configuration file
        server_url = self.server_url
        # begin of test ---------------------------------------------
        nb_time = self.conf_getInt('test_simple', 'nb_time')
        for i in range(nb_time):
            self.get(server_url, description='Get url')
        # end of test -----------------------------------------------

    def test_login(self):
        page="/index"
        self.login_as("admin", "admin")
        reply = self.get(self.server_url + page, description="Get index")
        self.logout()

    def test_register(self):
        self.logout()

        num_users = self.conf_getInt('test_register', 'num_users')
        for i in range(num_users):
            username = self.lipsum.getUniqWord()
            password = self.lipsum.getWord()
            name = self.lipsum.getWord() + " " + self.lipsum.getWord()
            email = self.lipsum.getWord() + "@example.org"

            server_url = self.server_url

            csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
            self.post(server_url + "/register",
                params=[ ['csrfmiddlewaretoken', csrftoken],
                ['username', username],
                ['password1', password],
                ['password2', password],
                ['name', name],
                ['email', email],
                ['profiletype', '1']],
                description="Post /register")

            self.assert_("index" in self.getLastUrl(), "Error in registration")
            self.logout()

    def test_credential(self):
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        login, pwd = xmlrpc_get_credential(credential_host, credential_port
            , "group1")
        self.login_as(login, pwd)
        self.logout()

    def test_show_all_users(self):
        page = "/users"
        self.login_as("admin", "admin", page, "Get users")
        self.assert_(page == self.getLastUrl(), "Error in login")
        reply = self.get(self.server_url + page, description="Get users")
        self.logout()

if __name__ in ('main', '__main__'):
    unittest.main()
