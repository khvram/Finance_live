from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import feedparser
from datetime import datetime, timedelta
import urllib.parse

# --- CONFIG ---
SPREADSHEET_ID = "1dqZk3Am2PN7VbBf1s4l2TCf_tEDIvil-3rrwvrWRs1Y"  # your sheet ID
SHEET_NAME = "ETF_News"                 # tab name
CREDENTIALS_FILE = "credentials.json"   # path to service account JSON

# --- FETCH NEWS ---
queries = ["AI ETF", "Crypto ETF"]
news_data = []
time_threshold = datetime.utcnow() - timedelta(days=1)  # last 24 hours

for q in queries:
    q_encoded = urllib.parse.quote(q)
    url = f"https://news.google.com/rss/search?q={q_encoded}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)

    count = 0
    for entry in feed.entries:
        if hasattr(entry, "published_parsed"):
            published_dt = datetime(*entry.published_parsed[:6])
            if published_dt < time_threshold:
                continue  # skip old news
        else:
            continue  # skip if no date

        news_data.append({
            "Category": q,
            "Title": entry.title,
            "Link": entry.link,
            "Date": published_dt.strftime("%Y-%m-%d %H:%M:%S")
        })

        count += 1
        if count >= 5:  # only 5 per query
            break

# Create DataFrame
df = pd.DataFrame(news_data)

# --- GOOGLE SHEETS AUTH ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = service_account.Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=creds)

# --- WRITE TO SHEET ---
data = [df.columns.tolist()] + df.values.tolist()
body = {"values": data}
range_name = f"{SHEET_NAME}!A1"

service.spreadsheets().values().update(
    spreadsheetId=SPREADSHEET_ID,
    range=range_name,
    valueInputOption="USER_ENTERED",
    body=body
).execute()

print("✅ ETF News (last 24h) written to Google Sheet")
