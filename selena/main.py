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
    receipts = main()
    print("No of receipts", len(receipts.receipts))
    for receipt in receipts.receipts.values():
        if receipt.amount is None:
            print(f"# Skipping {receipt.path} due to missing amount.")
            continue
        print(f"# Processing {receipt.path}")
        receipt.upload_fuel_bill()
        print(f"rm {receipt.path}")
    pdb.set_trace()
