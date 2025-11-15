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
    cur = sqlite3.connect(DB_NAME).cursor()

    # make sure each table exists and if not, create it
    if not _table_exists('groups', cur):
        cur.execute(f"""CREATE TABLE groups(
                        groupname varchar({MAX_GROUPNAME_LEN}) PRIMARY KEY,
                        owner varchar({MAX_USERNAME_LEN}),
                        public int
                    )
                    """)
        print('Created table: groups')
    
    if not _table_exists('receipt_data', cur):
        cur.execute(f"""CREATE TABLE receipt_data(
                        rnum PRIMARY KEY,
                        groupname,
                        owner varchar({MAX_USERNAME_LEN})
                    )""")
        print('Created table: receipts')

    if not _table_exists('group_members', cur):
        cur.execute(f"""CREATE TABLE group_members(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        membername varchar({MAX_USERNAME_LEN})
                    )""")
        print('Created table: group_members')

    if not _table_exists('receipts', cur):
        cur.execute(f"""CREATE TABLE receipts(
                        name varchar({MAX_GROUPNAME_LEN}),
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        author varchar({MAX_USERNAME_LEN})
                        )""")
        print('Created table: receipts')

    if not _table_exists('receipt_data', cur):
        cur.execute(f"""CREATE TABLE receipt_data(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}),
                        cost REAL
                        )""")
        print('Created table: receipt_data')

    if not _table_exists('claimed_items', cur):
        cur.execute(f"""CREATE TABLE claimed_items(
                        rID int,
                        itemname varchar({MAX_RECEIPT_ITEM_LEN}),
                        claimer varchar({MAX_USERNAME_LEN})
                        )""")
        
    if not _table_exists('requests', cur):
        cur.execute(f"""CREATE TABLE requests(
                        groupname varchar({MAX_GROUPNAME_LEN}),
                        requester varchar({MAX_USERNAME_LEN}),
                        request varchar({MAX_REQUEST_LEN})
                        )""")

def getGroups(username):
    # get all of the groups that the user has access to 
    cur = sqlite3.connect(DB_NAME).cursor()
    groups = cur.execute("SELECT groupname FROM groups").fetchall()
    joined = cur.execute(f"SELECT groupname FROM group_members WHERE membername='{username}'").fetchall()

    res = [[group, group in joined] for group in groups]
    return res

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
        return True
    except Exception as e:
        print(e)
        return False
    
def joinGroup(groupname, username):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    # check to make sure the username has permission to join or is already joined
    isPublic = cur.execute(f"SELECT public FROM groups WHERE groupname='{groupname}'").fetchone()
    if not isPublic[0]:
        return False

    already_joined = cur.execute(f"SELECT * FROM group_members WHERE groupname='{groupname}' AND membername='{username}'").fetchall()
    if len(already_joined) != 0:
        return True # return true as a safeguard from duplicate joins

    # user has permission and isn't already joined, add them to the database
    try:
        # execute join command and commit changes
        cur.execute("INSERT INTO group_members (groupname, membername) VALUES" \
                        f"('{groupname}', '{username}')")
        con.commit()
        return True
    except Exception as e:
        print(e)
        return False

def getMembers(groupname):
    cur = sqlite3.connect(DB_NAME).cursor()

    # make sure group exists
    group = cur.execute(f"SELECT owner FROM groups WHERE groupname='{groupname}'").fetchone()
    if len(group) == 0:
        return 'DNE', []
    
    owner = group[0]
    members = cur.execute(f"SELECT membername FROM group_members WHERE groupname='{groupname}'").fetchall()
    members.remove(owner) # no need to list the owner as a member since they literally own the group lol
    return owner, members

def getReceipts(groupname):
    cur = sqlite3.connect(DB_NAME).cursor()

    receipts = cur.execute(f"SELECT * FROM receipts WHERE groupname='{groupname}'").fetchall()
    return receipts

def newReceipt(groupname, name, author):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    try:
        cur.execute(f"INSERT INTO receipts (name, groupname, author) VALUES('{name}', '{groupname}', '{author}')")
        con.commit()

        return True
    except Exception as e:
        print(e)
        return False

setupTables()