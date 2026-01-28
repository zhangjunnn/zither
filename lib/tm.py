import time

class TimeOut:

    def __init__(self,timeout=30):

       self.timeout = timeout
       self.start_time = time.time()
    def is_timeout(self):
       
       if time.time() - self.start_time > self.timeout :
          return True
       else:
          return False

    
