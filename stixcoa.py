#!/usr/bin/env python
# -*- coding: utf-8

from stix2.v21 import CustomObject, CourseOfAction
from stix2.v21.bundle import Bundle
from stix2 import parse, properties
from StringIO import StringIO

import json
import os.path
import shutil
import sys
import tempfile
import unittest

__copyright__ = 'Copyright 2019 New Context Services, Inc.'
__maintainer__ = 'John-Mark Gurney'
__email__ = 'jmg@newcontext.com'

def fetchcode(coaobj):
	return coaobj.action_bin.decode('base64')

def runcoa(coaobj):
	code = fetchcode(coaobj)

	vars = {}
	exec(code, vars)

class Tests(unittest.TestCase):
	def setUp(self):
		# setup temporary directory
		d = os.path.realpath(tempfile.mkdtemp())
		self.homedir = os.getcwd()
		self.basetempdir = d
		self.tempdir = os.path.join(d, 'subdir')
		os.mkdir(self.tempdir)

		os.chdir(self.tempdir)

	def tearDown(self):
		shutil.rmtree(self.basetempdir)
		self.tempdir = None

	def ff(self, *args):
		return os.path.join(self.homedir, *args)

	def test_standardsample(self):
		with open(self.ff('coa_code.txt')) as fp:
			coacode = fp.read()

		with open(self.ff('std_4_3_template.json')) as fp:
			jsonb = json.load(fp)

		jsonb['objects'][0]['action_bin'] = coacode.encode('base64')

		# Don't need to reserialize to JSON, but want to make sure
		# it really gets parsed as JSON
		bundle = parse(json.dumps(jsonb))

		# make sure the action code was inserted correctly
		coaobj = bundle.objects[0]
		self.assertEqual(coacode, coaobj.action_bin.decode('base64'))

		self.assertEqual(coacode, fetchcode(coaobj))

		origstdout = sys.stdout
		newout = StringIO()
		try:
			sys.stdout = newout
			runcoa(coaobj)
		finally:
			sys.stdout = origstdout

		self.assertEqual(newout.getvalue(), 'this is a test\n')
