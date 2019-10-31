'''
Test ec2_cluster template creation, resource creation
and resource functionality for Anchore Engine Repository
'''
import os 
import unittest
import pytest
from anchore import ec2_cluster, main
from tests.mocks import schema

class TestEC2Cluster(unittest.TestCase):
	def setUp(self):
		self.template = ec2_cluster.EC2ClusterTemplate()

	def test_add_descriptions(self):
		template_file = self.template.add_descriptions("foobar")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_DESCRIPTION)

	def test_add_version(self):
		template_file = self.template.add_version("2010-09-09")
		self.assertEqual(template_file.to_yaml(), schema.MOCKED_VERSION)

	def test_create_alb_template(self):
		test_engine = main.AnchoreEngine()
		self.assertEqual(
			test_engine.create_ec2_cluster_template(),
			schema.mocked_ec2_cluster_template()
		)

	def tearDown(self):
		self.template = ec2_cluster.EC2ClusterTemplate()
