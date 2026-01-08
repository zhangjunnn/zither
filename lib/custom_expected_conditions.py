
def is_page_loading(driver):
       return driver.execute_script("""
               function isContain(dom) {
                    var viewHeight = window.innerHeight || document.documentElement.clientHeight;
                    var viewWidth = window.innerWidth || document.documentElement.clientWidth;
                    // 当滚动条滚动时，top, left, bottom, right时刻会发生改变。
                    var rect=dom.getBoundingClientRect();
                    return (rect.top >= 0 && rect.left >= 0 && rect.right <= viewWidth && rect.bottom <= viewHeight);
               }
               function find_expect_front(elems){
                     var i;
                     for(i = 0; i < elems.length; i++)
                     if (elems[i].childElementCount == 3 && isContain(elems[i]) ) return true;
 
                     return false;
               }
               var target = document.querySelector(".nprogress-busy");
               if (target) return true;
               else
                   target = document.querySelectorAll(".css-0");
                   if (target.length > 0 && find_expect_front(target)) return true;

       return false;

       """)

