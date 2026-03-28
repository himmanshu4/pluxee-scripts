import os
from pathlib import Path
import setup  # noqa: F401
import pdb
from move_chrome import ReceiptManager


def main():
    receipts_dir = Path(os.getenv("RECEIPTS_SELENA"))
    receipt_manager = ReceiptManager(receipts_dir)
    # print(receipt_manager.receipts)
    return receipt_manager


if __name__ == "__main__":
    receipt_manager = main()
    print("No of receipts", len(receipt_manager.receipts))
    for receipt in receipt_manager.receipts.values():
        if receipt.amount is None:
            print(f"# Skipping {receipt.path} due to missing amount.")
            continue
        print(f"# Processing {receipt.path}")
        receipt_manager.receiptUploader.upload_bill(receipt)
        if os.getenv("DEBUG", "False").upper() != "TRUE":
            print(f"rm {receipt.path}")
    pdb.set_trace()
