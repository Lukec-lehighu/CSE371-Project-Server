from database import *
from colorama import init, Fore
import sys

# keep track of tests passed vs failed
numpassed = 0
total_ran = 0

def runTest(function, name="function"):
    global numpassed, total_ran

    total_ran += 1
    try:
        res = function()
        if not res is None:
            print(res)

            if type(res) == bool:
                assert res # make sure that res is always True if it is a boolean

        print(Fore.GREEN + f'[+] {name} call success:' + Fore.RESET)
        numpassed += 1
    except Exception as e:
        print(Fore.RED + f"[-] {name} call failed: {e}" + Fore.RESET)
    print()

def tests():
    init() #start colorama

    #tables and groups
    runTest(lambda:setupTables(), "setupTables")
    runTest(lambda:newGroup('Testgroup', 'Testscript', 1), "newGroup")
    runTest(lambda:getGroups('Testscript'), "getGroups")
    runTest(lambda:userIsOwnerOfGroup('Testgroup', 'Testscript'), "userIsOwnerOfGroup")
    runTest(lambda:userInGroup('Testgroup', 'Testscript'), "userInGroup")
    runTest(lambda:joinGroup('Testgroup', 'newusertest'), "joinGroup")
    runTest(lambda:joinGroup('Testgroup', 'baduser'), "joinGroup")
    runTest(lambda:removeFromGroup('Testgroup', 'baduser', 'Testscript'), "removeFromGroup")
    runTest(lambda:getMembers('Testgroup'), "getMembers")

    #receipts
    runTest(lambda:newReceipt('Testgroup', 'receipt1', 'display name'), "newReceipt")
    runTest(lambda:newReceipt('Testgroup', 'receipt2', 'display name 2'), "newReceipt")
    runTest(lambda:getReceipts('Testgroup'), "getReceipts")
    runTest(lambda:removeReceipt(2, 'display name 2'), "removeReceipt")
    runTest(lambda:getReceipts('Testgroup'), "getReceipts")

    #receipt items
    runTest(lambda:getReceiptItems(1), "getReceiptItems")
    runTest(lambda:addReceiptItem(1, 'Tomatoes', 43.23), "addReceiptItem")
    runTest(lambda:addReceiptItem(1, 'Bread', 2.43), "addReceiptItem")
    runTest(lambda:removeReceiptItem(1, 'Bread'), "removeReceiptItem")
    runTest(lambda:getReceiptItems(1), "getReceiptItems")

    #requests
    runTest(lambda:newRequest('Testgroup', 'Testscript', 'display name', 'I want bread lol'), "newRequest")
    runTest(lambda:getRequests('Testgroup'), "getRequests")
    runTest(lambda:removeRequest(1), "removeRequest")
    runTest(lambda:getRequests('Testgroup'), "getRequests")

    #claimed items
    runTest(lambda:toggleClaimItem(1, 'Tomatoes', 'Testscript'), "toggleClaimItem")
    runTest(lambda:getClaimedItems(1), "getClaimedItems")
    runTest(lambda:toggleClaimItem(1, 'Tomatoes', 'Testscript'), "toggleClaimItem")

    #dept
    runTest(lambda:getDept('Testgroup', 'Testscript'), "getDebt")

    #cleanup
    runTest(lambda:deleteGroup('Testgroup', 'Testscript'), "deleteGroup")

    print()
    print(f"Tests finished: {numpassed} / {total_ran} passed")

def reset():
    init()
    runTest(lambda:deleteGroup('Testgroup', 'Testscript'), "deleteGroup")

if __name__=='__main__':
    print(sys.argv)
    if len(sys.argv) > 1 and sys.argv[1]=='reset':
        reset()
    else:
        tests()