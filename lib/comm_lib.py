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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.common.actions.mouse_button import MouseButton

from custom_expected_conditions import (
   is_page_loading,
)
import pyotp
import cv2
import os
import time
import datetime
import configparser

from catch_task import Catcher
from Logger import Logger
from tm import TimeOut
from util import Util

class commLib(Util):

    def init(self,env,target):
       self.env=env
       self.target=target

       #---load config
       self.config = configparser.ConfigParser()
       self.data = configparser.RawConfigParser()
       #base dir
       self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
       config_file_path = self.base_dir + '/config/%s.ini'%self.env
       assert os.path.exists(config_file_path),'config file:%s.ini not exist!'%self.env
       self.config.read(config_file_path)
       data_file_path = self.base_dir + '/data/data.ini'
       assert os.path.exists(data_file_path),'data file: data.ini not exist!'
       self.data.read(data_file_path)
       self.users_in_using=[]
       self.user_order=0
       self.user_token_list=[]
       self.user_info=[] #{'name':'zhj','token':'','email':''}
       self.browsers_tabs={} #{'browser name1':{'tab_queue':[handle1,handle2,...],'cur_tab':handle1,'browser name2':...}
       options = Options()
       #options = webdriver.FirefoxOptions()
       options.add_argument("--disable-infobars")
       options.add_argument("--disable-blink-features=AutomationControlled")
       options.add_argument("--disable-dev-shm-usage")
       options.add_argument("--no-sandbox")
       if not os.path.exists(self.base_dir + '/config/secret.ini'):
          options.add_argument('--headless=new') #headless mode
       options.add_argument("--use-fake-ui-for-media-stream")
       options.add_argument("--use-fake-device-for-media-stream")
       options.add_argument("--disable-popup-blocking")
       options.add_argument("--disable-notifications")
       options.add_argument("--disable-extensions")
       audio_file = self.get_data('mic input')
       video_file = self.get_data('camera input')
       options.add_argument("--use-file-for-fake-audio-capture=%s"%audio_file)
       options.add_argument("--use-file-for-fake-video-capture=%s"%video_file)
       #options.add_argument(f'user-agent=Mozilla/5.0 (Gradual;E2E) Chrome/120.0.0.0') #skip check
       options.add_argument(f'user-agent=Mozilla/5.0 (Gradual;E2E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36')
       #options.add_argument("--window-size=1920,1080") -- no use
       driver = webdriver.Chrome(options=options)
       #driver = webdriver.Edge(options=options)
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
       self.driver = driver
       self.wait = wait
       self.browsers_tabs['default'] = {'tab_queue': [self.driver.current_window_handle], 'cur_tab':self.driver.current_window_handle}
       self.cur_browser = 'default'
       

       log_dir = self.base_dir + '/log'
       if not os.path.exists(log_dir):
          os.makedirs(log_dir)
       self.log = Logger(log_dir)
       self.catcher = Catcher(driver,self.log)

    def get_data(self,var_name):
       type = self.data.get(var_name,'type')
       value = self.data.get(var_name,'value')

       if type == 'file':
          return self.base_dir + '/data/' + value

       elif type == 'string':
          return value

       else:
           assert False,'type: %s not defined'%type

 
    def start_browser(self,name):
       assert name not in self.browsers_tabs.keys(),"Browser '%s' has already existed"%name
       
       cur_handles = list(self.driver.window_handles)
       window_num = len(cur_handles) + 1
       self.driver.switch_to.new_window('window')
       self.wait.until(number_of_windows_to_be(window_num))
       
       new_handle = list(set(self.driver.window_handles) - set(cur_handles))[0]
       self.browsers_tabs[name] = {'tab_queue':[new_handle],'cur_tab':new_handle}
       self.cur_browser = name
       self.logger('start browser:%s(%s)'%(name,new_handle))
             
    def switch_to_browser(self,name):
       assert name in self.browsers_tabs.keys(),"Browser '%s' not exist"%name
       self.logger('switch to browser: %s(%s)'%(name,self.browsers_tabs[name]['cur_tab']))
       self.driver.switch_to.window(self.browsers_tabs[name]['cur_tab'])
       self.cur_browser = name
 
    def open_new_tab(self):
        cur_handles = list(self.driver.window_handles)
        window_num = len(cur_handles) + 1
        self.driver.switch_to.new_window('tab')
        self.wait.until(number_of_windows_to_be(window_num))
        new_handle = list(set(self.driver.window_handles) - set(cur_handles))[0]
        self.browsers_tabs[self.cur_browser]['tab_queue'].append(new_handle)
        self.browsers_tabs[self.cur_browser]['cur_tab'] = new_handle
        self.logger('open new tab: %s in browser %s'%(new_handle,self.cur_browser))

    #case auto opening new tab after clicking a link
    def add_new_win_handle_if_exist(self):
        cur_handles = []
        for browser in self.browsers_tabs:
            cur_handles = cur_handles + self.browsers_tabs[browser]['tab_queue']
        diff = list(set(self.driver.window_handles) - set(cur_handles))
        if diff:
          new_handle = diff[0]
          self.logger('new handle found: %s'%new_handle)
          self.browsers_tabs[self.cur_browser]['tab_queue'].append(new_handle)
          self.driver.switch_to.window(new_handle)
          self.browsers_tabs[self.cur_browser]['cur_tab'] = new_handle

    def switch_to_tab(self,order):
       assert int(order) <= len(self.browsers_tabs[self.cur_browser]['tab_queue']),'tab order [%d] not exist'%order
       target_handle = self.browsers_tabs[self.cur_browser]['tab_queue'][int(order) - 1]
       self.logger('switch to tab: %s in browser %s'%(target_handle,self.cur_browser))
       self.driver.switch_to.window(target_handle)
       self.browsers_tabs[self.cur_browser]['cur_tab'] = target_handle
     
    def close_tab(self):
       target_handle = self.browsers_tabs[self.cur_browser]['cur_tab']
       self.driver.close()
       self.logger('close tab: %s in browser %s'%(target_handle,self.cur_browser))
       if len(self.browsers_tabs[self.cur_browser]['tab_queue']) > 1:
          cur_index = self.browsers_tabs[self.cur_browser]['tab_queue'].index(target_handle)
          next_index = cur_index - 1 if cur_index != 0 else 1
          next_handle = self.browsers_tabs[self.cur_browser]['tab_queue'][next_index]
          self.browsers_tabs[self.cur_browser]['tab_queue'].remove(target_handle)
          self.logger('switch to tab: %s'%next_handle)
          self.driver.switch_to.window(next_handle)
          self.browsers_tabs[self.cur_browser]['cur_tab'] = next_handle
       else:
          del self.browsers_tabs[self.cur_browser]
          
          if not self.browsers_tabs:
             self.switch_to_browser(self.browsers_tabs.keys[0])
     
    def screen_shot(self):
       ct = time.time()
       current_time = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(ct))
       current_date = time.strftime("%Y-%m-%d", time.localtime(ct))
       t_ms = (ct - int(ct)) * 1000
       pic_name = "%s_%03d.png" % (current_time,t_ms)
       pic_path = self.base_dir + '/screenshots/'+current_date+'/'
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
           self.driver.set_window_size(width=1920, height=1080)
           self.win_size = self.driver.get_window_size()

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
         self.logger("start onelogin") 
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
         #     ) # --- not works
         self.wait.until(visibility_of_element_located((By.XPATH,"//ul[@id='sidebar-menus']//div[text()='Home']")) or visibility_of_element_located((By.CSS_SELECTOR,"input[placeholder='Enter your']")),'can not see home page after one login')

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
              is_page_loading
              )
           page_loading = True
           self.logger('the page is loading')
        except TimeoutException:
            self.logger('the page is not loading')
            page_loading = False

        #wait to disappear
        if page_loading :
              self.logger('wait page loading')
              WebDriverWait(self.driver,180,0.2).until_not(
                is_page_loading,'page is still loading...'
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
    
    def click_if_exist(self,reference,fuzzy_search=True,with_offset=None):
        self.action_if_exist('click',reference,fuzzy_search,with_offset)
    
    def hover_over_if_exist(self,reference,fuzzy_search=True,with_offset=None):
        self.action_if_exist('hover_over',reference,fuzzy_search,with_offset)
    
    def action_if_exist(self,action_type,reference,fuzzy_search,with_offset):
        time.sleep(3)
        elem = self.is_present(reference=reference,fuzzy_search=fuzzy_search)
        if elem:
           self.logger("'%s' exist when %sing"%(reference,action_type))
           self.elem_action(elem,'click',with_offset)
        else:
           self.logger("'%s' not exist when %sing"%(reference,action_type))

    def hover_over_exactly_if_exist(self,reference,with_offset=None):
        self.hover_over_if_exist(reference,False,with_offset=with_offset)

    def click_exactly_if_exist(self,reference,with_offset=None):
        self.click_if_exist(reference,False,with_offset)
    
    def click_exactly(self,reference,with_offset=None):
        self.click(reference,False,with_offset=with_offset)
    
    def triple_click(self,reference,fuzzy_search=True,search_tag=None,with_offset=None):
        self.action_reference('triple_click',reference,fuzzy_search,search_tag,with_offset)
    
    def double_click(self,reference,fuzzy_search=True,search_tag=None,with_offset=None):
        self.action_reference('double_click',reference,fuzzy_search,search_tag,with_offset)

    def click(self,reference,fuzzy_search=True,search_tag=None,with_offset=None):
        self.action_reference('click',reference,fuzzy_search,search_tag,with_offset)

    def action_reference(self,action_type,reference,fuzzy_search,search_tag,with_offset):
        if fuzzy_search:
              xpath = self.get_fuzzy_xpath(reference)
        else:
              xpath = self.get_exact_xpath(reference)
        
        #self.logger('click elem by reference[%s],xpath: %s'%(reference,xpath))
        self.logger("%s elem by reference: '%s'"%(action_type,reference))
        elem = self.is_present(reference=reference,fuzzy_search=fuzzy_search,search_tag=search_tag)
        if not elem:
            #self.wait.until(visibility_of_element_located((By.XPATH, xpath)), "Can't find element '%s'"%reference)
            self.wait.until(element_to_be_clickable((By.XPATH, xpath)), "Can't find element '%s'"%reference)
            elem = self.driver.find_elements(By.XPATH,xpath)[0]

        self.elem_action(elem,action_type,with_offset)
        
        
        self.add_new_win_handle_if_exist()
    
    def hover_over(self,reference,fuzzy_search=True,search_tag=None,with_offset=None):
       self.action_reference('hover_over',reference,fuzzy_search,search_tag,with_offset)

    def click_the_middle_of_screen(self,offset="0,0"):
        size = self.win_size
        action = ActionBuilder(self.driver)
        action.pointer_action.move_to_location(int(size.get("width")/2), int(size.get("height")/2))
        action.perform()
        self.logger("middle coordinates:%d,%d"%(int(size.get("width")/2), int(size.get("height")/2)))
        offset_x,offset_y = self.parse_coordinates(offset)
        ActionChains(self.driver).move_by_offset(offset_x,offset_y).click().perform()        

    def parse_coordinates(self,input_str):
       return int(input_str.split(',')[0]),int(input_str.split(',')[1])
    
    #action_type:click,double_click,hover_over
    def elem_action(self,elem,action_type,with_offset=None):
        self.to_be_in_viewport(elem)

        if action_type == 'click':
          if with_offset:
                offset_x,offset_y = self.parse_coordinates(with_offset)
                ActionChains(self.driver).move_to_element_with_offset(elem, offset_x, offset_y).click().perform()
          else:
              elem.click()

        elif action_type == 'hover_over':
          if with_offset:
             offset_x,offset_y = self.parse_coordinates(with_offset)
             ActionChains(self.driver).move_to_element_with_offset(elem, offset_x, offset_y).perform()
          else:
            ActionChains(self.driver).move_to_element_with_offset(elem).perform()
        
        elif action_type == 'double_click':
            if with_offset:
               offset_x,offset_y = self.parse_coordinates(with_offset)
               ActionChains(self.driver).move_to_element_with_offset(elem, offset_x, offset_y).double_click().perform()
            else:
               ActionChains(self.driver).double_click(elem).perform()
        elif action_type == 'triple_click':
            if with_offset:
               offset_x,offset_y = self.parse_coordinates(with_offset)
               ActionChains(self.driver).move_to_element_with_offset(elem, offset_x, offset_y).double_click().click().perform()
            else:
               ActionChains(self.driver).double_click(elem).click(elem).perform()


        if with_offset or action_type != 'click':
           ActionBuilder(self.driver).clear_actions()

    def click_xpath(self,xpath,with_offset=None):
        self.action_xpath('click',xpath,with_offset)
    
    def hover_over_xpath(self,xpath,with_offset=None):
        self.action_xpath('hover_over',xpath,with_offset)

    def action_xpath(self,action_type,xpath,with_offset):
        self.logger('%s elem by xpath: %s'%(action_type,xpath))
        elem = self.is_present(xpath=xpath)
        if not elem:
           self.wait.until(visibility_of_element_located((By.XPATH, xpath)), "Can't find element by xpath '%s'"%xpath)
           elem = self.driver.find_elements(By.XPATH,xpath)[0]
        
        self.elem_action(elem,action_type,with_offset)

        self.add_new_win_handle_if_exist()

    def click_css_selector(self,css_selector,with_offset=None):
        self.action_css_selector('click',css_selector,with_offset)
    
    def double_click_css_selector(self,css_selector,with_offset=None):
        self.action_css_selector('double_click',css_selector,with_offset)
    def action_css_selector(self,action_type,css_selector,with_offset):
        self.logger('click elem by css selector: %s'%css_selector)
        elem = self.is_present(css_selector=css_selector)
        if not elem:
           self.wait.until(visibility_of_element_located((By.CSS_SELECTOR, css_selector)), "Can't find element by css selector '%s'"%css_selector)
           elem = self.driver.find_elements(By.CSS_SELECTOR,css_selector)[0]

        self.elem_action(elem,action_type,with_offset)
        self.add_new_win_handle_if_exist()

    def is_present(self,reference=None,fuzzy_search=True,xpath=None,css_selector=None,search_tag=None):
        search_info = self.get_searching_elem_info(reference,fuzzy_search,xpath,css_selector,search_tag)
        all_elements_matched = self.driver.find_elements(search_info[0],search_info[1])
        all_elements_matched_visible = [elem for elem in all_elements_matched if elem.is_displayed()]
        all_elements_matched_in_viewport = [elem for elem in all_elements_matched_visible if self.is_in_viewport(elem)]

        self.logger('%d elements found in viewport'%len(all_elements_matched_in_viewport))
        for elem in all_elements_matched_in_viewport:
            self.logger('element selected:%s'%self.get_elem_rect(elem))
             

        self.logger('%d visible elements found'%len(all_elements_matched_visible))    
        for elem in all_elements_matched_visible:
            self.logger('element selected:%s'%self.get_elem_rect(elem))
        
        
        if len(all_elements_matched_in_viewport)>0 :
           return all_elements_matched_in_viewport[-1]

        elif len(all_elements_matched_visible)>0 :
           return all_elements_matched_visible[-1]
        
    def wait_until_page_contains(self,reference=None,xpath=None,css_selector=None,tag_name=None,tm=180):
        self.logger("waiting for: '%s'"%reference)
        search_info = self.get_searching_elem_info(reference,True,xpath,css_selector,tag_name)
        message = self.gen_message_error(search_info[2],search_info[1],reference)
        wait = WebDriverWait(self.driver,tm,0.2)
        #self.logger("wait_until_page_contains:%s,%s"%(search_info[0],search_info[1]))
        wait.until(visibility_of_element_located((search_info[0], search_info[1])), message)

        return self.driver.find_element(search_info[0],search_info[1])
    
    def wait_until_page_contains_exactly(self,reference=None,xpath=None,css_selector=None,tag_name=None,tm=180):
        self.logger("waiting for: '%s'"%reference)
        search_info = self.get_searching_elem_info(reference,False,xpath,css_selector,tag_name)
        message = self.gen_message_error(search_info[2],search_info[1],reference)
        wait = WebDriverWait(self.driver,tm,0.2)
        #self.logger("wait_until_page_contains:%s,%s"%(search_info[0],search_info[1]))
        wait.until(visibility_of_element_located((search_info[0], search_info[1])), message)
     
    def check_that_page_contains(self,reference,tm=30):
        try:
           self.wait_until_page_contains(reference,tm=30)
           self.logger("the page contains '%s'"%reference)
        except TimeoutException:
           self.logger("the page does not contain '%s'"%reference)
    
    def check_that_page_contains_exactly(reference,tm=30):
        self.wait_until_page_contains(reference,False,tm=30)

    def does_page_contain(self,reference):
        return self.is_present(reference,True)

    def does_page_contain_xpath(self,xpath):
        return self.is_present(xpath=xpath)
    
    def does_page_contain_css_selector(self,css_selector):
        return self.is_present(css_selector = css_selector)

    def does_page_contain_exactly(self,reference):
        return self.is_present(reference,False)
             
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
    
    def scroll_down_until_page_contains(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,True,'down',up_to_times,on,step)

    def scroll_down_until_page_contains_exactly(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,False,'down',up_to_times,on,step)

    def scroll_up_until_page_contains(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,True,'up',up_to_times,on,step) 
    
    def scroll_up_until_page_contains_exactly(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,False,'up',up_to_times,on,step)

    def scroll_left_until_page_contains(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,True,'left',up_to_times,on,step) 
   
    def scroll_left_until_page_contains_exactly(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,False,'left',up_to_times,on,step)

    def scroll_right_until_page_contains(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,True,'right',up_to_times,on,step) 
    
    def scroll_right_until_page_contains_exactly(self,reference,up_to_times=100,on=None,step=2):
        self.scroll_until_page_contains(reference,False,'right',up_to_times,on,step)

    def scroll_until_page_contains(self,reference,fuzzy_search,direct,up_to_times,on,step):
        times=0
        while not self.is_present(reference,fuzzy_search):
           if direct == 'down':
             self.scroll_down(on,step)
           elif direct == 'up':
             self.scroll_up(on,step)
           elif direct == 'left':
             self.scroll_left(on,step)
           else:
             self.scroll_right(on,step)
           
           times += 1
           if times > up_to_times:
              break
           time.sleep(1)
         
        elem = self.is_present(reference,fuzzy_search)    
        if elem :
           self.to_be_in_viewport(elem)
        else:
           assert False,"Can't find elem '%s' after scroll"%reference
    #to fix
    def to_be_in_viewport_center(self,elem):
       rect = self.get_elem_rect(elem)
       y_offset = int(rect['y'] + rect['height']/2 - self.win_size['height']/2)
       if y_offset > self.win_size['height']/50:
          y_offset = int(self.win_size['height'] - rect['height']/2)
          self.logger('try to scroll element in viewport center')
          scroll_origin = ScrollOrigin.from_element(elem)
          ActionChains(self.driver)\
              .scroll_to_element(elem)\
              .scroll_from_origin(scroll_origin,0,y_offset)\
              .perform()

    def to_be_in_viewport(self,elem):
        if not self.is_in_viewport(elem):
           self.logger('scroll element in viewport')
           ActionChains(self.driver)\
              .scroll_to_element(elem)\
              .perform()

    #step=2,means scroll by the 1/2 of screen
    def scroll_down(self,on=None,step=2):
        size = self.win_size
        self.scroll(0,int(size.get("height")/step),on)
    
    def scroll_up(self,on=None,step=2):
        size = self.win_size
        self.scroll(0,0 - int(size.get("height")/step),on)

    def scroll_right(self,on=None,step=2):
        size = self.win_size
        self.scroll(int(size.get("width")/step),0,on)

    def scroll_left(self,on=None,step=2):
        size = self.win_size
        self.scroll(0 - int(size.get("width")/step),0,on)

    def scroll(self,x,y,on):
        action = ActionChains(self.driver)
        if on:
          on_elem = self.wait_until_page_contains(on,tm=30)
          self.logger('start scroll...')
          scroll_origin = ScrollOrigin.from_element(on_elem)
          action.scroll_from_origin(scroll_origin, x, y).perform()
        else:
          action.scroll_by_amount(x,y).perform()

    def open_gmail(self):
        #gmail_url = self.get_data('gmail url')
        self.open_url(self.get_data('gmail url'))
        self.type('testaccount@gradual.com','identifier')
        self.click('Next')
        self.type('Gradual@001','Passwd')
        time.sleep(2)
        self.click('passwordNext')
        code = self.gen_pin_with_google_auth_qrcode(self.get_data('qrCode-new'))
        self.type(code,'totpPin')
        time.sleep(2)
        self.click('totpNext')
        print(self.driver.window_handles)
        cur_handles = self.driver.window_handles
        origin_win_handle = self.driver.current_window_handle
        self.wait_until_page_contains('Search mail')
        #check if popup new window
        new_handle = list(set(self.driver.window_handles) - set(cur_handles))
        if new_handle:
             self.logger('%d window found'%len(new_handle))
             self.driver.switch_to.window(new_handle[0])
             size = self.driver.execute_script('return {width: window.innerWidth, height: window.innerHeight}')
             self.logger('first window: size:%s,handle:%s'%(size,new_handle[0]))
             #self.driver.close() selenium.common.exceptions.WebDriverException: Message: unknown error: failed to close window in 20 seconds
             action = ActionBuilder(self.driver)
             action.pointer_action.move_to_location(420,500 )
             action.pointer_action.pointer_down(MouseButton.LEFT)
             action.pointer_action.pointer_up(MouseButton.LEFT)
             action.perform()
             self.driver.switch_to.window(origin_win_handle)
             

    def search_in_email(self,content):
        tm = TimeOut(60*15)
        lst_item = content.lower().split('+')
        while not tm.is_timeout():

           #from main page
           self.click_exactly('Mail') 
           #type content
           self.type(content,'Search mail')
           self.type(Keys.ENTER,'Search mail')
           #open latest mail
           self.click_xpath("(//tbody/tr[@class='zA zE' or @class='zA yO'][1]/td[4])[2]")
           self.click_if_exist('Show images')
           print(self.driver.window_handles)
           self.scroll_down_until_page_contains_exactly('Forward',on=':3')
           self.click_if_exist('Show images')
           self.click_if_exist('Show trimmed content') # '...'
           self.click_if_exist('Show images')
           self.scroll_down_until_page_contains_exactly('Forward',on=':3')
           #check cur page content
           email_title = self.grab_content_from('.hP')
           email_content_total = self.grab_content_from("[role='listitem']:nth-last-child(1)")
           cur_content = email_title.lower() + '\n' + email_content_total.lower()
           self.logger("cur email:%s"%cur_content)
           find_flag = True
           for item in lst_item:
              if item not in cur_content:
                 find_flag = False
                 break
           
           if not find_flag:
              time.sleep(10)
           else:
              return True

        assert False, "Not recv mail which contains '%s'"%content
           
    def gen_pin_with_google_auth_qrcode(self,qrcode_file_path):
        
        qrcode_image = cv2.imread(qrcode_file_path)
        qrCodeDetector = cv2.QRCodeDetector()
        data, bbox, straight_qrcode = qrCodeDetector.detectAndDecode(qrcode_image)
        #data = otpauth://totp/Google%3Atestaccount%40gradual.com?secret=xwu3a3t22iro37nlqtwanq4mohywsrau&issuer=Google
        secret = data.split('secret=')[1].split('&issuer')[0]
        totp = pyotp.TOTP(secret)
        return totp.now()
