import sqlite3

DB_NAME = 'groceries.db'

MAX_GROUPNAME_LEN = 50
MAX_USERNAME_LEN = 50
MAX_RECEIPT_ITEM_LEN = 100
MAX_REQUEST_LEN = 200

def _table_exists(name, cur):
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
    return not res.fetchone() is None

# TODO: keep track of email of author in receipts for ownership (using display name is not reliable since people can have the same name)

def setupTables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # make sure each table exists and if not, create it
    if not _table_exists('groups', cur):
        cur.execute(f"""CREATE TABLE groups(
                        groupname varchar({MAX_GROUPNAME_LEN}) PRIMARY KEY,
                        owner varchar({MAX_USERNAME_LEN}),
                        public int
                    )""")
        print('Created table: groups')
    
    if not _table_exists('group_members', cur):
        cur.execute(f"""CREATE TABLE group_members(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        membername varchar({MAX_USERNAME_LEN}),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname) ON DELETE CASCADE
                    )""")
        print('Created table: group_members')

    if not _table_exists('receipts', cur):
        cur.execute(f"""CREATE TABLE receipts(
                        rID INTEGER NOT NULL,
                        name varchar({MAX_GROUPNAME_LEN}),
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        author varchar({MAX_USERNAME_LEN}),
                        PRIMARY KEY(rID),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname) ON DELETE CASCADE
                        )""")
        print('Created table: receipts')

    if not _table_exists('receipt_data', cur):
        cur.execute(f"""CREATE TABLE receipt_data(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}) PRIMARY KEY,
                        cost REAL,
                        FOREIGN KEY (rID) REFERENCES receipts(rID) ON DELETE CASCADE
                        )""")
        print('Created table: receipt_data')

    if not _table_exists('claimed_items', cur):
        cur.execute(f"""CREATE TABLE claimed_items(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}),
                        claimer varchar({MAX_USERNAME_LEN}),
                        FOREIGN KEY (rID) REFERENCES receipts(rID) ON DELETE CASCADE
                        )""")
        print('Created table: claimed_items')
        
    if not _table_exists('requests', cur):
        cur.execute(f"""CREATE TABLE requests(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        requester varchar({MAX_USERNAME_LEN}),
                        request varchar({MAX_REQUEST_LEN}),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname) ON DELETE CASCADE
                        )""")
        print('Created table: requests')
    
    con.close()

def getGroups(username):
    # get all of the groups that the user has access to 
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    groups = cur.execute("SELECT groupname FROM groups").fetchall()
    joined = cur.execute(f"SELECT groupname FROM group_members WHERE membername=?", (username,)).fetchall()

    con.close()

    res = [[group, group in joined] for group in groups]
    return res

def userIsOwnerOfGroup(groupname, username, cur=None):
    con = None
    if not cur:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

    owner = cur.execute(f"SELECT owner FROM groups WHERE groupname=?", (groupname,)).fetchone()
    if con:
        con.close()
    return len(owner) != 0 and owner[0] == username

def userInGroup(groupname, member, cur=None):
    con = None
    if not cur:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

    already_joined = cur.execute(f"SELECT * FROM group_members WHERE groupname=? AND membername=?", (groupname, member)).fetchall()

    if con:
        con.close()

    if len(already_joined) != 0:
        return True
    return False

def newGroup(groupname, ownername, public):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # Trim names if necessary
    if len(groupname) > MAX_GROUPNAME_LEN:
        groupname = groupname[0:MAX_GROUPNAME_LEN]
    if len(ownername) > MAX_USERNAME_LEN:
        ownername = ownername[0:MAX_USERNAME_LEN]

    try:
        cur.execute("INSERT INTO groups (groupname, owner, public) VALUES" \
                    f"(?, ?, ?)", (groupname, ownername, 1 if public else 0))
        cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                    f"(?, ?)", (groupname, ownername))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def joinGroup(groupname, username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # check to make sure the username has permission to join or is already joined
    isPublic = cur.execute(f"SELECT public FROM groups WHERE groupname=?", (groupname,)).fetchone()
    if not isPublic[0]:
        return False

    if userInGroup(groupname=groupname, member=username, cur=cur):
        return True # return true as a safeguard from duplicate joins

    # user has permission and isn't already joined, add them to the database
    try:
        # execute join command and commit changes
        cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                        f"(?, ?)", (groupname, username))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def removeFromGroup(groupname, username, personDeleting):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # check to make sure the person doing this has authority
    if userIsOwnerOfGroup(groupname=groupname, username=personDeleting, cur=cur):
        cur.execute("PRAGMA foreign_keys = ON")
        if userIsOwnerOfGroup(groupname=groupname, username=username, cur=cur):
            # deleting the owner of the group, delete the whole group
            cur.execute("DELETE FROM groups WHERE groupname=?", (groupname,))
        else:
            # just delete the one member
            cur.execute("DELETE FROM group_members WHERE groupname=? AND membername=?", (groupname, username))
        con.commit()
        con.close()
        return True
    else:
        con.close()
        return False
    
