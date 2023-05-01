import socket
from urllib import request, error 
import json
import datetime
import os
from multiprocessing import Pool

# with open('./api_key.json', mode = 'r') as key_file:
#     ApiKey = json.loads(key_file.read())['key']

ApiKey = 'AUDU2TVS72YRB3CETQEH5CJP9RDPF4PJ5G'

def getBlockContent(blockNumber):
    timeout = 5
    socket.setdefaulttimeout(timeout)
    getBlockUrl = 'https://api.etherscan.io/api?module=proxy&action=eth_getBlockByNumber&tag=' + hex(blockNumber) + '&boolean=true&apikey=' + ApiKey
    blockContent = None

    while blockContent == None:
        try:
            with request.urlopen(getBlockUrl) as response:
                blockContent = json.loads(response.read().decode())
        except Exception as e:
            print(type(e))
            print(str(e))
            blockContent = None
            continue

        # check api error(status=0)
        if blockContent.get("status") == '0':
            print("Etherscan Api Error, status:0")
            blockContent = None
            continue
    
    return blockContent


def getTxReceipt(txhash):
    timeout = 5
    socket.setdefaulttimeout(timeout)
    getTxUrl = 'https://api.etherscan.io/api?module=proxy&action=eth_getTransactionReceipt&txhash=' + txhash + '&apikey=' + ApiKey
    txReceiptContent = None

    while txReceiptContent == None:
        try:
            with request.urlopen(getTxUrl) as response:
                txReceiptContent = json.loads(response.read().decode())
        except Exception as e:
            print(type(e))
            print(str(e))
            txReceiptContent = None
            continue

        # check api error(status=0)
        if txReceiptContent.get("status") == '0':
            print("Etherscan Api Error, status:0")
            txReceiptContent = None
            continue
    
    return txReceiptContent


def getContractSource(contractAdd):
    timeout = 5
    socket.setdefaulttimeout(timeout)
    getSourceUrl = 'https://api.etherscan.io/api?module=contract&action=getsourcecode&address=' + contractAdd + '&apikey=' + ApiKey

    contractSourceContent = None

    while contractSourceContent == None:
        try:
            with request.urlopen(getSourceUrl) as response:
                contractSourceContent = json.loads(response.read().decode())
        except Exception as e:
            print(type(e))
            print(str(e))
            contractSourceContent = None
            continue

        # check api error(status=0)
        if contractSourceContent.get("status") == '0':
            print("Etherscan Api Error, status:0")
            contractSourceContent = None
            continue
    
    return contractSourceContent

def devidingMultipleSolFile(multiple_sol_info, dirName):
    try:
        source_files = multiple_sol_info["sources"]
    except:
        source_files = multiple_sol_info

    for solidity_file in source_files.keys():
        with open(dirName+'/'+solidity_file.replace('/', '_'), 'w') as sol_file:
            sol_file.write(source_files[solidity_file]["content"])

    return

def checkBlock(blockNum):
    maxBlockNum = 15253305
    print(str(blockNum)+'/'+str(maxBlockNum))
    blockContent = getBlockContent(blockNum)
    os.mkdir('./Blocks/'+str(blockNum))

    # write block information into file
#    with open('./Blocks/'+str(blockNum)+'/block_info.json', 'w') as jsonf:
#        json.dump(blockContent, jsonf, indent=4)

    # get block timestamp
    blockTimestamp = int(blockContent["result"]["timestamp"], 0)
    blockDatetime = datetime.datetime.fromtimestamp(blockTimestamp).strftime('%Y-%m-%d')
    with open('./Blocks/'+str(blockNum)+'/deploy_date.txt', 'w') as datef:
        datef.write(blockDatetime)

    # get block transactions
    transactions = blockContent["result"]["transactions"]

 #   print('transactions: ' + str(len(transactions)))
    for tx in transactions:
        # tx: create contract
        if tx["to"] == None:
            txReceipt = getTxReceipt(tx["hash"])
            
            # new contract's address
            contractAddress = txReceipt["result"]["contractAddress"]

            if not os.path.exists('./Blocks/'+str(blockNum)+'/created_contracts'):
                os.mkdir('./Blocks/'+str(blockNum)+'/created_contracts')
            # write creation contract address into file
            with open('./Blocks/'+str(blockNum)+'/created_contracts/created_contracts.txt', 'a') as created_contract_file:
                created_contract_file.write(contractAddress+'\n')

            # get created contract source code
#            print('get source code of contract: ' + contractAddress)
            contractSourceContent = getContractSource(contractAddress)

            contractSource = contractSourceContent["result"][0]["SourceCode"]
            compilerVersion = contractSourceContent["result"][0]["CompilerVersion"]

            if contractSource == '':
                # not verified contract?, can't get solidity file
                with open('./Blocks/'+str(blockNum)+'/created_contracts/not_verified_contracts.txt', 'a') as not_verified_file:
                    not_verified_file.write(contractAddress+'\n')
            
            elif compilerVersion.startswith('vyper'):
                # created by vyper
                with open('./Blocks/'+str(blockNum)+'/created_contracts/vyper_contracts.txt', 'a') as vyper_file:
                    vyper_file.write(contractAddress+'\n')

            elif not contractSource[0] == '{':
                # created by single Solidity file
                with open('./Blocks/'+str(blockNum)+'/created_contracts/'+contractAddress+'_'+compilerVersion+'.sol', 'w') as solidity_file:
                    solidity_file.write(contractSource)

            else:
                #created by multiple Solidity file
                os.mkdir('./Blocks/'+str(blockNum)+'/created_contracts/'+contractAddress+'_'+compilerVersion)
                if contractSource[1] == '{' and contractSource[-1] == '}' and contractSource[-2] == '}':
                    devidingMultipleSolFile(json.loads(contractSource[1:-1]), './Blocks/'+str(blockNum)+'/created_contracts/'+contractAddress+'_'+compilerVersion)
                else:
                    devidingMultipleSolFile(json.loads(contractSource), './Blocks/'+str(blockNum)+'/created_contracts/'+contractAddress+'_'+compilerVersion)
    print('\tend:' + str(blockNum))

    return







#1. get block information and write into file
#APIError = '{\"status\":\"0\",\"message\":\"NOTOK\",\"result\":\"Max rate limit reached, please use API Key for higher rate limit\"}'

## 14297759 is last tx. in 2/28 23:59(unix time?)
# blockNum = 62040
maxBlockNum = 14297759

#blockNum = 13708860

#blocks = reversed(range(1043100, 13306006))




#blocks = reversed(range(13290000, 13306006))
#p = Pool(40)
#p.map(checkBlock, blocks)

#for i in reversed(range(105, 1120)):
#    blocks = range(i*10000, (i+1)*10000)
#    p = Pool(40)
#    p.map(checkBlock, blocks)

#blocks = range(1043100, 1050000)
#p = Pool(40)
#p.map(checkBlock, blocks)

blocks = range(15253306, 15449618)
p = Pool(40)
p.map(checkBlock, blocks, 1)


