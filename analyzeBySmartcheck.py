import os
import subprocess
from subprocess import PIPE
import glob
import csv
from multiprocessing import Pool

solidity_vulnerabilities = ['SOLIDITY_ADDRESS_HARDCODED',
                             'SOLIDITY_ARRAY_LENGTH_MANIPULATION',
                             'SOLIDITY_BALANCE_EQUALITY',
                             'SOLIDITY_BYTE_ARRAY_INSTEAD_BYTES',
                             'SOLIDITY_CONSTRUCTOR_RETURN',
                             'SOLIDITY_CALL_WITHOUT_DATA',
                             'SOLIDITY_DELETE_ON_DYNAMIC_ARRAYS',
                             'SOLIDITY_DEPRECATED_CONSTRUCTIONS',
                             'SOLIDITY_DIV_MUL',
                             'SOLIDITY_DO_WHILE_CONTINUE',
                             'SOLIDITY_DOS_WITH_THROW',
                             'SOLIDITY_ERC20_APPROVE',
                             'SOLIDITY_ERC20_FUNCTIONS_ALWAYS_RETURN_FALSE',
                             'SOLIDITY_ERC20_INDEXED',
                             'SOLIDITY_ERC20_TRANSFER_SHOULD_THROW',
                             'SOLIDITY_EXACT_TIME',
                             'SOLIDITY_EXTRA_GAS_IN_LOOPS',
                             'SOLIDITY_FUNCTIONS_RETURNS_TYPE_AND_NO_RETURN',   #ruleではFUNCTION?
                             'SOLIDITY_GAS_LIMIT_IN_LOOPS',
                             'SOLIDITY_INCORRECT_BLOCKHASH',
                             'SOLIDITY_LOCKED_MONEY',
                             'SOLIDITY_MSGVALUE_EQUALS_ZERO',
                             'SOLIDITY_OVERPOWERED_ROLE',
                             'SOLIDITY_PRAGMAS_VERSION',
                             'SOLIDITY_PRIVATE_MODIFIER_DONT_HIDE_DATA',    #ruleではDOES_NOT
                             'SOLIDITY_REDUNDANT_FALLBACK_REJECT',
                             'SOLIDITY_REVERT_REQUIRE',
                             'SOLIDITY_REWRITE_ON_ASSEMBLY_CALL',
                             'SOLIDITY_SAFEMATH',
                             'SOLIDITY_SEND',
                             'SOLIDITY_SHOULD_NOT_BE_PURE',
                             'SOLIDITY_SHOULD_NOT_BE_VIEW',
                             'SOLIDITY_SHOULD_RETURN_STRUCT',
                             'SOLIDITY_TRANSFER_IN_LOOP',
                             'SOLIDITY_TX_ORIGIN',
                             'SOLIDITY_UINT_CANT_BE_NEGATIVE',
                             'SOLIDITY_UNCHECKED_CALL',
                             'SOLIDITY_UNUSED_FUNCTION_SHOULD_BE_EXTERNAL',
                             'SOLIDITY_UPGRADE_TO_050',
                             'SOLIDITY_USING_INLINE_ASSEMBLY',
                             'SOLIDITY_VAR',
                             'SOLIDITY_VAR_IN_LOOP_FOR',
                             'SOLIDITY_VISIBILITY',
                             'SOLIDITY_WRONG_SIGNATURE']

def main():
    max = 14297759
#    blocks = range(14297000, 14297760)
#    p = Pool(50)
#    p.map(analyzeBySmartcheck, blocks)

#    for i in reversed(range(0, 6185)):
#        blocks = range(i*1000, (i+1)*1000)
#        p = Pool(150)
#        p.map(analyzeBySmartcheck, blocks)
    blocks = range(14688629, 15449618)
    p = Pool(100)
    p.map(analyzeBySmartcheck, blocks, 1)
    return


