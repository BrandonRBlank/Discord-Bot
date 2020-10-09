import sqlite3
from sqlite3 import Error
from sqlite3 import IntegrityError, OperationalError


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(str(e) + " in create_connection")
    return None

# -------------------------------------------------------------------------


def add_user(conn, serverId, userId, username):
    sql_users = "INSERT OR IGNORE INTO Users VALUES(?,?,?)"
    sql_connect = "INSERT OR IGNORE INTO UserOn VALUES(?,?)"
    cur = conn.cursor()

    cur.execute(sql_users, (userId, username, 250))
    cur.execute(sql_connect, (serverId, userId))

    conn.commit()
    return


def remove_user(conn, serverId, userId):
    sql_connect = "DELETE FROM UserOn WHERE server_id=? AND user_id=?"
    sql_users = "DELETE FROM Users WHERE user_id=?"
    sql_check_connect = "SELECT * FROM UserOn WHERE user_id=?"
    cur = conn.cursor()

    cur.execute(sql_connect, (serverId, userId))

    cur.execute(sql_check_connect, (userId,))
    duplicate = cur.fetchone()
    if duplicate is None:
        cur.execute(sql_users, (userId,))

    conn.commit()
    return


def add_channel(conn, serverId, channelId, channelName):
    sql_channels = "INSERT OR IGNORE INTO Channels VALUES(?,?)"
    sql_connect = "INSERT OR IGNORE INTO ChannelOn VALUES (?,?)"
    sql_check_connect = "SELECT * FROM ChannelOn WHERE server_id=? AND channel_id=?"
    cur = conn.cursor()

    cur.execute(sql_check_connect, (serverId, channelId))
    duplicate = cur.fetchone()

    cur.execute(sql_channels, (channelId, channelName))

    if duplicate is None:
        cur.execute(sql_connect, (serverId, channelId))

    conn.commit()
    return


def remove_channel(conn, channelId):
    sql_connect = "DELETE FROM ChannelOn WHERE channel_id=?"
    sql_channels = "DELETE FROM Channels WHERE channel_id=?"
    cur = conn.cursor()

    cur.execute(sql_connect, (channelId,))
    cur.execute(sql_channels, (channelId,))

    conn.commit()
    return


def update_channel(conn, channelId, channelName):
    sql_channel = "UPDATE Channels SET channel_name=? WHERE channel_id=?"
    sql_permission = "UPDATE AllowedChannels SET channel_name=? WHERE channel_id=?"
    cur = conn.cursor()

    cur.execute(sql_channel, (channelName, channelId))
    cur.execute(sql_permission, (channelName, channelId))

    conn.commit()
    return


def get_channels(conn, serverId):
    sql = "SELECT Channels.channel_id, Channels.channel_name " \
          "FROM Channels, ChannelOn " \
          "WHERE ChannelOn.server_id=? AND Channels.channel_id=ChannelOn.channel_id"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        channels = cur.fetchall()
        # channels = [x[0] for x in channels]
        return channels
    except TypeError:
        return


def add_server(conn, serverId, serverName, ownerId, ownerName, serverIcon, prefix="!"):
    sql = "INSERT INTO Servers VALUES(?,?,?,?,?,?,?)"
    cur = conn.cursor()
    try:
        cur.execute(sql, (serverId, serverName, ownerId, ownerName, serverIcon, prefix, 0))
    except IntegrityError:
        sql = "UPDATE Servers SET server_name=?, owner_name=?, server_icon=?, prefix=?, jackpot=0 WHERE server_id=?"
        cur.execute(sql, (serverName, ownerName, serverIcon, prefix, serverId))
    conn.commit()
    return


def add_channel_permission(conn, serverId, channelId, channelName):
    sql = "INSERT OR IGNORE INTO AllowedChannels VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, channelId, channelName))
    conn.commit()
    return


def get_channel_permission(conn, serverId):
    sql = "SELECT channel_id, channel_name FROM AllowedChannels WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        channels = cur.fetchall()
        return channels
    except TypeError:
        return


def remove_channel_permission(conn, channelId):
    sql = "DELETE FROM AllowedChannels WHERE channel_id=?"
    cur = conn.cursor()

    try:
        cur.execute(sql, (channelId,))
    except OperationalError:
        return

    conn.commit()
    return


