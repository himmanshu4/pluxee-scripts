from enum import Enum
import os
from time import sleep

import pdfplumber
from load_chrome import driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pathlib import Path
from pprint import pprint
import re


class Receipt:
    def __init__(self, amount, path, source=None, destination=None, date=None):
        self.amount = amount
        self.path = path
        self.source = source
        self.destination = destination
        self.date = date

    def __repr__(self):
        return f"amount={self.amount}, path='{self.path}', source='{self.source}', destination='{self.destination}', date='{self.date}')"

    def __hash__(self):
        return hash(self.path)


class ReceiptType(Enum):
    Rapido = "Rapido"


"""Manager class to handle receipt parsing and storage.
Currently supports Rapido receipts, but can be extended to other types.
initialization requires the directory path where receipts are stored, and it will automatically parse all PDF receipts in that directory."""


class ReceiptManager:
    def __init__(self, receipt_dir):
        self.receipts = dict[str, ReceiptWithChrome]()
        if not isinstance(receipt_dir, Path):
            receipt_dir = Path(receipt_dir)
        self.parse_directory(receipt_dir)

    def receipt_type_to_parser(self, receipt_type):
        # Add more receipt types and their corresponding parsing functions as needed.
        return {
            ReceiptType.Rapido: self.parseRapidoReceipt,
        }[receipt_type]

    def receipt_type(self, path: Path):
        return ReceiptType.Rapido

    def parse_directory(self, receipt_dir):
        # Logic to parse the directory and extract receipt information
        for p in Path(receipt_dir).glob("*.pdf"):
            receipt_type = self.receipt_type(p)
            parser = self.receipt_type_to_parser(receipt_type)
            receipt = parser(p)
            if receipt is not None:
                self.receipts[receipt.path] = receipt

    def parseRapidoReceipt(self, path: Path):
        # Logic to parse a Rapido receipt and extract information
        assert path.suffix == ".pdf", "Expected a PDF file"

        amount = None
        date = None
        date = None
        source = None
        destination = None

        try:
            with pdfplumber.open(path) as pdf:
                document_text = ""
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        document_text += extracted + "\n"
                
                # forbidden_phrases = ["421203"]
                # if any(phrase in document_text for phrase in forbidden_phrases):
                #     print(f"Skipping {path.name} due to presence of forbidden phrases.")
                #     return None

                # Extract Amount
                amount_match = re.search(
                    r"Selected Price\D*(\d+(?:\.\d+)?)",
                    document_text,
                    re.IGNORECASE,
                )
                if amount_match:
                    amount = amount_match.group(1)

                # Extract Date, Source, and Destination
                address_pattern = r"([A-Z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4},\s*\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+(.*?\d{6}(?:,\s*India)?)\s+(.*?\d{6}(?:,\s*India)?)\s+This document is issued"
                # Extract Date, Source, and Destination
                address_pattern = r"([A-Z]{3,9}\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4},\s*\d{1,2}:\d{2}\s*(?:AM|PM)?)\s+(.*?\d{6}(?:,\s*India)?)\s+(.*?\d{6}(?:,\s*India)?)\s+This document is issued"
                address_match = re.search(
                    address_pattern, document_text, re.IGNORECASE | re.DOTALL
                )

                if address_match:
                    date = address_match.group(1).replace("\n", " ").strip()
                    source = address_match.group(2).replace("\n", " ").strip()
                    destination = address_match.group(3).replace("\n", " ").strip()
                    date = address_match.group(1).replace("\n", " ").strip()
                    source = address_match.group(2).replace("\n", " ").strip()
                    destination = address_match.group(3).replace("\n", " ").strip()

                    # Clean "Selected Price..." from the source address
                    cleanup_regex = r"Selected Price\s*[^\w\s]*\s*\d+(?:\.\d+)?\s*"
                    source = re.sub(
                        cleanup_regex, "", source, flags=re.IGNORECASE
                    ).strip()

        except Exception as execution_error:
            amount = None
            source = f"File reading error: {execution_error}"
        return ReceiptWithChrome(
            amount=amount,
            path=str(path),
            source=source,
            destination=destination,
            date=date,
        )

    def __repr__(self):
        return (f"ReceiptManager(receipts={list(self.receipts.values())})")


class ReceiptWithChrome(Receipt):
    def wait_for_keyword_cycle(self, keyword, timeout=30):
        wait = WebDriverWait(driver, timeout)

        # wait for keyword to show
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{keyword}')]")
            )
        )

        # wait for keyword to disappear
        wait.until(
            EC.invisibility_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{keyword}')]")
            )
        )

    def set_web_amount(self, amount: int):
        wait = WebDriverWait(driver, 10)
        wait.until(EC.visibility_of_element_located((By.ID, "claim-amount")))
        driver.implicitly_wait(0.5)
        
        amount_box = driver.find_element(by=By.ID, value="claim-amount")
        amount_box.send_keys(str(amount))

    def upload_file(self, file_path: str):
        file_input = driver.find_element(By.ID, "import-img")
        file_input.send_keys(file_path)
        self.wait_for_keyword_cycle("rocessed")

    def submit_claim(self):
        wait = WebDriverWait(driver, 10)
        if os.getenv("DEBUG","False").upper() == "TRUE":
            print("DEBUG mode is on, not submitting claim.")
            return
        
        submit_btn = wait.until(
            EC.presence_of_element_located((By.ID, "submit-claim"))
        )
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", submit_btn
        )
        wait.until(EC.element_to_be_clickable((By.ID, "submit-claim")))
        submit_btn.click()
        sleep(5)

    def upload_fuel_bill(self):
        pluxee_url = os.getenv("PLUXEE_URL")
        driver.get("https://google.com")
        driver.get(pluxee_url)
        
        self.set_web_amount(int(self.amount))
        self.upload_file(self.path)
        self.submit_claim()


    def upload_mobile_bill(self, mobile_number: str):
        wait = WebDriverWait(driver, 10)
        pluxee_url = os.getenv("PLUXEE_MOBILE_URL")
        
        driver.get("https://google.com")
        driver.get(pluxee_url)
        
        self.set_web_amount(int(self.amount))
        self.upload_file(self.path)
        
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{mobile_number}')]")
            )
        )
        num_input = driver.find_element(
            By.XPATH, f"//*[contains(text(), '{mobile_number}')]"
        )
        num_input.click()
        self.submit_claim()


if __name__ == "__main__":
    receipts_dir = os.getenv("RECEIPTS_SELENA", ".")
    receipt_manager = ReceiptManager(receipts_dir)
