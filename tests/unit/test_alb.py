'''
Test alb template creation, resource creation
and resource functionality for Anchore alb
'''
import os 
import unittest
import pytest
from anchore import alb, main
from tests.mocks import schema

class TestALB(unittest.TestCase):
	def setUp(self):
		self.template = alb.ALBTemplate()

	def test_add_descriptions(self):
		template_file = self.template.add_descriptions("foobar")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_DESCRIPTION)

	def test_add_version(self):
		template_file = self.template.add_version("2010-09-09")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_VERSION)

	def test_create_alb_template(self):
		test_engine = main.AnchoreEngine()
		self.assertEqual(test_engine.create_alb_template(), schema.mocked_alb_template())

	def tearDown(self):
		self.template = alb.ALBTemplate()
