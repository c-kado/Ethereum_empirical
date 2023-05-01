import os
import glob
import pandas as pd
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

monthList = ['2015-07', '2015-08', '2015-09', '2015-10', '2015-11', '2015-12']

for year in range(2016, 2022):
    for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
        monthList.append(str(year)+'-'+month)


monthList += ['2022-01', '2022-02', '2022-03', '2022-04', '2022-05', '2022-06', '2022-07', '2022-08', '2022-09']


ind = ['total', 'error'] + solidity_vulnerabilities

#for ver in range(0, 9):
#    df = pd.DataFrame(0, index = ind, columns = monthList)
#    df.to_csv('sum_smartcheck_new_locked_money/v0.'+str(ver)+'_new_locked_money_single.csv')
#    df.to_csv('sum_smartcheck_new_locked_money/v0.'+str(ver)+'_new_locked_money_multiple.csv')

    #df.to_csv('sum_smartcheck/v0.'+str(ver)+'_single.csv')
    #df.to_csv('sum_smartcheck/v0.'+str(ver)+'_multiple.csv')


def sumVersion(version):
    #blocks = reversed(range(0, 14297760))
    blocks = reversed(range(0, 15449618))

    month = ''

    #os.chdir('Blocks/15000083')
    for blockNum in blocks:
        if os.path.exists('Blocks/'+str(blockNum)+'/resultSmartcheck'):
            os.chdir('Blocks/'+str(blockNum))
        else:
            continue
        with open('deploy_date.txt', 'r') as date_f:
            deploy_month = date_f.read()[:-3]
        if month != deploy_month:
            month = deploy_month
        
        #ver_file_list = glob.glob('resultSmartcheck/v0.*_new_locked_money.csv')
        #ver_file_list = glob.glob('resultSmartcheck/v0.?.?_new_locked_money.csv')
        #ver_file_list.extend(glob.glob('resultSmartcheck/v0.?.??_new_locked_money.csv'))
        #ver_file_list = glob.glob('resultSmartcheck/'+version+'*_new_locked_money.csv')
        ver_file_list = glob.glob('resultSmartcheck/'+version+'_new_locked_money.csv')
        ver_file_list.extend(glob.glob('resultSmartcheck/'+version+'-*_new_locked_money.csv'))
        #ver_file_list = glob.glob('resultSmartcheck/v0.?.csv')
        for ver_file in ver_file_list:
            #ver = ver_file[17:-4]
            #last change
            #ver = ver.split('-')[0]
            #ver = ver.split('_')[0]
            #if ver != sum_ver:
            #    continue
            ver_vul_df = pd.read_csv(ver_file, index_col=0)
            
            #last change : "os.path" cant' use '~'. 
            #if not os.path.exists(os.path.expanduser('~/')+'dicomo/sum_smartcheck_new_locked_money/' + ver + '_single.csv'):
                #with open('~/dicomo/sum_smartcheck_new_locked_money/' + ver + '_single.csv', 'w') as f:
                #    f.write('')
            #    df = pd.DataFrame(0, index = ind, columns = monthList)
            #    df.to_csv('~/dicomo/sum_smartcheck_new_locked_money/'+ver+'_single.csv')
            
            sum_single_df = pd.read_csv('~/dicomo/sum_smartcheck_new_locked_money/'+version[:4]+'/' + version + '_single.csv', index_col = 0)
            #sum_single_df = pd.read_csv('~/dicomo/sum_smartcheck/' + ver + '_single.csv', index_col = 0)
            sum_single_df[month] += ver_vul_df.loc['singlefile']
            sum_single_df.to_csv('~/dicomo/sum_smartcheck_new_locked_money/'+version[:4]+'/' + version + '_single.csv')
            #sum_single_df.to_csv('~/dicomo/sum_smartcheck/' + ver + '_single.csv')

            #if not os.path.exists(os.path.expanduser('~/')+'dicomo/sum_smartcheck_new_locked_money/' + ver + '_multiple.csv'):
                #with open('~/dicomo/sum_smartcheck_new_locked_money/' + ver + '_multiple.csv', 'w') as f:
                #    f.write('')
            #    df = pd.DataFrame(0, index = ind, columns = monthList)
            #    df.to_csv('~/dicomo/sum_smartcheck_new_locked_money/'+ver+'_multiple.csv')
            sum_multiple_df = pd.read_csv('~/dicomo/sum_smartcheck_new_locked_money/'+version[:4]+'/' + version + '_multiple.csv', index_col = 0)
            #sum_multiple_df = pd.read_csv('~/dicomo/sum_smartcheck/' + ver + '_multiple.csv', index_col = 0)
            sum_multiple_df[month] += ver_vul_df.loc['multiplefile']
            sum_multiple_df.to_csv('~/dicomo/sum_smartcheck_new_locked_money/'+version[:4]+'/' + version + '_multiple.csv')
            #sum_multiple_df.to_csv('~/dicomo/sum_smartcheck/' + ver + '_multiple.csv')
        if blockNum % 10000 == 0:
            print('end : '+str(blockNum)+'-')
        os.chdir('../../')
    with open('end_sum_version.txt', 'a') as f:
        f.write(version+'\n')


solc8 = range(0,18)
solc7 = range(0,7)
solc6 = range(0,13)
solc5 = range(0,18)
solc4 = range(0,27)
solc3 = range(0,7)
solc2 = range(0,3)
solc1 = range(0,8)

#sum_ver = 'v0.1.0'
versions = []
for v in solc8:
    versions.append('v0.8.'+str(v))
for v in solc7:
    versions.append('v0.7.'+str(v))
for v in solc6:
    versions.append('v0.6.'+str(v))
for v in solc5:
    versions.append('v0.5.'+str(v))
for v in solc4:
    versions.append('v0.4.'+str(v))
for v in solc3:
    versions.append('v0.3.'+str(v))
for v in solc2:
    versions.append('v0.2.'+str(v))
for v in solc1:
    versions.append('v0.1.'+str(v))

p = Pool(140)
p.map(sumVersion, versions)

