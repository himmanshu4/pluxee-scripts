import os
import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load Environment Variables
load_dotenv(".envvars")

def initialize_chrome_driver():
    """
    Initializes the Selenium Chrome driver using your exact authenticated profile.
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    profile_name = os.getenv("PROFILE_NAME")

    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH is not set in the environment variables.")
    if not profile_name:
        raise ValueError("PROFILE_NAME is not set in the environment variables.")

    print(f"Initializing Chrome with profile: {profile_name} at {chrome_profile_path}")

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_path}")
    options.add_argument(f"--profile-directory={profile_name}")
    options.add_argument("--disable-extensions")

    service = Service(
        service_args=["--verbose"],
        log_output="chromedriver.log"
    )

    driver = webdriver.Chrome(options=options, service=service)
    return driver

def automate_pluxee_uploads(api_endpoint, target_directory):
    """
    Fetches receipt data, fills the portal, waits for manual submission, and deletes the file.
    """
    print("Fetching receipt data from the local API...")
    try:
        response = requests.get(f"{api_endpoint}?directory={target_directory}")
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
    wait = WebDriverWait(driver, 10)

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
                    # Physically removes the file from the operating system
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
    # Define the location of your running Flask API
    LOCAL_API_URL = "http://127.0.0.1:5000/extract"
    
    # Securely load the directory path from your environment variables
    RECEIPTS_DIRECTORY = os.getenv("RECEIPTS_DIRECTORY")
    
    # Safety Check
    if not RECEIPTS_DIRECTORY:
        raise ValueError("RECEIPTS_DIRECTORY is not set in the environment variables.")
    
    print(f"Targeting receipts directory: {RECEIPTS_DIRECTORY}")
    
    # Execute the automation
    automate_pluxee_uploads(LOCAL_API_URL, RECEIPTS_DIRECTORY)