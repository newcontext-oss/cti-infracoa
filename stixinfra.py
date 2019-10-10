#!/usr/bin/env python
# -*- coding: utf-8

from stix2.v21 import CustomObject, Infrastructure
from stix2.v21.bundle import Bundle
from stix2 import parse, properties

import unittest

__copyright__ = 'Copyright 2019 New Context Services, Inc.'
__maintainer__ = 'John-Mark Gurney'
__email__ = 'jmg@newcontext.com'

@CustomObject('ipv4-addr', [
	('value', properties.StringProperty),
	])
class IPv4Addr(object):
	pass

class Tests(unittest.TestCase):
	def test_standardsample(self):
		with open('std_4_9.json') as fp:
			bundle = parse(fp)
