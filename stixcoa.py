#!/usr/bin/env python
# -*- coding: utf-8
#
# Copyright 2019 New Context Services, Inc.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

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
	acttype = coaobj.action_type

	if acttype == 'programmatic:application/x-python-code':
		code = fetchcode(coaobj)

		vars = {}
		exec(code, vars)
	else:
		raise ValueError('cannot handle action type: %s' % `acttype`)

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

		# that a bad type
		coaobj = coaobj.new_version(action_type='bogus:mime-type')

		# raises an exception
		self.assertRaises(ValueError, runcoa, coaobj)
