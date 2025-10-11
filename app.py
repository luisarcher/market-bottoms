
import os
import pandas as pd
import yfinance as yf
from williams_vix_fix import williams_vix_fix

from telegram_message import TelegramMessager

import logging
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

# Index tickers for yfinance
TICKERS = {
	'IWDA': 'IWDA.AS',  # Euronext Amsterdam
	'VWCE': 'VWCE.DE',  # Vanguard FTSE All-World UCITS ETF USD ACCUMULATING (XETRA)
}

def fetch_4h_candles(ticker, period='60d'):
	"""Fetch 4h candles for a given ticker using yfinance."""
	df = yf.download(ticker, interval='4h', period=period)
	# debug market data
	#df = df.rename(columns={
	#		'Open': 'Open', 'High': 'High', 'Low': 'Low', 'Close': 'Close', 'Volume': 'Volume'
	#})
	# Test -- save data for inspection
	#df.to_csv(f"data/{ticker}.csv")
	return df

def main():
	
	# NOTE: Find the conversation id with the bot
	#  Send a message to the bot
	#  Get bot updates (last message)
	#  https://api.telegram.org/bot<token>/getUpdates
	tm = TelegramMessager()
	
	results = {}
	for name, ticker in TICKERS.items():
		
		df = fetch_4h_candles(ticker)
		if df.empty:
			print(f"No data for {name} ({ticker})")
			continue
		
		indicator_df = williams_vix_fix(df)
		#indicator_df.to_csv(f"data/{name}_indicator.csv")
		last = indicator_df.iloc[-1].squeeze()
		logger.info(f"{name} ({ticker}): {last}")

		is_bottom = int(last['bottom'].iloc[0]) == 1
		results[name] = is_bottom

		# Calculate price variance for last 4 days
		last_4_days = df['Close'].tail(4)
		min_price = float(last_4_days.min())
		max_price = float(last_4_days.max())
		current_price = float(last_4_days.iloc[-1])
		price_variance = max_price - min_price
		variance_percentage = (price_variance / min_price) * 100
		
		# Send simple message with price analysis
		msg = (f"[{name}](https://finance.yahoo.com/quote/{ticker}) - Last 4 days analysis:\n"
			   f"Current: €{current_price:.2f}\n"
			   f"Min: €{min_price:.2f} | Max: €{max_price:.2f}\n"
			   f"Variance: €{price_variance:.2f} ({variance_percentage:.1f}%)")
		
		tm.log(msg)
		
		if is_bottom:
			tm.log(f"[BUY] Market Bottom Alert for {name}!")

if __name__ == "__main__":
	main()
