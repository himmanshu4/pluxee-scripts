from dotenv import load_dotenv
load_dotenv("../.envvars")
from load_chrome import driver
from selenium.webdriver.common.by import By
import json
import pdb
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)

pluxee_url = os.getenv("PLUXEE_URL")

driver.get(pluxee_url)
# pdb.set_trace()

title = driver.title
wait.until(EC.visibility_of_element_located((By.ID, "claim-amount")))
driver.implicitly_wait(0.5)

text_box = driver.find_element(by=By.ID, value="claim-amount")
text_box.send_keys("100")
file_input = driver.find_element(By.ID, "import-img")
# file_button = driver.find_element(by=By.CLASS_NAME, value="upload-btn")
file_input.send_keys("/home/himanshu/Downloads/AUTO_RECEIPT_RD17671637419101193.pdf")
pdb.set_trace()
# file_button.click()
# submit_button.click()

message = driver.find_element(by=By.ID, value="message")
text = message.text

# driver.quit()
import time
time.sleep(5)