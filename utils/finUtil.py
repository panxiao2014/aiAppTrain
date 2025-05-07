import os
import requests
import finnhub

with open('credentials/finnhub.txt', 'r') as f:
    finnhubKey = f.read().strip()
    finnhubClient = finnhub.Client(api_key=finnhubKey)


def get_company_list() -> list:
    #check if data/tickers.csv exists
    if os.path.exists('data/tickers.csv'):
        pass
    else:
        with open("credentials/alpha.vantage.txt", "r") as f:
            alpha_vantage_key = f.read().strip()
        url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={alpha_vantage_key}"

        response = requests.get(url)
        data = response.text

        #save first and second columns of data to a csv file in data folder
        with open("data/tickers.csv", "w") as f:
            for line in data.splitlines():
                f.write(",".join(line.split(",")[:2]) + "\n")

    companyList = []
    with open("data/tickers.csv", "r") as f:
        next(f) #skip the first line
        for line in f:
            companyList.append(line.strip().split(","))

    return companyList
    

def get_stock_price(symbol: str) -> float:
    return finnhubClient.quote(symbol)['c']



# Usage
if __name__ == "__main__":
    print(get_stock_price('AAPL'))
