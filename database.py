import sqlite3

DB_NAME = 'groceries.db'

MAX_GROUPNAME_LEN = 50
MAX_USERNAME_LEN = 50
MAX_RECEIPT_ITEM_LEN = 100
MAX_REQUEST_LEN = 200

def _table_exists(name, cur):
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
    return not res.fetchone() is None

def setupTables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # make sure each table exists and if not, create it
    if not _table_exists('groups', cur):
        cur.execute(f"""CREATE TABLE groups(
                        groupname varchar({MAX_GROUPNAME_LEN}) PRIMARY KEY,
                        owner varchar({MAX_USERNAME_LEN}),
                        public int
                    )
                    """)
        print('Created table: groups')
    
    if not _table_exists('group_members', cur):
        cur.execute(f"""CREATE TABLE group_members(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        membername varchar({MAX_USERNAME_LEN}),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname)
                    )""")
        print('Created table: group_members')

    if not _table_exists('receipts', cur):
        cur.execute(f"""CREATE TABLE receipts(
                        name varchar({MAX_GROUPNAME_LEN}),
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        author varchar({MAX_USERNAME_LEN}),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname)
                        )""")
        print('Created table: receipts')

    if not _table_exists('receipt_data', cur):
        cur.execute(f"""CREATE TABLE receipt_data(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}),
                        cost REAL,
                        FOREIGN KEY (rID) REFERENCES receipts(rowid)
                        )""")
        print('Created table: receipt_data')

    if not _table_exists('claimed_items', cur):
        cur.execute(f"""CREATE TABLE claimed_items(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}),
                        claimer varchar({MAX_USERNAME_LEN}),
                        FOREIGN KEY (rID) REFERENCES receipts(rowid)
                        )""")
        print('Created table: claimed_items')
        
    if not _table_exists('requests', cur):
        cur.execute(f"""CREATE TABLE requests(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        requester varchar({MAX_USERNAME_LEN}),
                        request varchar({MAX_REQUEST_LEN}),
                        FOREIGN KEY (groupname) REFERENCES groups(groupname)
                        )""")
        print('Created table: requests')
    
    con.close()

def getGroups(username):
    # get all of the groups that the user has access to 
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    groups = cur.execute("SELECT groupname FROM groups").fetchall()
    joined = cur.execute(f"SELECT groupname FROM group_members WHERE membername='{username}'").fetchall()

    con.close()

    res = [[group, group in joined] for group in groups]
    return res

def userIsOwnerOfGroup(groupname, username, cur=None):
    con = None
    if not cur:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

    owner = cur.execute(f"SELECT owner FROM groups WHERE groupname='{groupname}'")
    if con:
        con.close
    return len(owner) != 0 and owner[0] == username

def userInGroup(groupname, member, cur=None):
    con = None
    if not cur:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

    already_joined = cur.execute(f"SELECT * FROM group_members WHERE groupname='{groupname}' AND membername='{member}'").fetchall()

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

    # TODO: have more checks to avoid SQL code injections and such

    try:
        cur.execute("INSERT INTO groups (groupname, owner, public) VALUES" \
                    f"('{groupname}', '{ownername}', {1 if public else 0})")
        cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                    f"('{groupname}', '{ownername}')")
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
    isPublic = cur.execute(f"SELECT public FROM groups WHERE groupname='{groupname}'").fetchone()
    if not isPublic[0]:
        return False

    if userInGroup(groupname=groupname, member=username, cur=cur):
        return True # return true as a safeguard from duplicate joins

    # user has permission and isn't already joined, add them to the database
    try:
        # execute join command and commit changes
        cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                        f"('{groupname}', '{username}')")
        con.commit()
        con.close()
        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def deleteGroup(groupname, username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    if userIsOwnerOfGroup(groupname, username):
        con.commit()

    con.close()

def getMembers(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # make sure group exists
    group = cur.execute(f"SELECT owner FROM groups WHERE groupname='{groupname}'").fetchone()
    if len(group) == 0:
        return 'DNE', []
    
    owner = group[0]
    members = cur.execute(f"SELECT membername FROM group_members WHERE groupname='{groupname}'").fetchall()
    con.close()

    members.remove(owner) # no need to list the owner as a member since they literally own the group lol
    return owner, members

def getReceipts(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    receipts = cur.execute(f"SELECT * FROM receipts WHERE groupname='{groupname}'").fetchall()
    con.close()
    return receipts

def newReceipt(groupname, name, author):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    try:
        cur.execute(f"INSERT INTO receipts (name, groupname, author) VALUES('{name}', '{groupname}', '{author}')")
        con.commit()
        con.close()

        return True
    except Exception as e:
        print(e)
        con.close()
        return False
    
def removeReceipt(groupname, name):
    # TODO: protect this function to only fire if user is in the group
    pass
    
def getRequests(groupname):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # TODO: if the member isn't in the group, don't let them see information (not necessary, but good practice :3)
    #if not userInGroup(groupname=groupname, member=)

    requests = cur.execute(f"SELECT rowid, requester, request FROM requests WHERE groupname='{groupname}'").fetchall()
    con.close()
    return requests

def newRequest(groupname, username, displayname, request):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    if userInGroup(groupname=groupname, member=username, cur=cur):
        try:
            cur.execute(f"INSERT INTO requests (groupname, requester, request) VALUES('{groupname}', '{displayname}', '{request}')")
            con.commit()
            con.close()

            return True
        except Exception as e:
            print(e)
        
    con.close()
    return False

def removeRequest(rid: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute(f"DELETE FROM requests WHERE rowid={rid}")
    con.commit()

    con.close()

setupTables()