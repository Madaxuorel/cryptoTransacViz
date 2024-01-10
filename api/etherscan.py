import requests
import json

ENDPOINT = "https://api.etherscan.io/api"


"""
Object that interfaces with the etherscan api
Limited to 5 calls per sec in free plan
"""
class etherScanApi:

    def __init__(self, key):
        self.key = key
        
    """
    Returns net eth balance of a given account.
    """
    def getETHBalance(self,account):
        
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={account}&tag=latest&apikey={self.key}"
        response = requests.get(url)
        amount = response.json().get('result')
        return float(amount/1000000000000000000)
    
    """
    Returns eth/usd pair value at current time.
    """
    def getEthValue(self):
        print("CALL")
        url = f"https://api.etherscan.io/api?module=stats&action=ethprice&apikey={self.key}"
        ethUsd = requests.get(url).json().get('result').get('ethusd')
        return float(ethUsd)
    
    """
    Returns balance in a given account in usd, at current pair value.
    """
    def getUSDBalance(self,account):
        
        return self.getETHBalance(account) * float(self.getEthValue)
    
    """
    Returns list of latest transactions by a given account (to and from). Max 10k transactions.
    """
    def getLatestTransactions(self,account):
        
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={account}&startblock=0&endblock=9999999999999&page=1&offset=10000&sort=asc&apikey={self.key}"
        response = requests.get(url).json().get('result')
        return response
    
    """
    Returns the sorted top transactions by number of transactions received from same account.
    """
    def getTopAddressesReceived(self,account):
        
        self.transactions = self.getLatestTransactions(account)
        addressesReceived = {}
        
        for transaction in self.transactions:
            if transaction["from"] not in addressesReceived.keys():
                addressesReceived[transaction["from"]] = 1
            else:
                addressesReceived.update({transaction["from"]:addressesReceived[transaction["from"]]+1})

        addressesReceived = dict(sorted(addressesReceived.items(), key=lambda item: item[1], reverse=True))
        
        return addressesReceived
    
    """
    Returns top N addresses by received transaction count. 
    """
    def getTopNAddressesReceived(self,account,N):
        
        addressesReceived = self.getTopAddressesReceived(account)
        return {k: v for i, (k, v) in enumerate(addressesReceived.items()) if i < N}
    
    """
    Returns the sorted top transactions by number of transactions sent to same account.
    """
    def getTopAddressesSent(self,account):
        self.transactions = self.getLatestTransactions(account)
        addressesSent = {}
        for transaction in self.transactions:
            if transaction["to"] not in addressesSent.keys():
                addressesSent[transaction["to"]] = 1
            else:
                addressesSent.update({transaction["to"]:addressesSent[transaction["to"]]+1})
        
        addressesReceived = dict(sorted(addressesSent.items(), key=lambda item: item[1], reverse=True))

        return addressesSent
    
    """
    Returns top N addresses by sent transaction count. 
    """
    def getTopNAddressesSent(self,account,N):
        
        addressesSent = self.getTopAddressesSent(account)
        return {k: v for i, (k, v) in enumerate(addressesSent.items()) if i < N}
    
    """
    Return total value of transaction from/to the given account.
    """
    def getEthValueTransferred(self,account,transactionType):
        total = 0
        if transactionType == 'from':
            for transaction in self.transactions:
                if transaction["from"]==account:
                    total += int(transaction["value"])  
            
            return total
        
        elif transactionType == "to":
            for transaction in self.transactions:
                if transaction["to"]==account:
                    total += int(transaction["value"]) 
            return total