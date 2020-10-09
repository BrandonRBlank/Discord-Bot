
def add_casino(conn, userId):
    sql = "INSERT INTO CasinoUserData VALUES(?,?,?,?,?,?)"
    cur = conn.cursor()
    cur.execute(sql, (userId, 0, 0, 0, 0, 0))
    conn.commit()
    return


def get_player_bank(conn, userId):
    sql = "SELECT bank FROM Users WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (userId,))
    return cur.fetchone()[0]


def update_jackpot(conn, serverId, amount, empty=False):
    sql = "UPDATE Servers SET jackpot=jackpot+? WHERE server_id=?"
    if empty:
        sql = "UPDATE Servers SET jackpot=? WHERE server_id=?"

    cur = conn.cursor()
    cur.execute(sql, (amount, serverId))
    conn.commit()
    return


def get_jackpot(conn, serverId):
    sql = "SELECT jackpot FROM Servers WHERE server_id=?"
    cur = conn.cursor()
    cur.execute(sql, (serverId,))
    return cur.fetchone()[0]


def set_player_plays(conn, userId, game):
    sql = ""
    if game == "slots":
        sql = "UPDATE CasinoUserData SET slots_plays=slots_plays+1 WHERE user_id=?"
    elif game == "blackjack":
        sql = "UPDATE CasinoUserData SET blackjack_plays=blackjack_plays+1 WHERE user_id=?"
    elif game == "dice":
        sql = "UPDATE CasinoUserData SET dice_plays=dice_plays+1 WHERE user_id=?"

    cur = conn.cursor()
    cur.execute(sql, (userId,))

    conn.commit()
    return


def add_funds(conn, playerId, amount):
    sql = "UPDATE Users SET bank=bank+? WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (amount, playerId))
    conn.commit()
    return


def remove_funds(conn, playerId, amount):
    sql = "UPDATE Users SET bank=bank-? WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (amount, playerId))
    conn.commit()
    return


def update_money_won(conn, userId, amount):
    sql = "UPDATE CasinoUserData SET money_won=money_won+? WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (amount, userId))
    conn.commit()
    return


def update_money_lost(conn, userId, amount):
    sql = "UPDATE CasinoUserData SET money_lost=money_lost+? WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (amount, userId))
    conn.commit()
    return


def get_player_stats(conn, userId):
    sql = "SELECT * FROM CasinoUserData WHERE user_id=?"
    cur = conn.cursor()
    cur.execute(sql, (userId,))
    return cur.fetchall()[0]
