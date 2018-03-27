from django.template import RequestContext
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django import template

from sourcetrans.macro_module import macros, jeeves
from conf.models import UserProfile 

import JeevesLib
import logging

register = template.Library()

@register.filter
def concretizeVal(val, args):
    return JeevesLib.concretize(val, args)

@register.filter
def getRange(val,args):
    return range(int(args) - val.__len__())

@register.filter
def getScoreRange(val):
    return range(1, val+1)
