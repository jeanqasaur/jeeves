"""Conference management tests.

    :synopsis: Tests for the conference management case study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import datetime
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from conf.models import Paper, PaperVersion, UserProfile
from sourcetrans.macro_module import macros, jeeves

import nose.tools as nt


class TestConf(TestCase):
    def setUp(self):
        JeevesLib.init()

        self.jeanyangProfile = UserProfile.objects.create(
            username="jeanyang"
            , email=""
            , name="Jean Yang"
            , affiliation="MIT"
            , level='normal')

        paper0 = Paper.objects.create(author=self.jeanyangProfile
            , accepted=False)
        paperversion0 = PaperVersion.objects.create(paper=paper0
            , title="Some Title"
            , abstract="abstract")

    def test_get_user(self):
        jeanyang = UserProfile.objects.get(username="jeanyang")
        self.assertEqual(JeevesLib.concretize(jeanyang, jeanyang)
            , self.jeanyangProfile)

    def test_get_all_papers(self):
        papers = Paper.objects.all()
        self.assertEqual(1, JeevesLib.concretize(self.jeanyangProfile
            , papers.__len__()))

    @jeeves
    def test_all_papers_loop(self):
        papers = Paper.objects.all()
        print papers.prettyPrint()
        print papers.v
        count = 0
        for paper in papers:
            count += 1
        print count
        self.assertEqual(1, JeevesLib.concretize(self.jeanyangProfile
            , count))

