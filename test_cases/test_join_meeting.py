# -*- coding: utf-8 -*-
import pytest
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import os
import configparser
import datetime
import time
import sys

sys.path.append("./lib")
from comm_lib import commLib

#env = os.getenv("CUR_ENV")
#tenant = os.getenv("CUR_TARGET")
env='stg'
target='testrigor'

class TestJoinMeeting(commLib):
    """join meeting test case"""

    def setup_method(self):
        #---
        self.env=env
        self.target=target

        #---load config
        self.config = configparser.ConfigParser()
        self.config.read('./config/%s.ini'%self.env)
        
    def teardown_method(self):
        self.screen_shot()
        self.driver.quit()
    
    def test_join_meeting(self):
        user_1 = self.user_login() 
        print(user_1)
        
        #search event:meeting
        self.type("Meeting003-for-ci-test","Search")
        self.type(Keys.ENTER,"Search")
        self.wait_until_page_contains("Search results for")
        self.wait_page_loading()
        self.click_exactly_if_exist("Join")
        self.click_exactly_if_exist("Register")
        self.wait_page_loading()
        #self.wait_until_page_contains('Allow Access')
        #self.click_exactly('Allow Access')
        self.wait_until_page_contains('Join now')
        self.screen_shot()
        self.click('Join now')
        self.wait_until_page_contains(user_1['userUglyName'])
        time.sleep(10)
         
if __name__ == "__main__":
    pytest.main(["-v", "test_join_meeting.py"])
