import sys
sys.path.append("../")

from api import etherscan

acc = '0x45ca2D09D4C50606f1317D286890416C3082fA96'
testAcc = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'
api = etherscan.etherScanApi("TWUQ778V3WRVAW2EBX1XZZ9BNHDGQN442B")
api.getTopNAddressesReceived(testAcc,10)

