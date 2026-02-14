from pathlib import Path
from time import time
BASE_DIR = Path(__file__).resolve().parent.parent
RECEIPTS_DIR = BASE_DIR / "receipts"

class Receipt:
    def __init__(self, receipt_id, amount, state, path):
        self.receipt_id = receipt_id
        self.amount = amount
        self.state = state
        self.path = path
    def __repr__(self):        
        return f"Receipt(id={self.receipt_id}, amount={self.amount}, "\
        f"state={self.state}, path='{self.path}')"

class Extensions:
    img = ['.jpg', '.jpeg', '.png', ]

class ReceiptManager:
    def __init__(self,path=RECEIPTS_DIR):
        self.receipts = {}
        self.currIdx = 1 # Using timestamp as a simple unique ID generator
        self.parsePath(path)
    
    def nextID(self):
        self.currIdx += 1
        return self.currIdx

    def recover_past_receipts(self):
        # Logic to recover past receipts from storage
        pass
    def publish_receipt(self, receipt_id):
        # Logic to publish a receipt(write it in a well known file)
        pass
    def parsePath(self, path):
        for file in path.iterdir():
            if file.is_file() and file.suffix.lower() in Extensions.img:
                receipt_id = self.nextID()
                amount = 0 # Placeholder for amount extraction logic
                state = "pending" # Initial state
                self.receipts[receipt_id] = Receipt(receipt_id, amount, state, file)
        # Logic to parse the directory and extract receipt information
        

if __name__ == "__main__":
    print("Trial Receipt Manager")
    manager = ReceiptManager()
    print(manager.receipts)