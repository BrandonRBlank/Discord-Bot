import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(str(e) + " in create_connection")
    return None


def create_table(conn, sql):
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Error as e:
        print(str(e) + " in create_table")


def delete_table(conn, sql):
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Error as e:
        print(str(e) + " in delete_table")


def make_data(conn, sql, userdata):
    cur = conn.cursor()
    try:
        cur.execute(sql, userdata)
        return 0
    except Error as e:
        print(str(e))
        return 1


def set_data(db_file, sql, items):  # dataChange, ident):
    conn = create_connection(db_file)
    curr = conn.cursor()
    curr.execute(sql, items)
    conn.commit()
    conn.close()


def fetch_user_data(db_file, sql, items):
    try:
        conn = create_connection(db_file)
        curr = conn.cursor()
        curr.execute(sql, items)
        data = curr.fetchone()[0]
        conn.close()
        return data
    except TypeError:
        print("ERROR! DB not created yet ('fetch_user_data')")


def fetch_all(db_file, sql, items):
    try:
        conn = create_connection(db_file)
        curr = conn.cursor()
        curr.execute(sql, items)
        data = curr.fetchall()
        conn.close()
        return data
    except TypeError:
        print("ERROR! ('fetch_all')")

# -------------------------------------------------------------------------


# def make_web_user(conn, user):
#     sql = "INSERT INTO WebUsers VALUES(?,?,?)"
#     cur = conn.cursor()
#     cur.execute(sql, user)
#     conn.commit()
#     return


# def make_user_server(conn, servers):
#     sql = "INSERT INTO UserServers VALUES(?,?,?,?)"
#     cur = conn.cursor()
#     cur.execute(sql, servers)
#     conn.commit()
#     return


# def make_members_table(conn, server):
#     sql = "CREATE TABLE IF NOT EXISTS {} (Username TEXT, UserID INTEGER)".format("s" + str(server))
#     cur = conn.cursor()
#     cur.execute(sql)
#     conn.commit()
#     return


# def get_members_table(conn, serverId):
#     sql = "SELECT Username FROM {}".format("s" + str(serverId))
#     cur = conn.cursor()
#     cur.execute(sql)
#     return cur.fetchall()


def add_users(conn, serverId, username, userId):
    sql = "INSERT INTO ServerUsers VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (userId, username, serverId))
    conn.commit()
    return


def add_channel(conn, serverId, channelName, channelId):
    sql = "INSERT INTO ServerChannels VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (channelId, channelName, serverId))
    return


def add_server(conn, serverId, serverName, ownerId, ownerName, serverIcon):
    sql = "INSERT INTO BotServers VALUES(?,?,?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, serverName, ownerId, ownerName, serverIcon))
    conn.commit()
    return


def get_owner(conn, userId, serverId):
    sql = "SELECT owner_id FROM BotServers WHERE owner_id=? AND server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (userId, serverId))
    try:
        return cur.fetchone()[0]
    except TypeError:
        return False


# TODO: need sql refactoring because of schema change (both fetch_servers and fetch_server_id)
# returns array of 2-tuples
def fetch_servers(conn, id):
    sql = "SELECT ServerName,ServerIcon,ServerID FROM UserServers WHERE UserID={}".format(id)
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def fetch_server_id(conn, name, userId):
    #sql = "SELECT ServerID FROM UserServers WHERE ServerName={} AND UserID={}".format(name, userId)
    sql = "SELECT ServerID FROM UserServers WHERE ServerName=? AND UserID=?"
    cur = conn.cursor()
    cur.execute(sql, (name, userId))
    return cur.fetchone()[0]
