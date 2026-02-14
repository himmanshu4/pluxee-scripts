import os
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Robust Environment Loading
script_dir = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(os.path.dirname(script_dir), ".envvars")
print(f"Loading configuration from: {env_file_path}")
load_dotenv(env_file_path)

def initialize_chrome_driver():
    """
    Initializes the Selenium Chrome driver strictly for Windows environments,
    utilizing memory piping and anti-renderer-crash flags.
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    profile_name = os.getenv("PROFILE_NAME")

    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH is not set in the environment variables.")
    if not profile_name:
        raise ValueError("PROFILE_NAME is not set in the environment variables.")

    print(f"Initializing Chrome with profile: {profile_name} at {chrome_profile_path}")

    options = Options()
    
    # Profile Binding
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--disable-extensions")
    
    # Standard Windows Communication Flag
    options.add_argument("--remote-allow-origins=*")
    
    # --- ADDED: The Ultimate DevTools Bypasses & Anti-Crash Flags ---
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-pipe") # Bypasses the file system entirely
    options.add_argument("--disable-gpu") # Disables hardware acceleration preventing the 60s timeout
    options.add_argument("--disable-features=RendererCodeIntegrity") # Stops Windows from blocking the renderer
    # ----------------------------------------------------------------

    # Automated Driver Fetching via webdriver-manager
    service = Service(
        executable_path=ChromeDriverManager().install(),
        log_output="chromedriver.log"
    )

    driver = webdriver.Chrome(options=options, service=service)
    
    # --- ADDED: Tell Python to load pages faster without waiting for heavy background scripts ---
    driver.page_load_strategy = 'eager' 
    
    return driver

def automate_pluxee_uploads(api_endpoint, target_directory):
    """
    Fetches receipt data, fills the portal, waits for manual submission, and deletes the file.
    """
    print("Fetching receipt data from the local API...")
    try:
        # Safe URL Encoding via the 'params' argument
        response = requests.get(api_endpoint, params={"directory": target_directory})
        response.raise_for_status()
        receipt_data = response.json().get("receipts", [])
    except Exception as e:
        print(f"Failed to fetch data from API: {e}")
        return

    if not receipt_data:
        print("No receipts found or returned by the API.")
        return

    pluxee_url = os.getenv("PLUXEE_URL")
    if not pluxee_url:
        raise ValueError("PLUXEE_URL is not set in the environment variables.")

    driver = initialize_chrome_driver()
    wait = WebDriverWait(driver, 300)

    try:
        for index, receipt in enumerate(receipt_data, start=1):
            amount = receipt.get("amount")
            file_path = receipt.get("exact_file_path")
            filename = os.path.basename(file_path)

            if amount in ("Not Found", "Error", "N/A", ""):
                print(f"[{index}/{len(receipt_data)}] Skipping {filename} - Invalid amount.")
                continue

            print(f"\n--- Processing Receipt {index} of {len(receipt_data)} ---")
            print(f"File: {filename} | Amount: ₹{amount}")

            # Navigate to the portal
            driver.get(pluxee_url)

            # Wait for the amount input field and populate it
            amount_input = wait.until(EC.visibility_of_element_located((By.ID, "claim-amount")))
            amount_input.clear()
            amount_input.send_keys(str(amount))

            # Locate the hidden file input and inject the exact path
            file_input = driver.find_element(By.ID, "import-img")
            file_input.send_keys(file_path)
            
            # --- Human-in-the-Loop Pause & Safe Deletion ---
            print("\n*** ACTION REQUIRED ***")
            print("1. Please review the browser window.")
            print("2. Manually click the 'Submit' button on the Pluxee portal.")
            print("3. Wait for the success confirmation on the portal.")
            
            user_confirmation = input("\n4. Type 'y' and press ENTER if submitted successfully (this will DELETE the receipt), or just press ENTER to skip: ")
            
            if user_confirmation.strip().lower() == 'y':
                try:
                    os.remove(file_path)
                    print(f"Success: Permanently deleted '{filename}'.")
                except Exception as e:
                    print(f"Warning: Could not delete '{filename}'. Error: {e}")
            else:
                print(f"Notice: Skipped deletion for '{filename}'. Moving to the next file.")

    finally:
        print("\nAll receipts processed. Closing the browser gracefully.")
        driver.quit()

if __name__ == "__main__":
    LOCAL_API_URL = "http://127.0.0.1:5000/extract"
    
    RECEIPTS_DIRECTORY = os.getenv("RECEIPTS_DIRECTORY")
    
    if not RECEIPTS_DIRECTORY:
        raise ValueError("RECEIPTS_DIRECTORY is not set in the environment variables.")
    
    print(f"Targeting receipts directory: {RECEIPTS_DIRECTORY}")
    
    automate_pluxee_uploads(LOCAL_API_URL, RECEIPTS_DIRECTORY)