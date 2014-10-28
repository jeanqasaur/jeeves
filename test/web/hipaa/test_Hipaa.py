# -*- coding: iso-8859-15 -*-
"""Conf FunkLoad test

$Id$
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import extract_token
from funkload.utils import xmlrpc_get_credential

class Hipaa(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

    def login_as(self, username, password):
        # The description should be set in the configuration file
        server_url = self.server_url

        self.get(server_url + "/",
            description="Get /")
        reply = self.get(server_url + "/index",
            description="Get index")

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/accounts/login/?next=/",
            params=[['csrfmiddlewaretoken', csrftoken],
            ['redirect_to', '/index'],
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
        self.login_as("jeanyang", "hi")
        self.logout()

        self.login_as("admin", "admin")
        self.logout()

    def test_register(self):
        self.logout()

        username = "new_user"
        password = "password"

        server_url = self.server_url
        # self.get(server_url + "/register", description='Get url')

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/register",
            params=[ ['csrfmiddlewaretoken', csrftoken],
            ['username', 'newuser5'],
            ['password1', 'password'],
            ['password2', 'password'],
            ['name', 'New User'],
            ['email', 'new_user@example.org'],
            ['profiletype', '1']],
            description="Post /register")

    def test_credential(self):
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        login, pwd = xmlrpc_get_credential(credential_host, credential_port
            , "group1")
        self.login_as(login, pwd)
        self.logout()


if __name__ in ('main', '__main__'):
    unittest.main()
