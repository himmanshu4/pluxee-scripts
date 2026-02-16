import os
import re
from datetime import datetime

import pdfplumber
from flask import Flask, jsonify, request

app = Flask(__name__)


def process_receipts(directory_path):
    """
    Scans the directory, extracts data from PDFs, and compiles a dictionary list.
    """
    receipt_data = []

    if not os.path.exists(directory_path):
        return {"error": f"The directory '{directory_path}' could not be located."}, 404

    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".pdf"):
            exact_file_path = os.path.abspath(os.path.join(directory_path, filename))

            amount = "Not Found"
            date = "Not Found"
            date = "Not Found"
            source = "Not Found"
            destination = "Not Found"

            try:
                with pdfplumber.open(exact_file_path) as pdf:
                    document_text = ""
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            document_text += extracted + "\n"

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
                amount = "Error"
                source = f"File reading error: {execution_error}"

            # Append the extracted data to our payload list
            receipt_data.append(
                {
                    "exact_file_path": exact_file_path,
                    "date": date,
                    "amount": amount,
                    "source": source,
                    "destination": destination,
                }
            )

    # --- NEW: Sorting Logic ---
    def parse_date_for_sort(date_str):
        if date_str in ("Not Found", "Error", ""):
            return datetime.min  # Pushes unreadable dates to the bottom
        try:
            # Removes st, nd, rd, th so the datetime module can read it
            clean_date = re.sub(r"(?<=\d)(st|nd|rd|th)", "", date_str)
            return datetime.strptime(clean_date, "%b %d %Y, %I:%M %p")
        except ValueError:
            return datetime.min

    # Sorts the dictionary list descending based on the parsed datetime
    receipt_data.sort(key=lambda x: parse_date_for_sort(x["date"]), reverse=True)

    return {"receipts": receipt_data}, 200


@app.route("/extract", methods=["GET"])
def extract_api():
    """
    API Endpoint to trigger the extraction.
    Expects a query parameter: ?directory=path_to_folder
    """
    target_directory = request.args.get("directory", ".")
    payload, status_code = process_receipts(target_directory)

    return jsonify(payload), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
