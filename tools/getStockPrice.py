from utils.finUtil import get_company_list, get_stock_quote
from utils.companyCompleter import CompanyInput


if __name__ == "__main__":
    companyTicker = ""
    companyName = ""

    companyList = get_company_list()
    while(True):
        companyInput = CompanyInput(companyList)
        companyOutput = companyInput.run()

        if(companyOutput == None):
            continue

        companyTicker = companyOutput[0]
        companyName = companyOutput[1]
        break

    stockPrice = get_stock_quote(companyTicker)
    print(f"Current stock price for {companyTicker} ({companyName}): {stockPrice}$")
