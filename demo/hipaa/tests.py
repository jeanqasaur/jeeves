"""HIPAA tests.

    :synopsis: Tests for the HIPAA case study.

.. moduleauthor:: Jean Yang <jeanyang@csail.mit.edu>
"""
from datetime import date
from django.contrib.auth.models import User
from django.db import models
from django.utils import unittest
from django.test import TestCase

import JeevesLib

from jeevesdb import JeevesModel
from jelf.models import Address, CoveredEntity, HospitalVisit, Individual, UserProfile

import nose.tools as nt


class TestHealthModels(TestCase):
    def setUp(self):
        JeevesLib.init()

        self.arielsHouse=Address.objects.create(
            City="Cambridge",
            State="MA",
            Street="5 Y St.",
            ZipCode="14830")

        self.house1=Address.objects.create(
            City="Boston",
            State="MA",
            Street="625 Frost Ln.",
            ZipCode="14830")

        self.jean=Individual.objects.create(
            FirstName="Jean"
            , LastName="Yang"
            , Email="jean@example.com"
            , Sex="Female"
            , BirthDate=date(1900,01,01)
            , Address=self.house1)

        self.ariel=Individual.objects.create(
            FirstName="Ariel",
            LastName="Jacobs",
            Email="ariel@example.com",
            Sex="Male",
            BirthDate=date(1993,03,21),
            Address=self.arielsHouse)

        self.jeanyang=User.objects.create_user(
            username="jeanyang"
            , password="hi")

        self.jeanyangProfile=UserProfile.objects.create(
            profiletype=1
            , username="jeanyang"
            , email="jeanyang@example.com"
            , name="Jean Yang"
            , individual=self.jean)
        
        self.arielj=User.objects.create_user(
            username="arielj321"
            , email="ariel@example.com"
            , password="hipaaRules")

        self.arielProfile=UserProfile.objects.create(
            profiletype=1
            , username="arielj321"
            , email="ariel@example.com"
            , name="Ariel Jacobs"
            , individual=self.ariel)

        self.vision= CoveredEntity.objects.create(ein = "01GBS253DV"
            , name = "Vision National")
        self.visionProfile=UserProfile.objects.create(
            profiletype=2
            , username="visionhealth"
            , email="vision@example.com"
            , name="Vision National"
            , entity=self.vision)

    def test_get_sample_data(self):
        jeanyang = UserProfile.objects.get(username="jeanyang")
        self.assertEqual(JeevesLib.concretize(self.jeanyangProfile, jeanyang)
            , self.jeanyangProfile)

    def test_see_Address(self):
        self.assertEqual(
            JeevesLib.concretize(self.jeanyangProfile, self.jean.Address)
            , self.house1)
        self.assertEqual(
            JeevesLib.concretize(self.arielProfile, self.jean.Address.Street)
            , None)
        self.assertEqual(
            JeevesLib.concretize(self.arielProfile, self.jean.Address.ZipCode)
            , "14800")

    def test_hospital_visit_visibility(self):
        actual_visit_location = "Third room on the left"
        visit = HospitalVisit.objects.create(patient=self.ariel,
            date_admitted=date(2003,4,1),
            date_released=date(2003,9,13),
            condition="Good",
            location=actual_visit_location,
            hospital=self.vision)
        self.assertEqual(
            JeevesLib.concretize(self.jeanyangProfile, visit.location)
            , HospitalVisit.UNDISCLOSED_LOCATION)
        self.assertEqual(
            JeevesLib.concretize(self.arielProfile, visit.location)
            , actual_visit_location)
        self.assertEqual(
            JeevesLib.concretize(self.visionProfile, visit.location)
            , actual_visit_location)

