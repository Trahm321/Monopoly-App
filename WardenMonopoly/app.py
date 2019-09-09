from flask import Flask, request, render_template, redirect
from flask_material import Material
import database_handler
from forms import user_name
import os


SECRET_KEY = os.urandom(32)

app = Flask(__name__)
Material(app)
app.config['SECRET_KEY'] = SECRET_KEY

log = []

database_handler.initializer()

# Is a helper function used to change the color of the money field
def color_handler(funds):
    color = 'white'
    font_color = 'black'

    if funds >= 500:
        color = 'orange'
        font_color = 'white'
    elif funds >= 100:
        color = '#F5DD90'
        font_color = 'white'
    elif funds >= 50:
        color = '#8B5FBF'
        font_color = 'white'
    elif funds >= 20:
        color = '#D0FFD6'
        font_color = 'black'
    elif funds >= 10:
        color = '#84E3FF'
        font_color = 'white'
    elif funds >= 5:
        color = '#D7A0B8'
        font_color = 'white'

    return color, font_color

# The landing page of the app. Validates Player name and helps users navigate forward
@app.route('/', methods=['POST', 'GET'])
def index():

    # Catches disconnected users. If a user already exists in the database, they move straight to the play screen
    if request.remote_addr in database_handler.get_ip_addresses():
        return redirect('/play')

    # Ensures the names are correct and are valid. Also does not allow duplicate names
    form = user_name(request.form)
    if request.method == 'POST' and form.validate():
        if str(form.player_name._value()) in database_handler.get_user_names():
            return redirect('/')
        if request.form['player_status'] == "player":
            database_handler.user_join(str(request.remote_addr), str(form.player_name._value()),
                                       str(request.form['player_status']))
            return redirect('/join_lobby')
        else:
            if 'banker' in database_handler.get_all_players_status():
                return redirect('/')
            else:
                database_handler.user_join(str(request.remote_addr), str(form.player_name._value()),
                                           str(request.form['player_status']))
                return redirect('/banker_lobby')

    return render_template('index.html', title="main_page", form=form)

# A lobby with a list of all players. This waits until the banker initiates the game.
@app.route('/join_lobby', methods=['POST', 'GET'])
def join_lobby():
    game_status = str(database_handler.get_game_status())
    game_status = game_status[3:-4]
    if game_status == "on":
        return redirect('/play')

    player_list = database_handler.get_user_names()

    return render_template('join_lobby.html', players=player_list)

# Allows the banker to set the desired startup funds. Afterwards they may start the game.
@app.route('/banker_lobby', methods=['POST', 'GET'])
def banker_lobby():
    if request.method == 'POST':
        starting_funds = request.form['startup_funds']
        database_handler.set_game_status()
        database_handler.set_starting_funds(starting_funds)
        return redirect('/play')

    player_list = database_handler.get_user_names()

    return render_template('banker_lobby.html', players=player_list)


@app.route('/play', methods=['POST', 'GET'])
def play_screen():
    # If the game isn't running, redirects to the landing page
    game_status = str(database_handler.get_game_status())
    game_status = game_status[3:-4]
    if game_status == "off":
        return redirect('/')
    if game_status == "on" and request.remote_addr not in database_handler.get_ip_addresses():
        return redirect('/')

    # Gets user data based on their IP address.
    funds = database_handler.get_funds(str(request.remote_addr))
    color, font_color = color_handler(funds)
    player_list = database_handler.get_user_names()
    removed_player_list = database_handler.get_user_names()
    player_status = database_handler.get_player_status(request.remote_addr)
    if database_handler.ip_to_name(request.remote_addr) in player_list:
        removed_player_list.remove(database_handler.ip_to_name(request.remote_addr))

    return render_template('play_screen.html', funds=funds, full_players=player_list,
                           removed_players=removed_player_list,  player_type=player_status[0], color=color,
                           font_color=font_color)


# A checker to ensure the transfer being made are valid
@app.route('/fund_transfer', methods=['POST', 'GET'])
def fund_transfer():
    # Need to make this better! The logic might be flawed. Also need to add error alerts through flask.
    if request.form['send_amount'] != "":
        send_amount = int(request.form['send_amount'])
    else:
        send_amount = ""

    try:
        receiver = request.form['receiver']
    except:
        receiver = ""

    sender = request.remote_addr
    if send_amount == "" or receiver == 'null' or database_handler.has_enough(send_amount, sender) is False or \
            database_handler.name_to_ip(receiver) == sender or receiver == "":
        return redirect('/play')

    database_handler.move_money(sender, receiver, send_amount)
    if receiver == 'bank':
        log_message = database_handler.ip_to_name(sender) + " has sent $" + str(send_amount) + " to the Bank"
    elif receiver == 'free_parking':
        log_message = database_handler.ip_to_name(sender) + " has sent $" + str(send_amount) + " to Free Parking"
    else:
        log_message = database_handler.ip_to_name(sender) + " has sent $" + str(send_amount) + " to " + receiver
    log.insert(0, log_message)
    return redirect('/play')


# The handler for the log page. All transactions are logged.
@app.route('/logs')
def logs():
    funds = database_handler.get_free_parking()
    color, font_color = color_handler(funds)

    return render_template('log.html', log=log, funds=funds, color=color, font_color=font_color)


# Handler for if a user passes go.
@app.route('/pass_go', methods=['GET', 'POST'])
def pass_go():
    try:
        receiver = request.form['receiver']
    except:
        return redirect('/play')

    database_handler.bank_pays_player(receiver, 200)
    log_message = receiver + " has passed go"
    log.insert(0, log_message)
    return redirect('play')


# Handler for when the bank pays a player
@app.route('/bank_pays', methods=['GET', 'POST'])
def bank_pays():

    try:
        receiver = request.form['receiver']
    except:
        return redirect('/play')

    if request.form['send_amount'] != "":
        send_amount = int(request.form['send_amount'])
    else:
        send_amount = ""

    database_handler.bank_pays_player(receiver, send_amount)
    log_message = receiver + " has received $" + str(send_amount) + " from the Bank"
    log.insert(0, log_message)
    return redirect('/play')


# Handler for when a player wins the lottery
@app.route('/lotto_pays', methods=['GET', 'POST'])
def lotto_pays():
    try:
        receiver = request.form['receiver']
    except:
        return redirect('/play')
    database_handler.bank_pays_player(receiver, database_handler.get_free_parking())
    log_message = receiver + f" has won the lottery for ${database_handler.get_free_parking()}!!"
    database_handler.set_free_parking(0)

    log.insert(0, log_message)
    return redirect('play')


if __name__ == '__main__':
    # Please change the host and port to ur desired IP address and port.
    app.run(debug=True, host='0.0.0.0', port='8000')
