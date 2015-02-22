# -*- coding: iso-8859-15 -*-
"""ConfDBScaling FunkLoad test

"""
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase
from funkload.Lipsum import Lipsum
from funkload.utils import extract_token
from funkload.utils import xmlrpc_get_credential
from webunit.utility import Upload

class ConfDBScaling(FunkLoadTestCase):
    """This test use a configuration file Conf.conf."""

    def setUp(self):
        """Setting up test."""
        self.server_url = self.conf_get('main', 'url')
        
        credential_host = self.conf_get('credential', 'host')
        credential_port = self.conf_getInt('credential', 'port')
        self.username, self.pwd = xmlrpc_get_credential(
            credential_host, credential_port, "group1")

        self.lipsum = Lipsum()

    def tearDown(self):
        self.logout()

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

    def test_show_all_papers(self):
        page = "/index"
        self.login(page)
        self.assert_(page == self.getLastUrl(), "Error in login")
        reply = self.get(self.server_url + page, description="Get papers")
        self.logout()

    def test_show_all_users(self):
        page = "/users"
        self.login(page)
        self.assert_(page == self.getLastUrl(), "Error in login")
        reply = self.get(self.server_url + page, description="Get papers")
        self.logout()

    def test_view_paper(self):
        page = "/paper?id=0fcKOflDJSAyUrT1BaKOMBfFVQ1Oi57p"
        self.login(page)
        self.assert_("paper" in self.getLastUrl(), "Error in showing paper")
        self.logout()

    # TODO: Submit a paper.
    def test_submit_paper(self):
        page = "/submit"
        self.login(page)
        self.assert_(page == self.getLastUrl(), "Error in login")

        num_papers = self.conf_getInt('test_submit_paper', 'num_papers')
        for i in range(num_papers):
            csrftoken = extract_token(self.getBody(), "name='csrfmiddlewaretoken' value='", "' />")
            self.post(self.server_url + "/submit",
                params=[['csrfmiddlewaretoken', csrftoken],
                ['coauthors[]', self.lipsum.getWord()],
                ['coauthors[]', self.lipsum.getWord()], 
                ['title', self.lipsum.getSentence()],
                ['contents', Upload('files/rms_crossstitch.pdf')],
                ['abstract', self.lipsum.getMessage()]],
                description="Post /accounts/login/")
            self.assert_("paper" in self.getLastUrl(), "Error in login")

    # TODO: View profile.
    def test_view_profile(self):
        page = "/accounts/profile/"
        self.login(page)
        self.assert_(page == self.getLastUrl(), "Error in login")

if __name__ in ('main', '__main__'):
    unittest.main()
