import re
from PIL import Image
from CommonTypes import Receipt,UploadType
from pathlib import Path
import pytesseract
def mobikwikParser(imgFile):
    img = Image.open(imgFile)
    text = pytesseract.image_to_string(img)
    phone_match = re.search(r"\b\d{10}\b", text)
    phone = phone_match.group(0) if phone_match else None
    amount_match = re.search(r"\b\d+\.\d{2}\b", text)
    amount = amount_match.group(0) if amount_match else None
    receipt = Receipt(amount=amount, path=str(imgFile), mobile_number=phone,upload_type=UploadType.mobile)
    return receipt

for imgFile in Path("/home/himanshu/workDesk/pluxee-scripts/receipts/pdf").glob("*.jpeg"):
    mobikwikParser(imgFile)