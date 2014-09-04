"""Course manager tests.

    :synopsis: Tests for the course manager case study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from coursemanager.models import Course, CourseInstructor, StudentCourse, \
    UserProfile

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
        self.janeUser = UserProfile.objects.create(
          username="jane"
        , email="janedoe@mit.edu"
        , name="Jane Doe"
        , role='s')
        self.rishabhUser = UserProfile.objects.create(
          username="rishabh"
        , email="risgreat@gmail.com"
        , name="Rishabh Singh"
        , role='i')

        # Courses.
        self.course813 = Course.objects.create(
            name="User Interface Design", courseId="6.813")
        CourseInstructor.objects.create(
            course=self.course813, instructor=self.rishabhUser)

        StudentCourse.objects.create(
            student=self.benUser, course=self.course813, grade='B')

    def test_get_sample_data(self):
        ben = UserProfile.objects.get(username="ben")
        self.assertEqual(JeevesLib.concretize(ben, ben), self.benUser)

    def test_is_instructor(self):
        self.assertTrue(JeevesLib.concretize(self.benUser
            , self.rishabhUser.is_instructor(self.course813)))
        self.assertFalse(JeevesLib.concretize(self.benUser
            , self.benUser.is_instructor(self.course813)))

    def test_view_email(self):
        self.assertEqual(JeevesLib.concretize(self.benUser, self.benUser.email)
            , "ben@mit.edu")
        self.assertEqual(JeevesLib.concretize(self.janeUser, self.benUser.email)
            , "[redacted]")
        self.assertEqual(
            JeevesLib.concretize(self.rishabhUser, self.benUser.email)
            , "[redacted]")

    def test_view_grade(self):
        course_info = StudentCourse.objects.get(student=self.benUser)
        self.assertEqual(JeevesLib.concretize(self.benUser, course_info.grade)
            , 'B')
        self.assertEqual(JeevesLib.concretize(self.janeUser, course_info.grade)
            , 'U')
        self.assertEqual(
            JeevesLib.concretize(self.rishabhUser, course_info.grade)
            , 'B')
