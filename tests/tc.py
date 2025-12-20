from selenium import webdriver


driver = webdriver.Chrome()
try:
    print('driver started')
    driver.get('https://scale.uat.gradual.dev/')
except Exception as err:
    print(err)
finally: 
    driver.close()