def addToGroup(groupname, username, personAdding):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # check to make sure the person doing this has authority
    if userIsOwnerOfGroup(groupname=groupname, username=personAdding, cur=cur):
        if userInGroup(groupname=groupname, member=username, cur=cur):
            return True # return true as a safeguard from duplicate joins

        try:
            cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                        f"(?, ?)", (groupname, username))
            con.commit()
            con.close()
            return True
        except Exception as e:
            print(e)
            con.close()
            return False
    else:
        con.close()
        return False

def deleteGroup(groupname, username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    if userIsOwnerOfGroup(groupname, username):
        cur.execute("PRAGMA foreign_keys = ON") # allow for cascading delete
        cur.execute(f"DELETE FROM groups WHERE groupname=?", (groupname,))
        con.commit()

    con.close()

def getMembers(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # make sure group exists
    group = cur.execute(f"SELECT owner FROM groups WHERE groupname=?", (groupname,)).fetchone()
    if len(group) == 0:
        return 'DNE', []
    
    owner = group[0]
    members = cur.execute(f"SELECT membername FROM group_members WHERE groupname=?", (groupname,)).fetchall()
    con.close()

    members = [members[i][0] for i in range(len(members))]
    members.remove(owner) # no need to list the owner as a member since they literally own the group lol
    return owner, members

def getReceipts(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    receipts = cur.execute(f"SELECT * FROM receipts WHERE groupname=?", (groupname,)).fetchall()
    con.close()
    return receipts

# TODO: username check
def newReceipt(groupname, name, author):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    try:
        cur.execute(f"INSERT INTO receipts (name, groupname, author) VALUES(?, ?, ?)", (name, groupname, author))
        con.commit()
        con.close()

        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def removeReceipt(rowid:int, username):
    # TODO: protect this function to only fire if user is in the group
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    #get owner of receipt and check to make sure it's the username
    receipt_owner = cur.execute("SELECT author FROM receipts WHERE rID=?", (rowid,)).fetchone()
    if not receipt_owner or len(receipt_owner) == 0:
        con.close()
        return True # receipt doesn't exist, ignore and say it was a success
    elif receipt_owner[0] != username:
        con.close()
        return False

    try:
        cur.execute("PRAGMA foreign_keys = ON") # allow for cascading delete
        cur.execute(f"DELETE FROM receipts WHERE rowid=?", (rowid,))
        con.commit()
        con.close()

        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def getRequests(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # TODO: if the member isn't in the group, don't let them see information (not necessary, but good practice :3)
    #if not userInGroup(groupname=groupname, member=)

    requests = cur.execute(f"SELECT rowid, requester, request FROM requests WHERE groupname=?", (groupname,)).fetchall()
    con.close()
    return requests

def newRequest(groupname, username, displayname, request):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    if userInGroup(groupname=groupname, member=username, cur=cur):
        try:
            cur.execute(f"INSERT INTO requests (groupname, requester, request) VALUES(?, ?, ?)", (groupname, displayname, request))
            con.commit()
            con.close()
            return True
        except Exception as e:
            print(e)
            con.close()
            return False
        
    con.close()
    return False

# TODO: username checks for all of these functions
def removeRequest(rid: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # TODO: try-except?

    cur.execute("PRAGMA foreign_keys = ON") # allow for cascading delete
    cur.execute(f"DELETE FROM requests WHERE rowid=?", (rid,))
    con.commit()

    con.close()
    return True

def getReceiptItems(rid):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    data = cur.execute(f"SELECT itemname, cost FROM receipt_data WHERE rID=?", (rid,)).fetchall()
    con.close()
    return data

def addReceiptItem(rid, itemname, cost:float):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    
    try:
        cur.execute(f"INSERT INTO receipt_data (rID, itemname, cost) VALUES(?, ?, ?)", (rid, itemname, cost))
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def removeReceiptItem(rid, itemname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # TODO: try-except?

    cur.execute(f"DELETE FROM receipt_data WHERE rID=? AND itemname=?", (rid, itemname))
    con.commit()

    con.close()

def getClaimedItems(rid):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    data = cur.execute(f"SELECT itemname, claimer FROM claimed_items WHERE rID=?", (rid,)).fetchall()
    con.close()
    return data

def toggleClaimItem(rid, itemname, username): # instead of "add" and "remove" for claimed functions, just make it all one function so that the client code can just use a button
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # check to see if entry already exists
    res = cur.execute(f"SELECT * FROM claimed_items WHERE rID=? AND itemname=? AND claimer=?", (rid, itemname, username)).fetchone()

    try:
        if not res or len(res) == 0:
            # entry doesn't exist, add it
            cur.execute(f"INSERT INTO claimed_items (rID, itemname, claimer) VALUES(?, ?, ?)", (rid, itemname, username))
        else:
            # entry exists, remove it
            cur.execute(f"DELETE FROM claimed_items WHERE rID=? AND itemname=? AND claimer=?", (rid, itemname, username))

        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        con.close()
        return False

def getDept(groupname, username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # get receipts in group
    receipts = cur.execute(f"SELECT rID, author FROM receipts WHERE groupname=?", (groupname,)).fetchall()

    # build dictionary from collected receipt data
    rdict = {}
    for rid, author in receipts:
        if author != username:
            rdict[rid] = author

    # get items user has claimed from each receipt
    claimed_items = {}
    for rid in rdict.keys():
        c = cur.execute(f"SELECT itemname FROM claimed_items WHERE rID=? AND claimer=?", (rid, username)).fetchall()
        claimed_items[rid] = c

    # for each claimed item:
    debts = {}
    for rid in claimed_items.keys():
        # get author of receipt
        author = cur.execute(f"SELECT author FROM receipts WHERE rID=?", (rid,)).fetchone()[0]

        for itemname in claimed_items[rid]:
            # get number of people who have also claimed same receipt items
            num_people_claimed = len(cur.execute(f"SELECT itemname FROM claimed_items WHERE rID=? AND itemname=?", (rid, itemname)).fetchall())

            # take total cost and divide among claimers
            total_cost = cur.execute(f"SELECT cost FROM receipt_data WHERE rID=? AND itemname=?", (rid, itemname)).fetchone()[0]
            
            cost = total_cost / num_people_claimed

            # add to total debt
            debts[author] = debts.get(author, 0) + cost

    # return total debt
    con.close()
    return debts

# if not _table_exists('receipts', cur):
#         cur.execute(f"""CREATE TABLE receipts(
#                         rID INTEGER NOT NULL,
#                         name varchar({MAX_GROUPNAME_LEN}),
#                         groupname varchar({MAX_GROUPNAME_LEN}),
#                         author varchar({MAX_USERNAME_LEN}),
#                         PRIMARY KEY(rID),
#                         FOREIGN KEY (groupname) REFERENCES groups(groupname) ON DELETE CASCADE
#                         )""")
#         print('Created table: receipts')
# if not _table_exists('receipt_data', cur):
#         cur.execute(f"""CREATE TABLE receipt_data(
#                         rID int,
#                         itemname varchar({MAX_RECEIPT_ITEM_LEN}) PRIMARY KEY,
#                         cost REAL,
#                         FOREIGN KEY (rID) REFERENCES receipts(rID) ON DELETE CASCADE
#                         )""")
#         print('Created table: receipt_data')
# if not _table_exists('claimed_items', cur):
#         cur.execute(f"""CREATE TABLE claimed_items(
#                         rID int,
#                         itemname varchar({MAX_RECEIPT_ITEM_LEN}),
#                         claimer varchar({MAX_USERNAME_LEN}),
#                         FOREIGN KEY (rID) REFERENCES receipts(rID) ON DELETE CASCADE
#                         )""")
#         print('Created table: claimed_items')

setupTables()