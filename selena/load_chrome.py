import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Read environment variables
chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
profile_name = os.getenv("PROFILE_NAME")

if not chrome_profile_path:
    raise ValueError("CHROME_PROFILE_PATH is not set")
else:
    print(f"Using Chrome profile path: {chrome_profile_path}")

if not profile_name:
    raise ValueError("PROFILE_NAME is not set")
else:
    print(f"Using Chrome profile name: {profile_name}")

options = Options()
# options.add_argument("--user-data-dir=/tmp/selenium-profile")

options.add_argument(f"--user-data-dir={chrome_profile_path}")
options.add_argument(f"--profile-directory={profile_name}")
options.add_argument("--disable-extensions")

from selenium.webdriver.chrome.service import Service
from selenium import webdriver

service = Service(
    service_args=["--verbose"],
    log_output="chromedriver.log"
)


driver = webdriver.Chrome(options=options, service=service)
print("Chrome driver initialized with specified profile.")
driver.get("https://www.google.com")
