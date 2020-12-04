import yfinance as yf

#create ticker
msft = yf.Ticker("PLTR")

#Get stock info
msft.info
price_data = msft.history(period='1mo')
print(price_data)
print(msft.institutional_holders)

#Get historical market data
