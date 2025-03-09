# rest-api-de

## How to Run:

- **Prerequisite Step:**
    - `git clone git@github.com:toonnga/rest-api-de.git` (SSH) or `git clone https://github.com/toonnga/rest-api-de.git` (HTTPS)
    - `cd rest-api-de`
    - `pip install poetry`
    - `poetry install`
    - `poetry update`
- **Running Step:**
    - `poetry run python main.py`


## Configuration:

**File Structure**

```
rest-api-de
  ├── /products
  │     └── ProductReference.csv    # Product reference data
  ├── /transactions                 # Directory to store transaction files
  ├── main.py                       # FastAPI application
  ├── /modules
  │     └── get_data.py             # Get Transaction and product data processing logic with data handling auto sync
  ├── pyproject.toml                # Dependencies for the project
  └── README.md      
```

 - ProductReference.csv: Contains product information (e.g., product ID, product name, manufacturing city).
 - transactions/: Directory for incoming transaction files (CSV format).

 *Ensure that the product reference CSV and transaction files are placed correctly before starting the app.*


**Environment Variables**

You may need to adjust some settings, such as:

 - TRANSACTION_FOLDER: Path to the directory where incoming transaction files will be stored.
 - REFERENCE_FILE: Path to the ProductReference.csv file.

*By default, these settings are configured to use the products and transactions directories relative to the project folder.*

## Usage

*API Endpoints*
1. Get Transaction by ID

    - Endpoint: /assignment/transaction/{transaction_id}
    - Method: GET
    - Description: Retrieves the transaction details for the given transaction ID.
    - Example:
        - URL: http://localhost:8080/assignment/transaction/1
        - Response:
        ```json
        {
        "transactionId": 1,
        "productId": 10,
        "productName": "P1",
        "transactionAmount": 1000.0,
        "transactionDatetime": "2025-03-08 10:10:1-"
        }
        ```

2. Get Transaction Summary by Product (Last N Days)

    - Endpoint: /assignment/transactionSummaryByProducts/{last_n_days}
    - Method: GET
    - Description: Retrieves the total transaction amounts by product over the last N days.
    - Example:
        - URL: http://localhost:8080/assignment/transactionSummaryByProducts/1
        - Response:
        ```json
        {
        "summary": [
            {"productName": "P1", "totalAmount": 9000.0},
            {"productName": "P2", "totalAmount": 8000.0},
            {"productName": "P3", "totalAmount": 6000.0}
        ]
        }
        ```

3. Get Transaction Summary by Manufacturing City (Last N Days)

    - Endpoint: /assignment/transactionSummaryByManufacturingCity/{last_n_days}
    - Method: GET
    - Description: Retrieves the total transaction amounts by product manufacturing city over the last N days.
    - Example:
        - URL: http://localhost:8080/assignment/transactionSummaryByManufacturingCity/1
        - Response:
        ```json
        {
        "summary": [
            {"cityName": "C1", "totalAmount": 17000.0},
            {"cityName": "C2", "totalAmount": 6000.0}
        ]
        }
        ```

**File Monitoring**

The application monitors the transactions/ folder for new transaction files. When a new .csv file is added, it will automatically process the transactions and update the global transaction dictionary. Similarly, if a file is deleted, the associated transactions will be removed.

## File Structure

The transactions/ folder should contain transaction files in CSV format with the following columns:

- transactionId: Unique ID for each transaction.
- productId: The ID of the product being sold.
- transactionAmount: The amount of the transaction.
- transactionDatetime: The date and time of the transaction.

Example transaction file (Transaction_20250308101010.csv):

## Example Transaction File Structure

The transaction file should have the following columns:

| Column Name          | Description                                  | Example                  |
|----------------------|----------------------------------------------|--------------------------|
| **transactionId**     | Unique identifier for the transaction        | 1                        |
| **productId**         | ID of the product associated with the transaction | 10                   |
| **transactionAmount** | The amount of the transaction                | 1000.0                      |
| **transactionDatetime** | The timestamp when the transaction occurred | 2025-03-08 10:10:10      |

