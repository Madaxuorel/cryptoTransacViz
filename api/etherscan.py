import requests
import json

ENDPOINT = "https://api.etherscan.io/api"

"""
when given an eth address, we will query :
1 : ACCOUNT BALANCE
2 : TOP ACCOUNTS BY TRANSACTION VOLUME
3 : ENS ? 
4 : TOP TRANSACTIONS BY SIZE
5 : MISC STATS ? (TOTAL GAS, TOTAL TRANS VOL)
"""


class etherScanApi:

    def __init__(self, key):
        self.key = key
        
    def getETHBalance(self,account):
        
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={account}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        amount = response.json().get('result')
        return float(amount/1000000000000000000)
    
    def getEthValue(self):
        
        url = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={self.key}"
        ethUsd = requests.get(url).json().get('result').get('ethusd')
        return float(ethUsd)
    
    def getUSDBalance(self,account):
        
        return self.getETHBalance(account) * float(self.getEthValue)
    
    def getLatestTransactions(self,account):
        
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={account}&startblock=0&endblock=9999999999999&page=1&offset=10000&sort=asc&apikey={self.key}"
        response = requests.get(url).json().get('result')
        return response
    
    def getTopAddressesReceived(self,account):
        
        transactions = self.getLatestTransactions(account)
        addressesReceived = {}
        
        for transaction in transactions:
            if transaction["from"] not in addressesReceived.keys():
                addressesReceived[transaction["from"]] = 1
            else:
                addressesReceived.update({transaction["from"]:addressesReceived[transaction["from"]]+1})

        addressesReceived = dict(sorted(addressesReceived.items(), key=lambda item: item[1], reverse=True))
        
        return addressesReceived
    
    def getTopNAddressesReceived(self,account,N):
        
        addressesReceived = self.getTopAddressesReceived(account)
        return {k: v for i, (k, v) in enumerate(addressesReceived.items()) if i < N}
        