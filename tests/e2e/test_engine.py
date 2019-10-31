'''
Test Anchore Engine server functionality and usage

Cases: 
    1. Is server up - engine version
    2. Can Ip range access server
    3. CLI configuration and response 
        - credentials
        - user
        - account commands 
'''
import os
import uuid
import json
import requests
import pytest
import unittest

class TestAnchoreEngine(unittest.TestCase):
    '''
    End-to-End class object
    '''
    def setUp(self):
        self.anchore_user = os.environ.get('ANCHORE_CLI_USER', 'admin')
        self.anchore_pass = os.environ.get('ANCHORE_CLI_PASS', 'foobar')
        self.anchore_url = os.environ.get('ANCHORE_CLI_URL', 'http://internal-DEMO-LoadB-TEHME0YAGU49-1824236530.us-east-2.elb.amazonaws.com:8228/v1')


    def test_engine_version(self):
        version = get_engine_version(self.anchore_user, self.anchore_pass, self.anchore_url)
        assert version >= '0.3.0'

    # def test_system_status():

    # def test_account_access():

    # def test_account_lifecycle():

    def tearDown(self):
        self.anchore_user = os.environ.get('ANCHORE_CLI_USER', 'admin')
        self.anchore_pass = os.environ.get('ANCHORE_CLI_PASS', 'foobar')
        self.anchore_url = os.environ.get('ANCHORE_CLI_URL', 'http://internal-DEMO-LoadB-TEHME0YAGU49-1824236530.us-east-2.elb.amazonaws.com:8228/v1')



def get_engine_version(username, password, base_url):
    url = "{}/status".format(base_url)
    r = requests.get(url, auth=(username, password))
    if r.status_code == 200:
        d = r.json()
        return(d.get("version", None))
    else:
        raise AssertionError('Error response for version check: {}'.format(r))
