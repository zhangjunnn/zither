import random
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common import (
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
#from selenium.common.exceptions import NoSuchElementException
#from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys

import os
import time
import datetime

from catch_task import Catcher
from fo import fileOperator
from Logger import Logger

class commLib:

    #def __init__(self):
    users_in_using=[]
    user_order=0
    user_token_list=[]
    user_info=[] #{'name':'zhj','token':'','email':''}
    options = Options()
    options.add_argument('--headless=new') #headless mode
    options.add_argument(f'user-agent=Mozilla/5.0 (Gradual;E2E) Chrome/120.0.0.0') #skip check
    #options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    #driver.implicitly_wait(30) #default=0
    driver.maximize_window()
    driver.set_page_load_timeout(300)
    wait = WebDriverWait(
            driver,
            timeout=30,
            poll_frequency=.2,
            ignored_exceptions=[
                NoSuchElementException,
                StaleElementReferenceException,
                ElementNotInteractableException,
                
            ],
    )
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/log'
    if not os.path.exists(log_dir):
       os.makedirs(log_dir)
    log = Logger(log_dir)
    catcher = Catcher(driver,log)

    def screen_shot(self):
       ct = time.time()
       current_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(ct))
       current_date = time.strftime("%Y-%m-%d", time.localtime(ct))
       t_ms = (ct - int(ct)) * 1000
       pic_name = "%s_%03d.png" % (current_time,t_ms)
       pic_path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))+'/screenshots/'+current_date+'/'
       if not os.path.exists(pic_path):
           os.makedirs(pic_path)  #
       self.driver.save_screenshot(pic_path + pic_name)
       return pic_name
 
    def logger(self,msg,screenPrint=False):
        self.log.logger(msg,screenPrint)

    def open_url(self,url):
        self.logger('open url:%s'%url)
        try:
           self.driver.get(url)
        except:
           self.logger('open url failed.')
           self.screen_shot()
           raise

    def gen_message_error(self,origin_by,locator,reference_content):

        if(origin_by == 'reference'):
            message = "Can't find element '%s'"%reference_content
        elif (search_info[2] == 'xpath'):
            message = "Can't find element by xpath '%s'"%locator
        else:
            message = "Can't find element by css selector '%s'"%locator
        
        return message

    def type(self,content,reference=None,fuzzy_search=True,xpath=None,css_selector=None):
        self.logger("type:%s"%content)
        elem = self.is_present(reference=reference,fuzzy_search=fuzzy_search,xpath=xpath,css_selector=css_selector,search_tag='input')
        if elem:
           elem.send_keys(content)
        else:
            search_info = self.get_searching_elem_info(reference,fuzzy_search,xpath,css_selector,'input')
            message = self.gen_message_error(search_info[2],search_info[1],reference)
            self.wait.until(visibility_of_element_located((search_info[0], search_info[1])), message)
            self.driver.find_element(search_info[0],search_info[1]).send_keys(content)
           
    def one_login(self):
      self.wait.until(
        lambda driver: visibility_of_element_located((By.XPATH,"//div[text()='Onelogin ・ DevAuth']")) or
                       visibility_of_element_located((By.XPATH,"//div[text()='Home']")) or
                       visibility_of_element_located((By.CSS_SELECTOR,"input[placeholder='Enter your']"))
      )
      if self.is_present('Onelogin ・ DevAuth'):
         self.logger("start onelog") 
         self.click('Onelogin ・ DevAuth')
         #self.driver.find_element(By.ID,"username").send_keys("jun@gradual.com")
         self.type("jun@gradual.com","username")
         self.click_xpath("//button[@type='submit']")
         #self.driver.find_element(By.ID,"password").send_keys("Zhj&123456")
         self.type("Zhj&123456","password")
         self.click_xpath("//button[@type='submit']")
         #time.sleep(10)
         #self.wait.until(
         #     lambda driver: visibility_of_element_located((By.XPATH,"//div[text()='Home']")) or
         #              visibility_of_element_located((By.CSS_SELECTOR,"input[placeholder='Enter your']"))
         #     )
         self.wait.until(visibility_of_element_located((By.XPATH,"//div[text()='Home']")) or visibility_of_element_located((By.CSS_SELECTOR,"input[placeholder='Enter your']")))

         #self.driver.find_element(By.XPATH,value="//div[text()='Onelogin ・ DevAuth']").click()
         #time.sleep(20) 
         #self.driver.find_element(By.ID,"username").send_keys("jun@gradual.com")
         #self.driver.find_element(By.XPATH,value="//button[@type='submit']").click()
         #time.sleep(5)
         #self.driver.find_element(By.ID,"password").send_keys("Zhj&123456")
         #self.driver.find_element(By.XPATH,value="//button[@type='submit']").click()
         #time.sleep(10)

      else:
         self.logger("no need [one login]")
 
    def open_target_url(self):
        self.domain = self.target + '.'+self.config.get('gradual','domain suffix')
        url = "https://%s/"%self.domain
        self.open_url(url)
        self.one_login()
        self.click_if_exist('Got it')
    
    #use token to login
    #param:user_order,the token order that have been fetched from token list
    def user_login(self,user_order=None):
        
        #get user token
        if user_order:
           token = self.user_token_list[user_order - 1]['token']

        else:
          user_list = self.config.get(self.target,'user_list').split(',')
          while True:
            index = random.randint(0,len(user_list)-1)
            if index not in self.users_in_using:
               #print(self.target.upper()+'_' + user_list[index].upper()+'_TOKEN')
               token = os.getenv(self.target.upper()+'_' + user_list[index].upper()+'_TOKEN')
               self.users_in_using.append(index)
               self.user_info.append({'token':token})
               break

        assert token,'get token failed:%s'%token       
        self.open_target_url()

        self.driver.add_cookie({'name':'token-v1','value':token})
        self.driver.add_cookie({'name':'token-v1.1','value':token})
        self.driver.add_cookie({'name':'token-v2','value':token})
        self.driver.refresh()
        self.catcher.start()
        #time.sleep(10)
        self.wait_page_loading()
        
        if not self.is_present('SIGN IN'):
           print('login success')
        else:
           assert False,'login failed' 
   
        #get user name,user role,user email
        #self.driver.find_element(By.XPATH,value="//div[@aria-label='User options menu']")
        self.click("User options menu")
        if not self.is_present('StyledDisplayName'):
           self.click("User options menu")
        userName = self.driver.find_element(By.XPATH,value="//div[contains(@class,'StyledDisplayName')]").text
        userTitle = self.driver.find_element(By.XPATH,value="//div[contains(@class,'StyledDisplayName')]/following-sibling::div[1]").text
        userEmail = self.driver.find_element(By.XPATH,value="//div[contains(@class,'StyledDisplayName')]/following-sibling::div[2]").text
        userRole = userTitle.split(' @ ')[0]
        userCompany = userTitle.split(' @ ')[1]
        userFirstName = userName.split(" ")[0]
        userLastName = userName.split(" ")[1]
        userUglyName = userFirstName + ' ' + userName.split(" ")[1][0:1]
        #make disappear
        self.click("User options menu")
        
        index = len(self.user_info)-1
        self.user_info[index]={'userName':userName}
        self.user_info[index]['userFirstName']=userFirstName
        self.user_info[index]['userLastName']=userLastName
        self.user_info[index]['userUglyName']=userUglyName
        self.user_info[index]['userRole']=userRole
        self.user_info[index]['userCompany']=userCompany
        self.user_info[index]['userEmail']=userEmail
        self.user_info[index]['userTitle']=userTitle
        
        self.logger("user login: %s"%(self.user_info[index]))
   
        return self.user_info[index]
    def wait_page_loading(self):
        #wait to be loading
        try:
           WebDriverWait(self.driver,5,0.2).until(
              visibility_of_element_located((By.CSS_SELECTOR,".css-0")) or visibility_of_element_located((By.CSS_SELECTOR,".nprogress-busy"))
              )
           page_loading = True
           self.logger('the page is loading')
        except TimeoutException:
            page_loading = False

        #wait to disappear
        if page_loading :
              self.logger('wait page loading')
              WebDriverWait(self.driver,300,0.2).until_not(
                visibility_of_element_located((By.CSS_SELECTOR,".css-0")) or visibility_of_element_located((By.CSS_SELECTOR,".nprogress-busy")),'page is still loading...'
               )
              self.logger('page load finished')

        
    def get_fuzzy_xpath(self,reference,search_tag=None):
        search_str = reference.lower()
        if search_tag :
           tag = search_tag
        else:
           tag = '*'

        return """//%s[name() != 'script' and (contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@class,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@id,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@name,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@placeholder,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@value,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    or contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'%s')
                    )]"""%(tag,search_str,search_str,search_str,search_str,search_str,search_str,search_str)

    def get_exact_xpath(self,reference,search_tag=None):
        if search_tag :
           tag = search_tag
        else:
           tag = '*'
        return "//%s[text()='%s' or  @class='%s' or @id='%s' or @name='%s' or @placeholder='%s' or @value='%s' or @aria-label='%s']"%(tag,reference,reference,reference,reference,reference,reference,reference)
    def click_if_exist(self,reference,fuzzy_search=True):
        time.sleep(3)
        elem = self.is_present(reference=reference,fuzzy_search=fuzzy_search)
        if elem:
           self.logger("'%s' exist when clicking"%reference)
           elem.click()
        else:
           self.logger("'%s' not exist when clicking"%reference)

    def click_exactly_if_exist(self,reference):
        self.click_if_exist(reference,False)
    
    def click_exactly(self,reference):
        self.click(reference,False)

    def click(self,reference,fuzzy_search=True,search_tag=None):
        if fuzzy_search:
              xpath = self.get_fuzzy_xpath(reference)
        else:
              xpath = self.get_exact_xpath(reference)
        
        #self.logger('click elem by reference[%s],xpath: %s'%(reference,xpath))
        self.logger("click elem by reference: '%s'"%reference)
        elem = self.is_present(reference=reference,fuzzy_search=fuzzy_search,search_tag=search_tag)
        if elem:
           elem.click()
        else:
            self.wait.until(visibility_of_element_located((By.XPATH, xpath)), "Can't find element '%s'"%reference)
            self.driver.find_elements(By.XPATH,xpath)[0].click()
        
        
    def click_xpath(self,xpath):
        self.logger('click elem by xpath: %s'%xpath)
        elem = self.is_present(xpath=xpath)
        if elem:
           elem.click()

        else:
           self.wait.until(visibility_of_element_located((By.XPATH, xpath)), "Can't find element by xpath '%s'"%xpath)
           self.driver.find_elements(By.XPATH,xpath)[0].click()
        
    def click_css_selector(self,css_selector):
        self.logger('click elem by css selector: %s'%css_selector)
        elem = self.is_present(css_selector=css_selector)
        if elem:
           elem.click()
        else:
           self.wait.until(visibility_of_element_located((By.CSS_SELECTOR, css_selector)), "Can't find element by css selector '%s'"%css_selector)
           self.driver.find_elements(By.CSS_SELECTOR,css_selector)[0].click()
        
    def is_present(self,reference=None,fuzzy_search=True,xpath=None,css_selector=None,search_tag=None):
        search_info = self.get_searching_elem_info(reference,fuzzy_search,xpath,css_selector,search_tag)
        all_elements_matched = self.driver.find_elements(search_info[0],search_info[1])
        all_elements_matched_visible = [elem for elem in all_elements_matched if elem.is_displayed()]

        if (len(all_elements_matched_visible)>0):
           return all_elements_matched_visible[0]

    def wait_until_page_contains(self,reference=None,fuzzy_search=True,xpath=None,css_selector=None,tag_name=None,tm=300):
        self.logger("waiting for: '%s'"%reference)
        search_info = self.get_searching_elem_info(reference,fuzzy_search,xpath,css_selector,tag_name)
        message = self.gen_message_error(search_info[2],search_info[1],reference)
        wait = WebDriverWait(self.driver,tm,0.2)
        #self.logger("wait_until_page_contains:%s,%s"%(search_info[0],search_info[1]))
        wait.until(visibility_of_element_located((search_info[0], search_info[1])), message)
    
    def check_that_page_contains(reference,tm=30):
        self.wait_until_page_contains(reference,tm=30)
    
    def check_that_page_contains_exactly(reference,tm=30):
        self.wait_until_page_contains(reference,False,tm=30)
        
         
    def get_searching_elem_info(self,reference=None,fuzzy_search=True,xpath=None,css_selector=None,tag_name=None):
        reference_content=reference
        if reference:
           origin_by = 'reference'
           by=By.XPATH
           if fuzzy_search:
              value = self.get_fuzzy_xpath(reference,tag_name)

           else:
              value = self.get_exact_xpath(reference,tag_name)
        elif xpath:
           origin_by = 'xpath'
           by = By.XPATH
           value = xpath

        elif css_selector:
           origin_by = 'css_selector'
           by = By.CSS_SELECTOR
           value = css_selector
        
        return (by,value,origin_by,reference_content)
