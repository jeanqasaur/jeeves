# -*- coding: iso-8859-15 -*-
"""Conf FunkLoad test

$Id$
"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.utils import extract_token
from funkload.utils import xmlrpc_get_credential

class Jcourse(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')

        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        self.username, self.pwd = xmlrpc_get_credential(
            credential_host, credential_port, "group1")


    def login(self, page="/index"):
        # The description should be set in the configuration file
        server_url = self.server_url

        reply = self.get(server_url + "/index",
            description="Get index")

        csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
        self.post(server_url + "/accounts/login/?next=" + page,
            params=[['csrfmiddlewaretoken', csrftoken],
            ['redirect_to', page],
            ['username', self.username],
            ['password', self.pwd]],
            description="Post /accounts/login/")

    def logout(self):
        self.get(self.server_url + "/accounts/logout/",
                    description="Get /accounts/logout/")

    def test_show_all_assignments(self):
        page = "/courses"
        self.login(page)
        self.assert_(page == self.getLastUrl(), "Error in login")
        reply = self.get(self.server_url + page, description="Get assignments")
        self.logout()

if __name__ in ('main', '__main__'):
    unittest.main()