def analyzeBySmartcheck(blockNum):
    #while(not os.path.exists('Blocks/'+str(blockNum))):
    #    print('wait Block:'+str(blockNum)+' created')
    print('Block : '+str(blockNum))
    if os.path.exists('Blocks/'+str(blockNum)):
        os.chdir('Blocks/'+str(blockNum))
    else:
        return

    contracts = glob.glob('created_contracts/0x*')
    if len(contracts) == 0:
        os.chdir('../../')
        return
    
    os.mkdir('resultSmartcheck')
    singlefile_count = [0]*46       #total, err, vul
    multiplefile_count = [0]*46     #total, err, vul

    for contract in contracts:
        if contract.endswith('.sol'):
            singlefile_count = [x + y for (x, y) in zip(singlefile_count, analyzeSingleFileContract(contract))]
        else:
            multiplefile_count = [x + y for (x, y) in zip(multiplefile_count, analyzeMultipleFileContract(contract))]

    with open('deploy_date.txt', 'r') as date_file:
        date = date_file.read()
    
    # type   | date(year-month) | total | err | vuls
    # single | 20xx-xx          |
    # multi  | 

    with open('resultSmartcheck/smartcheck_vulnerable_count.csv', 'w') as vul_count_file:
        writer = csv.writer(vul_count_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(['type', 'date', 'total', 'error'] + solidity_vulnerabilities)      #header
        writer.writerow(['singlefile', date]+singlefile_count)
        writer.writerow(['multiplefile', date]+multiplefile_count)

    # 月ごとにresultまとめる（最後）

    os.chdir('../../')
    return

def analyzeSingleFileContract(contract):
    # extract address and compiler ver. (0x------_v0.x.x)
    contract_address = contract.split('/')[1].split('+')[0]
    exist_vul = [0]*44

    # run smartcheck
    proc = subprocess.run('smartcheck -p ' + contract, shell=True, stdout=PIPE, stderr=PIPE, text=True)
    
    with open('resultSmartcheck/'+contract_address+'.txt', 'w') as resultFile:
        if not proc.stderr == '':
            resultFile.write('ANALYZE ERROR-----------------------\n')
            resultFile.write(proc.stderr)
        resultFile.write('\n\n\nRESULT------------------------------\n')
        resultFile.write(proc.stdout)

    if not proc.stdout.endswith('solidity-rules.xml'):
        for resultLine in reversed(proc.stdout.split('\n')[:-1]):   #最後の改行後の''をはぶく
            if resultLine == '':
                break

            vul_and_count = resultLine.split(' :')
            try:
                vul_index = solidity_vulnerabilities.index(vul_and_count[0])
                exist_vul[vul_index] = 1
            except Exception as e:
                with open('resultSmartcheck/singleFileAnalyzeError.txt', 'a') as errFile:
                    errFile.write(contract_address+'\n')
                return [1, 1] + [0]*44

    return [1, 0] + exist_vul

def analyzeMultipleFileContract(contract):
    # extract address and compiler ver. (0x------_v0.x.x)
    contract_address = contract.split('/')[1].split('+')[0]
    exist_vul = [0]*44

    # result---/0x---のディレクトリに各ファイルの解析結果をいれる
    # 全ファイルからの１結果はresult以下に0x---.txtで作成

    os.mkdir('resultSmartcheck/'+contract_address)
    
    for solFilePath in glob.glob(contract+'/*'):
        solFileName = solFilePath.split('/')[2][:-4]

        # run smartcheck
        proc = subprocess.run('smartcheck -p ' + solFilePath, shell=True, stdout=PIPE, stderr=PIPE, text=True)

        with open('resultSmartcheck/'+contract_address+'/'+solFileName+'.txt', 'w') as resultFile:
            if not proc.stderr == '':
                resultFile.write('ANALYZE ERROR-----------------------\n')
                resultFile.write(proc.stderr)
            resultFile.write('\n\n\nRESULT------------------------------\n')
            resultFile.write(proc.stdout)

        if not proc.stdout.endswith('solidity-rules.xml'):
            for resultLine in reversed(proc.stdout.split('\n')[:-1]):
                if resultLine == '':
                    break

                vul_and_count = resultLine.split(' :')
                try:
                    vul_index = solidity_vulnerabilities.index(vul_and_count[0])
                    exist_vul[vul_index] += 1
                except Exception as e:
                    with open('resultSmartcheck/multipleFileAnalyzeError.txt', 'a') as errFile:
                        errFile.write(contract_address+'\t'+solFileName+'\n')
                        errFile.write('\t'+type(e)+'\t'+str(e))
                    return [1, 1] + [0]*44


    for vul_index in range(0, 44):
        with open('resultSmartcheck/'+contract_address+'.txt', 'a') as contractVulFile:
            if exist_vul[vul_index] > 0:
                contractVulFile.write(solidity_vulnerabilities[vul_index] + ' :' + str(exist_vul[vul_index]) + '\n')
                exist_vul[vul_index] = 1

    return [1, 0] + exist_vul


if __name__ == '__main__':
    main()
