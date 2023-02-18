import bottle
import model
from bottle import *
import sqlite3

#glavni_model = model.Model()
POZICIJE = {1:"GK", 2:"DEF", 3:"DEF", 4:"DEF", 5:"DEF", 6:"MID", 7:"MID", 8:"MID", 9:"ATK", 10:"ATK", 11:"ATK"}

@get('/')
def index():
    # TODO namesto * napisem ustrezne stolpce
    s = "SELECT * FROM Player WHERE team_id = 50000;"
    cur.execute(s)
    moji_igralci = cur.fetchall()
    s = "SELECT team_long_name FROM Team WHERE team_api_id = 50000;"
    cur.execute(s)
    ime_ekipe = cur.fetchone()
    return bottle.template("moja_ekipa.html", moji_igralci=moji_igralci, ime_ekipe=ime_ekipe)



@get('/pregled_baze')
def pregled_baze():
    cur.execute("SELECT * FROM Country limit 10;")
    Country = cur.fetchall()
    cur.execute("SELECT * FROM League limit 10;")
    League = cur.fetchall()
    cur.execute("SELECT * FROM Match limit 10;")
    Match = cur.fetchall()
    cur.execute("SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_name in ('Lionel Messi')")
    cur.execute("SELECT * FROM Player;")
    #cur.execute("SELECT count(*) FROM Player where team_id not null;")
    Player = cur.fetchall()
    cur.execute("SELECT * FROM Player_Attributes limit 10;")
    Player_Attributes = cur.fetchall()
    cur.execute("SELECT * FROM Team;")
    Team = cur.fetchall()
    cur.execute("SELECT * FROM Team_Attributes limit 10;")
    Team_Attributes = cur.fetchall()
    return bottle.template("pregled_tabel.html", Country=Country, League=League, Match=Match, Player=Player, Player_Attributes=Player_Attributes, Team=Team, Team_Attributes=Team_Attributes)

@get('/quick_match')
def load_quick_match():
    # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
    home_team = 10194 # request.forms.get('home_team')
    away_team = 10260 # request.forms.get('away_team')

    # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
    # s_home = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    # JOIN Team ON Player.team_id = Team.team_api_id 
    # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    # WHERE Player.team_id = {home_team}
    # ORDER BY Player_Attributes.overall_rating DESC;"""
    # cur.execute(s_home) 
    # home_igralci = cur.fetchall()

    # s_away = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    # JOIN Team ON Player.team_id = Team.team_api_id 
    # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    # WHERE Player.team_id = {away_team}
    # ORDER BY Player_Attributes.overall_rating DESC;"""
    # cur.execute(s_away) 
    # away_igralci = cur.fetchall()

    return template("quick_match.html", home_igralci=[], away_igralci=[], poz=POZICIJE)


@post('/quick_match')
def load_quick_match():
    # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')

    # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
    s_home = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.team_id = {home_team}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    cur.execute(s_home) 
    home_igralci = cur.fetchall()

    s_away = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.team_id = {away_team}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    cur.execute(s_away) 
    away_igralci = cur.fetchall()

    return template("quick_match.html", home_igralci=home_igralci, away_igralci=away_igralci, poz=POZICIJE)

# TODO naredi tako da lahko izberes igralce in dodaj gumb odigraj tekmo

@post('/simuliraj_tekmo')
def simuliraj_tekmo():
    seznam_home_igralcev = []
    seznam_away_igralcev = []
    # res = f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev)
    return '2 : 1'



# @get('/uredi_ekipo')
# def uredi_ekipo():
#     cur.execute("SELECT * FROM Player;")
#     Player = cur.fetchall()
#     return bottle.template("igralci.html", Player = Player)


@get('/lestvica')
def izberi_lestico():
    return bottle.template("liga.html", lestvica=[])

@post('/lestvica')
def do_lestvica():
    league_id = request.forms.get('liga')
    sezona = request.forms.get('sezona')
    krog = int(request.forms.get('krog'))

    slovar_lest = model.izracunaj_lestvico(cur, league_id, sezona, krog)
    lest = [(ekipa_id, Z, R, P, dani_goli, prejeti_goli) for  ekipa_id, (Z, R, P, dani_goli, prejeti_goli) in slovar_lest.items()]
    #lest.sort()
    lest_sortirana = sorted(lest, key=prvi_na_vrsti, reverse=True)   #sortiramo po tockah (prvi bo na prvem mestu)
    # reverse=True poskrbi da gre od najvecjega stevila tock do najmanjsega
    return bottle.template("liga.html", lestvica=lest_sortirana)

