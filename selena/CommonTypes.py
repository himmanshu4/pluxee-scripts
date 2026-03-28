from enum import Enum
import math


class ReceiptType(Enum):
    Rapido = "Rapido"
    Mobikwik = "Mobikwik"

class UploadType(Enum):
    mobile = "mobile"
    fuel = "fuel"

class Receipt:
    def __init__(self, amount, path, source=None, destination=None, date=None, mobile_number=None, upload_type=None):
        self.amount = math.ceil(float(amount)) if amount is not None else None
        self.path = path
        self.source = source
        self.destination = destination
        self.date = date
        self.mobile_number = mobile_number
        self.upload_type = upload_type

    def __repr__(self):
        return f"Receipt(amount={self.amount}, path='{self.path}', source='{self.source}', destination='{self.destination}', date='{self.date}', mobile_number='{self.mobile_number}', upload_type='{self.upload_type}')"

    def __hash__(self):
        return hash(self.path)