'''
Test vpc template creation, resource creation
and resource functionality for Anchore vpc
'''
import os 
import unittest
import pytest
from anchore import vpc, main
from tests.mocks import schema

class TestVPC(unittest.TestCase):
	def setUp(self):
		self.template = vpc.VPCTemplate()

	def test_add_descriptions(self):
		template_file = self.template.add_descriptions("foobar")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_DESCRIPTION)

	def test_add_version(self):
		template_file = self.template.add_version("2010-09-09")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_VERSION)

	def test_create_vpc_template(self):
		test_engine = main.AnchoreEngine()
		self.assertEqual (test_engine.create_vpc_template(), schema.mocked_vpc_template())

	def tearDown(self):
		self.template = vpc.VPCTemplate()
