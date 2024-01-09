import json

def blacklistedAddresses():
    file_path = "../addressesBlacklist.json"
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    addresses = [entry['address'] for entry in data]
    
    return addresses