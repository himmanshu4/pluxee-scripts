class ReceiptType(Enum):
    Rapido = "Rapido"

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