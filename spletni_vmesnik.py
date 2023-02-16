import bottle
#import model
from bottle import get, post, template, request
import sqlite3

#glavni_model = model.Model()

@get('/')
def index():
    name = "Aljaž"
    return bottle.template("index.html", name=name)


@get('/pregled_baze')
def pregled_baze():
    cur.execute("SELECT * FROM Country limit 10;")
    Country = cur.fetchall()
    cur.execute("SELECT * FROM League limit 10;")
    League = cur.fetchall()
    cur.execute("SELECT * FROM Match limit 10;")
    Match = cur.fetchall()
    cur.execute("SELECT * FROM Player limit 10;")
    #cur.execute("SELECT count(*) FROM Player where team_id not null;")
    Player = cur.fetchall()
    cur.execute("SELECT * FROM Player_Attributes limit 10;")
    Player_Attributes = cur.fetchall()
    cur.execute("SELECT * FROM Team;")
    Team = cur.fetchall()
    cur.execute("SELECT * FROM Team_Attributes limit 10;")
    Team_Attributes = cur.fetchall()
    return bottle.template("pregled_tabel.html", Country=Country, League=League, Match=Match, Player=Player, Player_Attributes=Player_Attributes, Team=Team, Team_Attributes=Team_Attributes)



@get('/uredi_ekipo')
def uredi_ekipo():
    cur.execute("SELECT * FROM Player;")
    Player = cur.fetchall()
    return bottle.template("igralci.html", Player = Player)


@get('/lestvica')
def izberi_lestico():
    cur.execute("SELECT name FROM League;")
    leagues = cur.fetchall()
    return bottle.template("liga.html", ekipe=[])

@post('/lestvica')
def do_lestvica():
    league_id = request.forms.get('liga')
    sezona = request.forms.get('sezona')

    s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
    res = cur.execute(s)
    teams = [(long_name, short_name) for long_name, short_name in res.fetchall()]

    return bottle.template("liga.html", ekipe=teams)


#da izpiše vse igralce
@get('/ekipa/<ime_ekipe>')
def ekipa(ime_ekipe):
    team_api_id = 4087
    print(ime_ekipe)
    s = f"SELECT player_name FROM Player JOIN Team ON Player.team_id = Team.team_api_id WHERE Team.team_long_name = '{ime_ekipe}'"
    res = cur.execute(s)
    igralci = res.fetchall()
    return bottle.template("ekipa.html", ime_ekipe=ime_ekipe, igralci = igralci)



# @post('/lestvica')
# def do_lestvica():
#     league_id = request.forms.get('liga')
#     sezona = request.forms.get('sezona')
#     print(league_id, sezona)
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return bottle.template("lestvica.html", ekipe=teams)

@get('/lestvica/<league_id>')
def lestvica(league_id):
    s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
    res = cur.execute(s)
    teams = res.fetchall()
    print(teams)
    return bottle.template("lestvica.html", ekipe=teams)



baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()

bottle.run(debug=True, reloader=True)



# import bottle
# import model

# glavni_model = model.Model()

# @bottle.route("/static/slikice/<filename>")    #ZA SLIKO
# def serve_static_files(filename):
#     return bottle.static_file(filename, root="./static/img")  

# @bottle.route("/static/css/<filename>")    #ZA RDEČO barvo, dodamo to kar mamo na datoteki style.css
# def serve_static_files(filename):
#     return bottle.static_file(filename, root="./static/css") 

# @bottle.get("/")
# def glavna_stran():
    
#     podatki = glavni_model.dobi_vse_uporabnike()
    
#     return bottle.template(
#         "glavna.html", uporabniki=podatki
#         )




# bottle.run(debug=True, reloader=True)