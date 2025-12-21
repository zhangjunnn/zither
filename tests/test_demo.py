import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class TestBaidu:
    """百度搜索测试用例"""

    def setup_method(self):
        """每个测试方法前执行"""
        # 创建浏览器驱动
        #service = Service(executable_path="/usr/local/share/chromedriver-linux64/chromedriver")
        #options = Options()
        #options.add_argument("--start-maximized")
        #self.driver = webdriver.Chrome(service=service, options=options)  # 如果驱动在PATH中，可以直接这样写
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)   # 隐式等待10秒
        self.driver.maximize_window()     # 最大化窗口

    def teardown_method(self):
        """每个测试方法后执行"""
        # 关闭浏览器
        self.driver.quit()

    def test_baidu_search(self):
        """测试百度搜索功能"""
        # 打开百度
        self.driver.get("https://www.baidu.com")

        # 定位搜索框并输入关键词
        search_box = self.driver.find_element(By.ID, "kw")
        search_box.send_keys("自动化测试")

        # 定位搜索按钮并点击
        search_btn = self.driver.find_element(By.ID, "su")
        search_btn.click()

        # 验证搜索结果
        time.sleep(2)  # 等待页面加载
        assert"自动化测试"in self.driver.title
        print("测试通过！")
if __name__ == "__main__":
    pytest.main(["-v", "test_demo.py"])
