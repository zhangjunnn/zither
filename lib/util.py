
class Util:
   
   def grab_content_from(self,selector):
      return self.driver.execute_script("""
        var target=null;
        var elem_num=0;
        var selector_str="%s";
       if(selector_str.startsWith("//") || selector_str.startsWith("(//")) {
        target = document.evaluate(selector_str, document).iterateNext();
       }
       else { 
       target = document.querySelector(selector_str);
       }
       if (target != null) {
         var innerText = target.innerText
         if (innerText != undefined) {
           innerText = innerText.replaceAll('&nbsp;', ' ');
           innerText = innerText.replace(/\\n/g, "");
        }
        return innerText
       }
       return "elem not exist"
       """%selector)
   
   def is_in_viewport(self,element):
     return self.driver.execute_script("""
          const viewWidth = window.innerWidth || document.documentElement.clientWidth;
          const viewHeight = window.innerHeight || document.documentElement.clientHeight;
          const { top, right, bottom, left } = arguments[0].getBoundingClientRect();

      return top >= 0 && left >= 0 && right <= viewWidth && bottom <= viewHeight;
     """,element)

   def get_elem_rect(self,element):
     return self.driver.execute_script("""
          var rect =  arguments[0].getBoundingClientRect();
          return {
                  x: rect['left'],
                  y: rect['top'],
                  width:  rect['width'],
                  height: rect['height']
                 }

          """,element)
