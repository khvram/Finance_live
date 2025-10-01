from google.oauth2 import service_account
from googleapiclient.discovery import build
import yfinance as yf
import pandas as pd

# --- CONFIG ---
SPREADSHEET_ID = "1dqZk3Am2PN7VbBf1s4l2TCf_tEDIvil-3rrwvrWRs1Y"  # from the sheet URL
SHEET_NAME = "Sheet1"                  # tab name
CREDENTIALS_FILE = "credentials.json"        # path to service account JSON

# --- FETCH DATA ---
symbol = "AAPL"
ticker = yf.Ticker(symbol)
price = ticker.history(period="1d")["Close"].iloc[-1]

df = pd.DataFrame([{"symbol": symbol, "price": round(price, 2)}])

# --- GOOGLE SHEETS AUTH ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)

# --- WRITE TO SHEET ---
data = [df.columns.tolist()] + df.values.tolist()  # include headers
body = {"values": data}
range_name = f"{SHEET_NAME}!A1"

service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=range_name,
    valueInputOption="USER_ENTERED",
    body=body
).execute()

print("✅ Data written to Google Sheet")
