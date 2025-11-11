import sqlite3

DB_NAME = 'groceries.db'
MAX_GROUPNAME_LEN = 50
MAX_OWNERNAME_LEN = 50

def setupTables():
    cur = sqlite3.connect(DB_NAME).cursor()
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='groups'")
    if res.fetchone() is None:
        cur.execute(f"""CREATE TABLE groups(
                        groupname varchar({MAX_GROUPNAME_LEN}) PRIMARY KEY,
                        owner varchar({MAX_GROUPNAME_LEN})
                    )
                    """)
        print('Created table: groups')
    
    res = cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='receipts'")
    if res.fetchone() is None:
        cur.execute("CREATE TABLE receipts(rnum, groupname, owner, items, prices, members paid)")
        print('Created table: receipts')

def getGroups():
    cur = sqlite3.connect(DB_NAME).cursor()
    res = cur.execute("SELECT * FROM groups")
    return res.fetchall()

def newGroup(groupname, ownername):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    # Trim names if necessary
    if len(groupname) > MAX_GROUPNAME_LEN:
        groupname = groupname[0:MAX_GROUPNAME_LEN]
    if len(ownername) > MAX_OWNERNAME_LEN:
        ownername = ownername[0:MAX_OWNERNAME_LEN]

    # TODO: have more checks to avoid SQL code injections and such

    try:
        cur.execute("INSERT INTO groups (groupname, owner) VALUES" \
                    f"('{groupname}', '{ownername}')")
        con.commit()
        return True
    except:
        return False

setupTables()