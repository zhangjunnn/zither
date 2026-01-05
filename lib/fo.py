class fileOperator():
    #t:1 is read(),2 is readline(),other is readlines()
    def __init__(self,fpath):
       self.fpath = fpath
    def fread(self,m='r',t=1):
        with open(self.fpath, m,encoding= 'utf8') as f:  
            if t==1:
               return f.read()
            if t==2: 
               return f.readline()
            else:  
               return f.readlines()
                      
    #t:1 is write(),other is writelines()
    def fwrite(self,content=None,m='a',t=1):
       if not None:
          #print('content'+content)
          with open(self.fpath, m,encoding= 'utf8') as f:
            if t==1: 
                f.write(content)
            else:
                f.writelines(content)
