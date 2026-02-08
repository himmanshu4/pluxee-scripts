from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/receipt/{receipt_id}")
def read_item(receipt_id: int, q: str | None = None):
    return {"receipt_id": receipt_id, "amount":0, "state":0}