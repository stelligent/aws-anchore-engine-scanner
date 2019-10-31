'''
Test ecs template creation, resource creation
and resource functionality for Anchore Engine ECS
'''
import os 
import unittest
import pytest
from anchore import ecs, main
from tests.mocks import schema

class TestECS(unittest.TestCase):
	def setUp(self):
		self.template = ecs.ECSTemplate()

	def test_add_descriptions(self):
		template_file = self.template.add_descriptions("foobar")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_DESCRIPTION)

	def test_add_version(self):
		template_file = self.template.add_version("2010-09-09")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_VERSION)

	def test_create_alb_template(self):
		test_engine = main.AnchoreEngine()
		self.assertEqual (test_engine.create_ecs_template(), schema.mocked_ecs_template())

	def tearDown(self):
		self.template = ecs.ECSTemplate()
