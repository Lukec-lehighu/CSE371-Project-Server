import sqlite3

DB_NAME = 'groceries.db'
MAX_GROUPNAME_LEN = 50
MAX_USERNAME_LEN = 50

def _table_exists(name, cur):
    res = cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{name}'")
    return not res.fetchone() is None

def setupTables():
    cur = sqlite3.connect(DB_NAME).cursor()
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

setupTables()