#Spodnjo funkcijo uporabimo v def do_lestvica() zgoraj, da izracunamo stevilo tock in gol razliko. Po temu potem sortiramo lestvico. Najprej tocke potem gol razlika.
def prvi_na_vrsti(elem):
    return (elem[1] * 3 + elem[2], elem[4] - elem[5])  #uporabimo tuple
    

@get('/naredi_ekipo')
def naredi_ekipo():
    # TODO * zamenjaj s ustreznimi stolpci
    s = "SELECT * FROM Player WHERE team_id = 50000;"
    cur.execute(s)
    moji_igralci = cur.fetchall()
    return bottle.template("izbor_igralcev.html", moji_igralci=moji_igralci, igralci=[])


@post('/naredi_ekipo')
def sestavi_ekipo():
    ime_igralca = request.forms.get('igralec')
    vratar = request.forms.get('vratar')
    branilec = request.forms.get('branilec')
    vezist = request.forms.get('vezist')
    napadalec = request.forms.get('napadalec')
    polozaji = []
    if vratar != None:
        polozaji += [1]
    if branilec != None:
        polozaji += [2,3,4,5]
    if vezist != None:
        polozaji += [6,7,8]
    if napadalec != None:
        polozaji += [9,10,11]
    if len(polozaji) == 1:
        polozaji = f"({polozaji[0]})"
    else:
        polozaji = tuple(polozaji)

    s = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_coordinate_y in {polozaji} AND Player.player_name like '%{ime_igralca}%' 
    ORDER BY Player_Attributes.overall_rating DESC;"""
    res = cur.execute(s) 
    sez_igralcev = res.fetchall()
    def f_cena(r):
        r = int(r) if r != None else 1
        if r > 70:
            return r * 100000
        else:
            return r * 1000
    return bottle.template("izbor_igralcev.html", moji_igralci=[], igralci = sez_igralcev, poz=POZICIJE, f_cena=f_cena, url=bottle.url)

@post('/kupi/<igralec_id>')
def kupi(igralec_id):
    cur.execute(f"SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_api_id = {igralec_id};")
    player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y = tuple(cur.fetchone())
    # TODO preveri ce je ta igralec ze med kupljenimi
    # TODO denar se mora odsteti od budgeta
    print(player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y)
    s = f"""
        INSERT INTO Player
        (player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y) 
        VALUES ((SELECT MAX(player_api_id)+1 FROM Player), '{player_name}', (SELECT MAX(player_fifa_api_id)+1 FROM Player), '{birthday}', {50000}, {player_coordinate_x}, {player_coordinate_y});
    """ 
    cur.execute(s)
    con.commit()
    return redirect(url('/naredi_ekipo'))

# TODO podobno kot kupi (rabil bom player_api_id), tako kot je narejeno v izbor_igralcev.html 56 vrstica
# @post('/prodaj/<igralec_id>')
# def prodaj(igralec_id):
#     cur.execute(f"SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_api_id = {igralec_id};")
#     player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y = tuple(cur.fetchone())
#     # TODO preveri ce je ta igralec ze med kupljenimi
#     # TODO denar se mora odsteti od budgeta
#     print(player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y)
#     s = f"""
#         INSERT INTO Player
#         (player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y) 
#         VALUES ((SELECT MAX(player_api_id)+1 FROM Player), '{player_name}', (SELECT MAX(player_fifa_api_id)+1 FROM Player), '{birthday}', {50000}, {player_coordinate_x}, {player_coordinate_y});
#     """ 
#     cur.execute(s)
#     con.commit()
#     return redirect(url('/naredi_ekipo'))

# @get('/lestvica/<league_id>')
# def lestvica(league_id):
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return bottle.template("lestvica.html", ekipe=teams)


# @get('/lestvica/<league_id>')
# def lestvica(league_id):
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return bottle.template("lestvica.html", ekipe=teams)


#da izpiše vse igralce
@get('/ekipa/<ime_ekipe>')
def ekipa(ime_ekipe):
    s = f"""SELECT Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
            JOIN Team ON Player.team_id = Team.team_api_id WHERE Team.team_long_name = '{ime_ekipe}';"""
    print(s)
    res = cur.execute(s) 
    igralci = res.fetchall()
    return bottle.template("ekipa.html", ime_ekipe = ime_ekipe, igralci = igralci)

# @get('/igralec/<ime_igralca>')
# def igralec(ime_igralca):
#     s = f'''SELECT Player.birthday, Team.team_long_name, Team.team_short_name, 
#             Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
#             JOIN Team ON Player.team_id = Team.team_api_id
#             WHERE Player.player_name = {ime_igralca}'''
#     res = cur.execute(s)
#     atributi = res.fetchall()
#     return bottle.template("igralec.html",ime_igralca = ime_igralca)


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