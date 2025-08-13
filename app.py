
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
		indicator_df.to_csv(f"data/{name}_indicator.csv")
		last = indicator_df.iloc[-1].squeeze()
		logger.info(f"{name} ({ticker}): {last}")

		is_bottom = int(last['bottom'].iloc[0]) == 1
		results[name] = is_bottom

		# TEST is_bottom condition
		# Get row where wvf == 4.316614315920342
		#wvf_row = indicator_df[indicator_df['wvf'] == 4.316614315920342]
		#logger.info(f"WVF row for {name}:\n{wvf_row}")
		#is_bottom_test = int(wvf_row['bottom'].iloc[0]) == 1
		#logger.info(f"{name} is_bottom_test: {is_bottom_test}")

		if is_bottom:
			msg = f"{name}: Good day to buy!"
			tm.log(f"Market Bottom Alert!\n{msg}")

if __name__ == "__main__":
	main()
