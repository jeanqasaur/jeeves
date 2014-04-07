#!/usr/bin/env python
import os
import sys

import macropy.activate
from macropy.core.exporters import SaveExporter
macropy.exporter = SaveExporter("exported", ".")

import JeevesLib
JeevesLib.init()

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
