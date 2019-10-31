'''
Test ecr template creation, resource creation
and resource functionality for Anchore Engine Repository
'''
import os 
import unittest
import pytest
from anchore import ecr, main
from tests.mocks import schema

class TestECR(unittest.TestCase):
	def setUp(self):
		self.template = ecr.ECRTemplate()

	def test_add_descriptions(self):
		template_file = self.template.add_descriptions("foobar")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_DESCRIPTION)

	def test_add_version(self):
		template_file = self.template.add_version("2010-09-09")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_VERSION)

	def test_create_alb_template(self):
		test_engine = main.AnchoreEngine()
		self.assertEqual (test_engine.create_ecr_template(), schema.mocked_ecr_template())

	def tearDown(self):
		self.template = ecr.ECRTemplate()
