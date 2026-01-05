import time
import datetime
from fo import fileOperator
class Logger:
   def __init__(self,log_dir):
      self.log_dir = log_dir

   def logger(self,msg,screenPrint=False):
       current_date = time.strftime("%Y-%m-%d", time.localtime(time.time()))
       log_file_name = current_date + '.log'

       fo = fileOperator(self.log_dir+'/'+log_file_name)
       if screenPrint:
          print(str(datetime.datetime.now())+' '+str(msg))
       fo.fwrite(str(datetime.datetime.now())+' '+str(msg)+'\n','a')
