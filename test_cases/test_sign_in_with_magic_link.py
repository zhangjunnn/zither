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
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin

import os
import configparser
import datetime
import time
import sys

import pyautogui

sys.path.append("./lib")
from comm_lib import commLib

class TestSignInWithMagicLink(commLib):

    def setup_method(self):
        self.init(os.getenv("TEST_ENV"),'test')
        
    def teardown_method(self):
        time.sleep(3)
        self.screen_shot()
        self.driver.quit()

    def test_login_with_magic_link(self):
        self.open_target_url()
        self.wait_page_loading()
        if not self.does_page_contain('Enter your'):
           self.click('SIGN IN')
        
        self.type('testaccount@gradual.com','Enter your') 
        self.click('Continue')
        self.wait_until_page_contains('We sent you a magic link to log in')
        
        self.start_browser('email')
        self.open_gmail()
        self.search_in_email('Sign in')
        self.click_exactly('Sign in')
        self.click('User options menu')
        self.check_that_page_contains('Edit Profile')

         
         
if __name__ == "__main__":
    pytest.main(["-v", "test_move_by_offset_from_element"])
