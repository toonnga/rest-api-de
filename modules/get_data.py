import pandas as pd
import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List
import threading

# Initialize FastAPI app
app = FastAPI()
lock = threading.Lock()

class LoadFile():
    def __init__(self, BASE_DIR):
        self.transactions: Dict[int, Dict] = {}
        self.products: Dict[int, Dict] = {}
        self.TRANSACTION_FOLDER = os.path.join(BASE_DIR, "transactions")
        self.REFERENCE_FILE = os.path.join(BASE_DIR, "products", "ProductReference.csv")
        self.file_to_transactions = {}
        self.BASE_DIR = BASE_DIR

    # Load product reference data
    def load_product_reference(self):
        global products
        if not os.path.exists(self.REFERENCE_FILE):
            print(f"Warning: {self.REFERENCE_FILE} not found! Ensure the file exists.")
            return
        df = pd.read_csv(self.REFERENCE_FILE)
        products = df.set_index("productId").to_dict("index")
        # products = df.to_dict("index")
        # print(products)
        # print(products.get(10, {}).get("productName", "Unknown"))
        print("Product reference data loaded successfully.")
        return products

    def load_existing_transactions(self):
        transaction_files = glob.glob(os.path.join(self.TRANSACTION_FOLDER, "*.csv"))
        for file in transaction_files:
            # print(file)
            self.file_to_transactions = self.process_transaction_file(file)
        print(f"Loaded {len(transaction_files)} transaction files.")
    
        return self.transactions, self.file_to_transactions

    # Process new transaction files
    def process_transaction_file(self, file_path):
        # global transactions
        df = pd.read_csv(file_path)

        # Check the transaction file datetime part of the filename to ensure it's recent
        file_date = os.path.basename(file_path).split("_")[1]  # Assuming filename format 'Transaction_yyyyMMddHHmmss.csv'
        file_date = file_date.replace('.csv', '')
        print(file_date)
        file_datetime = datetime.strptime(file_date, "%Y%m%d%H%M%S")

        transaction_ids = []

        with lock: # Ensure no other thread modifies the transactions while this is running
            for _, row in df.iterrows():

                #Each API request should not be a repeatable task.
                if row.transactionId in self.transactions:
                        print(f"Skipping duplicate transaction: {row.transactionId}")
                        continue  # Skip already processed transactions
                
                self.transactions[row.transactionId] = {
                    "transactionId": row.transactionId,
                    "productId": row.productId,
                    "productName": products.get(row.productId, {}).get("productName", "Unknown"),
                    "transactionAmount": row.transactionAmount,
                    "transactionDatetime": row.transactionDatetime,
                }

                # Collect transaction IDs for the current file
                transaction_ids.append(row.transactionId)

        # print(transactions)

        self.file_to_transactions[file_path] = transaction_ids
        
        print(f"Processed transaction file: {file_path} (File Date: {file_datetime})")

        return self.file_to_transactions

    # Remove transactions corresponding to a deleted file
    def remove_transactions_from_file(self, file_path, file_to_transactions):
        # global transactions
        # Get the transaction IDs associated with the deleted file
        # print(f"File deleted: {file_path}")
        print(f"Updated file_to_transactions: {file_to_transactions}")
        transaction_ids_to_remove = file_to_transactions.pop(file_path, None)
        print(transaction_ids_to_remove)

        if not transaction_ids_to_remove:
            print(f"No transactions found for deleted file: {file_path}")
            return

        with lock:  # Ensure no other thread modifies the transactions while this is running
            for txn_id in transaction_ids_to_remove:
                if txn_id in self.transactions:
                    print(f"Removing transaction: {txn_id}")
                    del self.transactions[txn_id]

        print(f"Removed transactions from deleted file: {file_path}")

    
    # Start file monitoring
    def start_file_monitoring(self):
        observer = Observer()
        event_handler = TransactionFileHandler(self.BASE_DIR, self.transactions, self.file_to_transactions)
        # print(load_data.TRANSACTION_FOLDER)
        observer.schedule(event_handler, self.TRANSACTION_FOLDER, recursive=False)
        observer.start()
        return observer

    
class TransactionFileHandler(LoadFile, FileSystemEventHandler):
    def __init__(self, BASE_DIR, transactions, file_to_transactions):
        LoadFile.__init__(self, BASE_DIR)  # Initialize the parent class (LoadFile)
        FileSystemEventHandler.__init__(self) 
        self.transactions = transactions # Initialize the FileSystemEventHandler
        self.file_to_transactions = file_to_transactions

    def on_deleted(self, event):
        print(f"File deleted: {event.src_path}")
        if event.src_path.endswith(".csv"):
            self.remove_transactions_from_file(event.src_path, self.file_to_transactions)

    def on_created(self, event):
        print(f"New file detected: {event.src_path}")
        if event.src_path.endswith(".csv"):
            self.process_transaction_file(event.src_path)