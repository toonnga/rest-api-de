import pandas as pd
import os
import asyncio
import uvicorn
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List
import threading
from modules.get_data import LoadFile

# Initialize FastAPI app
app = FastAPI()

# Get the absolute path of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

get_data = LoadFile(BASE_DIR)

# Global variables for transactions and products
transactions = {}
products = {}

# API to get transaction details
@app.get("/assignment/transaction/{transaction_id}")
def get_transaction(transaction_id: int):
    transaction = transactions.get(transaction_id)
    if transaction:
        data_without_product_id = {key: value for key, value in transaction.items() if key != "productId"}

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return data_without_product_id

# API to get transaction summary by product
@app.get("/assignment/transactionSummaryByProducts/{last_n_days}")
def get_summary_by_product(last_n_days: int):

    cutoff_date = datetime.now() - timedelta(days=last_n_days)
    cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0) 
    summary = {}
    
    for txn in transactions.values():
        txn_date = datetime.strptime(txn["transactionDatetime"], "%Y-%m-%d %H:%M:%S")
        txn_date = txn_date.replace(hour=0, minute=0, second=0, microsecond=0)

        if txn_date >= cutoff_date:
            summary[txn["productName"]] = summary.get(txn["productName"], 0) + txn["transactionAmount"]
    
    return {"summary": [{"productName": k, "totalAmount": v} for k, v in summary.items()]}

# API to get transaction summary by manufacturing city
@app.get("/assignment/transactionSummaryByManufacturingCity/{last_n_days}")
def get_summary_by_city(last_n_days: int):
    cutoff_date = datetime.now() - timedelta(days=last_n_days)
    cutoff_date = cutoff_date.replace(hour=0, minute=0, second=0, microsecond=0) 
    summary = {}
    
    for txn in transactions.values():
        txn_date = datetime.strptime(txn["transactionDatetime"], "%Y-%m-%d %H:%M:%S")
        txn_date = txn_date.replace(hour=0, minute=0, second=0, microsecond=0)

        city = products.get(txn["productId"], {}).get("productManufacturingCity", "Unknown")
        if txn_date >= cutoff_date:
            summary[city] = summary.get(city, 0) + txn["transactionAmount"]
    
    return {"summary": [{"cityName": k, "totalAmount": v} for k, v in summary.items()]}

# Start the app and initialization process
@app.on_event("startup")
async def startup_event():
    global transactions, products  # Ensure these are recognized as global
    products = get_data.load_product_reference()  # Load the product reference data
    transactions = get_data.load_existing_transactions()  # Load existing transactions
    handler_data = get_data.start_file_monitoring
    threading.Thread(target=handler_data, daemon=True).start()


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8080, reload=True)
