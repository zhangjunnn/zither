# -*- coding: utf-8 -*-
import time
class Catcher:
  def __init__(self,driver,logger):
     self.driver = driver
     self.log = logger
  def logger(self,msg):
     self.log.logger(msg)
  
  def start(self):
     self.catch_task()

  def prepare_to_catch(self):
        msg_box = self.driver.execute_script("""
           return sessionStorage.getItem('message_box_ss')
        """)
        
        if '#!catching!#' in msg_box:
           
           #check catch task
           if(int(time.time()*1000) - int(msg_box.split('<|>')[1]) > 4000):
             self.logger("Catcher sees to sleep,so start another catcher.")
             self.catch_task(self.driver)
        else:
           self.logger('seems that catch task is not working,start...')
           self.catch_task(self.driver)

  def fetch_content_catched(self): 
        msg_box = self.driver.execute_script("""
           return sessionStorage.getItem('message_box_ss')
        """)
        content=""
        if '#!catching!#' in msg_box:
           
           content = msg_box.split('<|>')[3]
           #check catch task
           if(int(time.time()*1000) - int(msg_box.split('<|>')[1]) > 4000):
             self.logger("Catcher sees to sleep,so start another catcher.")
             self.catch_task(self.driver)
        else:
           self.logger('seems that catch task is not working,start...')
           self.catch_task(self.driver)
           
        return content

  def catch_task(self):

    js_code= """
         function isInViePortOfOne(el){
           if(el == null) return false;
           var viewPortHeight = window.innerHeight || document.documentElement.clientHeight||document.body.clientHeight
           var offsetTop = el.offsetTop;
           var scollTop = document.documentElement.scrollTop
           var top = offsetTop - scollTop;
           //return top <= viewPortHeight && top >= 0;
           return top <= viewPortHeight && top > 0; //for me
         }
        function isContain(dom) {
          var viewHeight = window.innerHeight || document.documentElement.clientHeight;
          var viewWidth = window.innerWidth || document.documentElement.clientWidth;
          // 当滚动条滚动时，top, left, bottom, right时刻会发生改变。
          var rect=dom.getBoundingClientRect();
          return (rect.top >= 0 && rect.left >= 0 && rect.right <= viewWidth && rect.bottom <= viewHeight);
        }

        function multiElemHandle(elems){
         var i;
         for(i = 0; i < elems.length; i++)
           if(elems[i].innerText.length>0 && ! arr_messages.includes(elems[i].innerText)) arr_messages.push(elems[i].innerText);
        }

        function find_expect_front(elems){
        var i;
        for(i = 0; i < elems.length; i++)
        if (elems[i].childElementCount == 3 && isContain(elems[i]) ) return true;
 
        return false;
        }

       function find_expect_dashboard(elems){
        var i;
        for(i = 0; i < elems.length; i++)
        if (elems[i].childElementCount == 4 && isContain(elems[i]) ) return true;

        return false;
       }
       //other task:hide profile popup
       function Sub_loop(){
         setTimeout(function(){
         document.querySelector("#popup-root>div").style.display='none';
         if(sub_loop_to_run) Sub_loop();
       },100);
       }
      //main task
      function Loop(){
         //run sub loop
         var run_flag = sessionStorage.getItem('hide_profile_popup_ss');
         if(run_flag) {
            if(!sub_loop_to_run) Sub_loop();sub_loop_start=true;
          }else sub_loop_to_run=false;
     
         //clear
         var clear_flag = sessionStorage.getItem('message_catched_clr_ss');
         if (clear_flag !=null){
        //if( clear_flag != '' ) sessionStorage.setItem('message_catched_clr_ss','');//clear cache first,then hanle continuiously.
        if( clear_flag == 'clear all' ) {
        arr_messages.splice(0,arr_messages.length);
        dict_message_fetched.clear();
        sessionStorage.setItem('message_catched_clr_ss',0);
        }
        else {
             
             //clear message which has been catched 
             //clear signal given
             //no clear signal given for over 600 seconds(300 cycles)
            dict_message_fetched.forEach(function(value, key) {
            if (new Date().getTime() - key >= 300000 || key <= parseInt(clear_flag)) { 
                 var index = arr_messages.indexOf(value);
                 if (index >=0) arr_messages.splice(index,1);
                 
                 dict_message_fetched.delete(key);
            }
            
          });
        }
     }
     //---- start catch ---
     //front
     target = document.querySelectorAll(".ant-message-notice-content");
     if (target.length>0 ) multiElemHandle(target);

     target = document.querySelectorAll(".Toastify__toast-body");
     if (target.length>0 ) multiElemHandle(target);
     //meeting room ,broadcast
     target = document.querySelector(".gradual-notification-notice-content");
     if (target != null && ! arr_messages.includes(target.innerText)) arr_messages.push(target.innerText);

     target = document.querySelector("#video-chat-main-area [class*='-NotificationContainer ']");
     if (target != null && ! arr_messages.includes(target.innerText)) arr_messages.push(target.innerText);

     target = document.querySelector("[class*='-MessageContentContainer ']");
     if (target != null && ! arr_messages.includes(target.innerText)) arr_messages.push(target.innerText);

     target = document.querySelector(".popup-content");
     if (target != null && ! arr_messages.includes(target.innerText)) arr_messages.push(target.innerText);

     //register dialog
     target = document.querySelector(".rc-dialog-content div[class*='-ImageBox ']")
     if (target != null ){
        target = document.querySelector(".rc-dialog-content")
        expect_msg = target.innerText;
        if(! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     }
     //dashboard
     target = document.querySelectorAll(".ant-notification-notice-message");
     if (target.length>0 ) multiElemHandle(target);
     target = document.querySelectorAll(".ant-notification-notice-description");
     if (target.length>0 ) multiElemHandle(target);
     //page load
     expect_msg = 'page is loading'
     if(arr_messages.includes(expect_msg)) arr_messages.splice(arr_messages.indexOf(expect_msg),1);
     
     target = document.querySelector(".nprogress-busy");
     if (target != null) arr_messages.push(expect_msg);
     //#front
     target = document.querySelectorAll(".css-0");
     if (target.length > 0 && find_expect_front(target) && ! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     //#vm-player loading
     target_vm_player = document.querySelector("vm-player")
     if (target_vm_player){
      target = document.querySelector("vm-player vm-ui vm-loading-screen");
      if (target && !target.shadowRoot.querySelector(".inactive") && ! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     }
     //#dashboard
     target = document.querySelectorAll(".ant-spin-dot-spin");
     if (target.length > 0 && find_expect_dashboard(target) && ! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     
     target = document.querySelectorAll(".ant-btn-loading-icon");
     if (target.length > 0 && find_expect_dashboard(target) && ! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     
    //segment
    target = document.querySelectorAll("title#spinner-1");
     if (target.length > 0 && find_expect_dashboard(target) && ! arr_messages.includes(expect_msg)) arr_messages.push(expect_msg);
     
      //photo uploading
      target = document.querySelector(".ant-modal-content")
      if (target != null && target.innerText.indexOf('Add Photos')>=0 && ! arr_messages.includes(target.innerText)) arr_messages.push(target.innerText);
      //---- set value ---
      expect_msg = sessionStorage.getItem('message_expected_ss');
      if(expect_msg !=null && expect_msg.length>0){
          last_expected_msg = expect_msg;
          var timestamp = new Date().getTime() - interval_time;
          for ( var i = 0; i < arr_messages.length; i++) {
              if(arr_messages[i].indexOf(expect_msg)>=0) {
                  dict_message_fetched.set(timestamp - i,arr_messages[i]);
                  sessionStorage.setItem('message_expected_ss','');
               }
          }
      }
      sessionStorage.setItem('message_box_ss','#!catching!#'+'<|>'+ new Date().getTime()+'<|>'+ new Date().toLocaleTimeString()+'<|>'+arr_messages.join('#|#')+'<|>last expect message:'+last_expected_msg);
     //console.log(sessionStorage.getItem('message_box_ss'));
     //check the item list name and get the item count
     var targets = document.querySelectorAll("div[class*='-GridCardsList'],[class*='-ListContainer'],.ant-list-items,[class*='ForumPostsContainer']");
     var item_list_len=-1;
     if (targets.length > 0){
         target = targets[0];
         if(targets.length > 1) target = targets[targets.length-1];
         var item_list_len = target.childElementCount;
      } 
      sessionStorage.setItem('item_list_len_ss',item_list_len);
      //get the page height
    sessionStorage.setItem('de_scrollTop_ss',document.documentElement.scrollTop);
     //hide the beacon
      var target = document.getElementById("beacon-container")
     if (target != null && target.style.display != 'none') target.style.display='none'
      //remove the chat message
      target = document.querySelector("#hubspot-messages-iframe-container")
      if (target != null) target.remove();
      //remove the chat message
      target = document.querySelector(".intercom-lightweight-app-launcher")
      if (target != null) target.remove();
      target = document.querySelector(".intercom-app")
      if (target != null) target.remove();
      //cancel the low-performance switch prompt
      target = document.evaluate("//span[text()='Switch']/../../preceding-sibling::div/button", document).iterateNext();
      //target = document.evaluate("//span[text()='Switch']", document).iterateNext();
      if (target != null) target.click();
      
      //target = document.evaluate("//*[text()='Allow Access']",document).iterateNext();
      //if (target != null) target.click();
  
     //wait and run next loop
     if (loop_count <= up_to){
             setTimeout(function(){
              Loop();
             },interval_time);
      }
     loop_count = loop_count +1;
       }
  
      var content_catched='';
      var arr_messages = [];
      var dict_message_fetched = new Map();
      var loop_count = 0;
      var interval_time = 1200;
      var duration = 4800000;
      var up_to = parseInt(duration / interval_time);
      var expect_msg;
      var last_expected_msg='';
      const callback = arguments[arguments.length - 1];
      Loop();
      callback();
      """
    self.driver.execute_async_script(js_code)
