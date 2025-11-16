from database import *
from colorama import init, Fore

def runTest(function, name="function"):
    try:
        res = function()
        print(Fore.GREEN + f'{name} call success:' + Fore.RESET)
        if not res is None:
            print(res)
    except Exception as e:
        print(Fore.RED + f"{name} call failed: {e}" + Fore.RESET)
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
    runTest(lambda:getMembers('Testgroup'), "getMembers")

    #receipts
    runTest(lambda:newReceipt('Testgroup', 'receipt1', 'display name'), "newReceipt")
    runTest(lambda:newReceipt('Testgroup', 'receipt2', 'display name 2'), "newReceipt")
    runTest(lambda:getReceipts('Testgroup'), "getReceipts")
    runTest(lambda:removeReceipt('Testgroup', 'receipt2'), "removeReceipt")
    runTest(lambda:getReceipts('Testgroup'), "getReceipts")

    #requests
    runTest(lambda:newRequest('Testgroup', 'Testscript', 'display name', 'I want bread lol'), "newRequest")
    runTest(lambda:getRequests('Testgroup'), "getRequests")
    runTest(lambda:removeRequest(0), "removeRequest")
    runTest(lambda:getRequests('Testgroup'), "getRequests")

    #claimed items


    runTest(lambda:deleteGroup('Testgroup', 'Testscript'), "deleteGroup")

if __name__=='__main__':
    tests()