# SQLITE Handler. Is used as the backend. All the functions here are helper functions.

import sqlite3


# Creates the database file just in case you delete it
def create_database():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('CREATE TABLE game(game_num INT PRIMARY KEY, game_status VARCHAR, starting_funds INT,'
              ' free_parking_funds INT)')
    c.execute('CREATE TABLE users(ip_address VARCHAR,player_name VARCHAR PRIMARY KEY, player_funds INT, player_status VARCHAR)')
    c.execute('INSERT INTO game VALUES(1, "off", 0, 0)')
    conn.commit()
    conn.close()


# Shows the contents of the users table
def show_all():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('SELECT * FROM game')
    c.execute('SELECT * FROM users')
    all_rows = c.fetchall()
    print(all_rows)
    conn.commit()
    conn.close()


# Initializes the database by deleting all rows from tables.
def initializer():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('DELETE FROM game')
    c.execute('DELETE FROM users')
    c.execute('INSERT INTO game VALUES(1, "off", 0, 0)')
    conn.commit()
    conn.close()


# Adds a user along with IP Address, name and status to the users table.
def user_join(ip_add, player_name, player_status):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    statement = f'INSERT INTO users VALUES("{ip_add}", "{player_name}", 0, "{player_status}")'
    c.execute(statement)
    conn.commit()
    conn.close()


# Gets a list of all the players in the game.
def get_user_names():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('SELECT player_name FROM users')
    all_names = c.fetchall()
    conn.commit()
    conn.close()

    player_list = []

    for player in all_names:
        player_list.append(player[-1])

    return player_list


# Sets the game status to on.
def set_game_status():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('UPDATE game SET game_status = "on" WHERE game_status="off"')
    conn.commit()
    conn.close()


# Gets the game status from the game table.
def get_game_status():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('SELECT game_status from game')
    game_status = c.fetchall()
    conn.commit()
    conn.close()

    return game_status


# Sets starting funds to desired amount.
def set_starting_funds(funds):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'UPDATE users SET player_funds = {funds} WHERE player_funds = 0')
    conn.commit()
    conn.close()


# Gets a specific players funds by IP address
def get_funds(ip_add):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT player_funds FROM users WHERE ip_address = "{ip_add}"')
    funds = c.fetchall()
    conn.commit()
    conn.close()

    for money in funds:
        return money[-1]


# Sets a specific players funds by IP address.
def set_player_funds(funds, player_ip):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'UPDATE users SET player_funds = {funds} WHERE ip_address = "{player_ip}"')
    conn.commit()
    conn.close()


# Gets a players status
def get_player_status(ip_add):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT player_status FROM users WHERE ip_address = "{ip_add}"')
    all = c.fetchall()
    conn.commit()
    conn.close()

    status = []

    for player in all:
        status.append(player[-1])

    return status


# Gets all IP addresses in the game.
def get_ip_addresses():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT ip_address FROM users')
    all = c.fetchall()
    conn.commit()
    conn.close()

    addresses = []
    for address in all:
        addresses.append(address[-1])

    return addresses


# Converts from IP address to name of player.
def ip_to_name(ip_add):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT player_name FROM users WHERE ip_address = "{ip_add}"')
    all = c.fetchall()
    conn.commit()
    conn.close()

    for player in all:
        return player[-1]



# Converts from name to ip address of player.
def name_to_ip(name):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT ip_address FROM users WHERE player_name = "{name}"')
    all = c.fetchall()
    conn.commit()
    conn.close()

    for ip_add in all:
        return ip_add[-1]


# Checks if a player has enough money by IP address.
def has_enough(amount, ip_add):
    funds = get_funds(ip_add)
    if funds - amount <= 0:
        return False
    else:
        return True


def set_free_parking(amount):
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'UPDATE game SET free_parking_funds = {amount}')
    conn.commit()
    conn.close()


def get_free_parking():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute('SELECT free_parking_funds FROM game')
    all = c.fetchall()
    conn.commit()
    conn.close()

    for ip_add in all:
        return ip_add[-1]

# Moves Money from sender to receiver.
def move_money(sender, receiver, amount):
    if receiver == 'bank':
        set_player_funds(get_funds(sender) - amount, sender)
    elif receiver == 'free_parking':
        set_player_funds(get_funds(sender) - amount, sender)
        set_free_parking(amount + int(get_free_parking()))
    else:
        receiver = name_to_ip(receiver)
        set_player_funds(get_funds(sender) - amount, sender)
        set_player_funds(get_funds(receiver) + amount, receiver)


# Gives a player either $200 (Go money) or lotto money
def bank_pays_player(receiver, amount):
    receiver = name_to_ip(receiver)
    set_player_funds(get_funds(receiver) + amount, receiver)


def get_all_players_status():
    sqlite_file = 'monopoly_money.sqlite'
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    c.execute(f'SELECT player_status FROM users')
    all = c.fetchall()
    conn.commit()
    conn.close()

    statuses = []
    for status in all:
        statuses.append(status[-1])

    return statuses