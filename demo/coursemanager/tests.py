"""Course manager tests.

    :synopsis: Tests for the course manager case study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from coursemanager.models import Course, CourseInstructor, UserProfile

import nose.tools as nt


class TestJeevesModel(TestCase):
    def setUp(self):
        JeevesLib.init()

        # Users.
        self.benUser = UserProfile.objects.create(
          username="ben"
        , email="ben@mit.edu"
        , name="Ben Shaibu"
        , role='s')
        self.rishabhUser=UserProfile.objects.create(
          username="rishabh"
        , email="risgreat@gmail.com"
        , name="Rishabh Singh"
        , role='i')

        # Courses.
        self.course813=Course.objects.create(
            name="User Interface Design", courseId="6.813")
        CourseInstructor.objects.create(
            course=self.course813, instructor=self.rishabhUser)

    def testGetSampleData(self):
        ben = UserProfile.objects.get(username="ben")
        self.assertEqual(JeevesLib.concretize(ben, ben), self.benUser)

    def testGetInstructor(self):
        self.assertTrue(JeevesLib.concretize(self.benUser
            , self.rishabhUser.is_instructor(self.course813)))
        self.assertFalse(JeevesLib.concretize(self.benUser
            , self.benUser.is_instructor(self.course813)))
