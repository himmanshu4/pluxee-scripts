import os
from pathlib import Path
import setup  # noqa: F401
import pdb
from move_chrome import ReceiptManager


def main():
    receipts_dir = Path(os.getenv("RECEIPTS_SELENA"))
    receipt_manager = ReceiptManager(receipts_dir)
    print(receipt_manager.receipts)
    return receipt_manager


if __name__ == "__main__":
    receipts = main()
    pdb.set_trace()
