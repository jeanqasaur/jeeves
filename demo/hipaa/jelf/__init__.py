# Since other files in this module (e.g., views.py) use macropy,
# we need to active it here (since this file will always get imported
# first).

from django.conf import settings
import csv
import os

# TODO: Move this somewhere else?
file=open(os.path.join(settings.BASE_DIR, '2010ZipcodePopulation.csv'))
reader = csv.reader(file)
zipCodes = {}
reader.next()
for row in reader:
	zipCodes[row[0]]=int(row[1])

restrictedZipCodes={}
for code in zipCodes:
	if code[:3] in restrictedZipCodes:
		restrictedZipCodes[code[:3]]+=zipCodes[code]
	else:
		restrictedZipCodes[code[:3]]=zipCodes[code]

import macropy.activate
import JeevesLib
JeevesLib.init()