def add_stream_channel(conn, serverId, channelId, channelName):
    sql = "INSERT OR IGNORE INTO StreamChannels VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, channelId, channelName))
    conn.commit()
    return


def get_stream_channel(conn, serverId):
    sql = "SELECT channel_id, channel_name FROM StreamChannels WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        channels = cur.fetchall()
        return channels
    except TypeError:
        return


def remove_stream_channel(conn, channelId):
    sql = "DELETE FROM StreamChannels WHERE channel_id=?"
    cur = conn.cursor()

    try:
        cur.execute(sql, (channelId,))
    except OperationalError:
        return

    conn.commit()
    return


def add_casino_channel(conn, serverId, channelId, channelName):
    sql = "INSERT OR IGNORE INTO CasinoChannels VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, channelId, channelName))
    conn.commit()
    return


def get_casino_channel(conn, serverId):
    sql = "SELECT channel_id, channel_name FROM CasinoChannels WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        channels = cur.fetchall()
        return channels
    except TypeError:
        return


def remove_casino_channel(conn, channelId):
    sql = "DELETE FROM CasinoChannels WHERE channel_id=?"
    cur = conn.cursor()

    try:
        cur.execute(sql, (channelId,))
    except OperationalError:
        return

    conn.commit()
    return


def set_prefix(conn, new, serverId):
    sql = "UPDATE Servers SET prefix=? WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (new, serverId))
    conn.commit()
    return


def get_prefix(conn, serverId):
    sql = "SELECT prefix FROM Servers WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    return cur.fetchone()


def add_streamer(conn, serverId, userId, userName):
    sql = "INSERT OR IGNORE INTO Streamer VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, userId, userName))
    conn.commit()
    return


def get_streamer(conn, serverId):
    sql = "SELECT user_id, user_name FROM Streamer WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        channels = cur.fetchall()
        return channels
    except TypeError:
        return


def remove_streamer(conn, serverId, userId):
    sql = "DELETE FROM Streamer WHERE server_id=? AND user_id=?"
    cur = conn.cursor()

    try:
        cur.execute(sql, (serverId, userId))
    except OperationalError:
        return

    conn.commit()
    return


def add_blacklist_user(conn, serverId, userId, userName):
    sql = "INSERT OR IGNORE INTO BlacklistUsers VALUES(?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (serverId, userId, userName))
    conn.commit()
    return


def get_blacklist_users(conn, serverId):
    sql = "SELECT user_id,user_name FROM BlacklistUsers WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    try:
        users = cur.fetchall()
        return users
    except TypeError:
        return


def remove_blacklist_user(conn, serverId, userId):
    sql = "DELETE FROM BlacklistUsers WHERE server_id=? AND user_id=?"
    cur = conn.cursor()

    try:
        cur.execute(sql, (serverId, userId))
    except OperationalError:
        return

    conn.commit()
    return


def get_ow_rank(conn, level):
    sql = "SELECT link from Data WHERE rank <= {} ORDER BY rank DESC LIMIT 5".format(level)
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]


# WEB FUNCTIONS --------------------------------------------------------------------------------------------------------

def fetch_servers(conn, userId):
    sql = "SELECT server_id,server_name,server_icon FROM Servers WHERE owner_id=?"
    cur = conn.cursor()
    cur.execute(sql, (userId,))
    return cur.fetchall()


def fetch_server_id(conn, userId, serverName):
    sql = "SELECT server_id FROM Servers WHERE owner_id=? AND server_name=?"
    cur = conn.cursor()
    cur.execute(sql, (userId, serverName))
    return cur.fetchone()[0]


def get_stats_count(conn):
    sql_servers = "SELECT COUNT(server_id) FROM Servers"
    sql_channels = "SELECT COUNT(channel_id) FROM Channels"
    sql_users = "SELECT COUNT(user_id) FROM Users"
    cur = conn.cursor()

    return (
        cur.execute(sql_servers).fetchone()[0],
        cur.execute(sql_channels).fetchone()[0],
        cur.execute(sql_users).fetchone()[0]
    )


def get_users(conn, serverId):
    sql = "SELECT Users.user_name, Users.user_id " \
          "FROM UserOn, Users " \
          "WHERE UserOn.server_id=? AND UserOn.user_id=Users.user_id"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    return cur.fetchall()
