import bottle
import model
from bottle import *
import sqlite3


###### zacetna stran
# Poklicemo funkciji moji_igralci() in ime_moje_ekipe() iz model.py. Na prvi strani spletne strani bo seznam igralcev moje ekipe.
@get('/')
def index():
    moji_igralci = model.moji_igralci()
    ime_ekipe = model.ime_moje_ekipe()
    return template("moja_ekipa.html", igralci=moji_igralci, ime_ekipe=ime_ekipe, poz = model.POZICIJE, f_cena = model.f_cena)  #f_cena tukaj ne pisemo kot funkcije, ne dodamo ()


####### pregled baze
@get('/pregled_baze')
def pregled_baze():
    Country, League, Match, Player, Player_Attributes, Team, Team_Attributes = model.pregled()
    return template("pregled_tabel.html", Country=Country, League=League, Match=Match, Player=Player, Player_Attributes=Player_Attributes, Team=Team, Team_Attributes=Team_Attributes)



##############################################
# lestvica
##############################################

@get('/lestvica')
def izberi_lestvico():
    return template("liga.html", lestvica=[])

@post('/lestvica')
def do_lestvica():
    league_id = request.forms.get('liga')
    sezona = request.forms.get('sezona')
    krog = int(request.forms.get('krog'))
    lest_sortirana = model.naredi_lestvico(league_id, sezona, krog)
    print(lest_sortirana)
    return template("liga.html", lestvica=lest_sortirana)



####################################################################################
# transfer market
####################################################################################

@get('/naredi_ekipo')
def naredi_ekipo():
    moji_igralci = model.moji_igralci()
    vsota_denarja = model.koliko_denarja()
    stevilo_igralcev = model.stevilo_igralcev_v_ekipi()
    return template("izbor_igralcev.html", denar = vsota_denarja, stevilo_igralcev = stevilo_igralcev, moji_igralci=moji_igralci, igralci=[], poz=model.POZICIJE,  url=bottle.url)


@post('/naredi_ekipo')
def sestavi_ekipo():
    ime_igralca = request.forms.get('igralec')
    vratar = request.forms.get('vratar')
    branilec = request.forms.get('branilec')
    vezist = request.forms.get('vezist')
    napadalec = request.forms.get('napadalec')
    klub = request.forms.get('klub')
    # filtriramo glede na ceno
    manj20 = request.forms.get('manj20')
    manj40 = request.forms.get('manj40')
    manj60 = request.forms.get('manj60')
    manj80 = request.forms.get('manj80')
    manj100 = request.forms.get('manj100')

    sez_igralcev = model.seznam_igralcev_za_prikaz(ime_igralca, vratar, branilec, vezist, napadalec, klub, manj20, manj40, manj60, manj80, manj100)
    vsota_denarja = model.koliko_denarja()
    stevilo_igralcev = model.stevilo_igralcev_v_ekipi()
    return template("izbor_igralcev.html", denar = vsota_denarja, stevilo_igralcev = stevilo_igralcev, moji_igralci=[], igralci = sez_igralcev, poz=model.POZICIJE, url=bottle.url)

@post('/kupi/<igralec_id>')
def kupi(igralec_id):
    model.kupi(igralec_id)
    return redirect(url('/naredi_ekipo'))

# TODO podobno kot kupi (rabil bom player_api_id), tako kot je narejeno v izbor_igralcev.html 56 vrstica
@post('/prodaj/<igralec_id>')
def prodaj(igralec_id):
    model.prodaj(igralec_id)
    return redirect(url('/naredi_ekipo'))




#####################################################
# quick match
#####################################################

@get('/quick_match')
def load_quick_match():
    # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')
    return template("quick_match.html", home_igralci=[], away_igralci=[], poz=model.POZICIJE)


@post('/quick_match')
def load_quick_match():
    # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
    # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')

    home_igralci, away_igralci = model.igralci_v_ekipi(home_team), model.igralci_v_ekipi(away_team)

    return template("quick_match.html", home_igralci=home_igralci, away_igralci=away_igralci, poz=model.POZICIJE)

# TODO naredi tako da lahko izberes igralce in dodaj gumb odigraj tekmo


# @post('/simuliraj_tekmo')
# def simuliraj_tekmo():
#     seznam_home_igralcev = []
#     seznam_away_igralcev = []
#     # res = f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev)
#     return '2 : 1'

@post('/simuliraj_tekmo')
def simuliraj_tekmo():
    # grdo ampak deluje
    max_stevilo_igralcev_izmed_vseh_ekip = 30
    seznam_home_igralcev = []
    seznam_away_igralcev = []
    for i in range(max_stevilo_igralcev_izmed_vseh_ekip):
        id_home = request.forms.get(str(i))
        if id_home != None: seznam_home_igralcev.append(id_home)
        id_away = request.forms.get(str(i+max_stevilo_igralcev_izmed_vseh_ekip))
        if id_away != None: seznam_away_igralcev.append(id_away)

    if len(seznam_home_igralcev) != 11: return "V domači ekipi ni 11 igralcev"
    if len(seznam_away_igralcev) != 11: return "V gostojoči ekipi ni 11 igralcev"

    res = model.f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev)
    return #res



# @get('/uredi_ekipo')
# def uredi_ekipo():
#     cur.execute("SELECT * FROM Player;")
#     Player = cur.fetchall()
#     return template("igralci.html", Player = Player)


# @get('/lestvica/<league_id>')
# def lestvica(league_id):
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return template("lestvica.html", ekipe=teams)


# @get('/lestvica/<league_id>')
# def lestvica(league_id):
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return template("lestvica.html", ekipe=teams)


#da izpiše vse igralce
@get('/ekipa/<ime_ekipe>')
def ekipa(ime_ekipe):
    ime_ekipe, igralci = model.ekipa_model(ime_ekipe)
    return template("ekipa.html", ime_ekipe=ime_ekipe, igralci=igralci)

# @get('/igralec/<ime_igralca>')
# def igralec(ime_igralca):
#     s = f'''SELECT Player.birthday, Team.team_long_name, Team.team_short_name, 
#             Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
#             JOIN Team ON Player.team_id = Team.team_api_id
#             WHERE Player.player_name = {ime_igralca}'''
#     res = cur.execute(s)
#     atributi = res.fetchall()
#     return template("igralec.html",ime_igralca = ime_igralca)


# @post('/lestvica')
# def do_lestvica():
#     league_id = request.forms.get('liga')
#     sezona = request.forms.get('sezona')
#     print(league_id, sezona)
#     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
#     res = cur.execute(s)
#     teams = res.fetchall()
#     print(teams)
#     return template("lestvica.html", ekipe=teams)


bottle.run(debug=True, reloader=True)







# 'import bottle
# import model
# from bottle import *
# import sqlite3

# #glavni_model = model.Model()
# POZICIJE = {1:"vratar", 2:"branilec", 3:"branilec", 4:"branilec", 5:"branilec", 6:"vezist", 7:"vezist", 8:"vezist", 9:"napadalec", 10:"napadalec", 11:"napadalec"}

# @get('/')
# def index():
#     moja_ekipa = 50000
#     s = f"""SELECT Player.player_api_id, Player.team_id, Player.player_name, DATE(Player.birthday) AS birthday, Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot FROM Player 
#     JOIN Team ON Player.team_id = Team.team_api_id 
#     JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     WHERE Player.player_name IN (SELECT player_name FROM Player WHERE team_id = {moja_ekipa}) AND team_id != {moja_ekipa}
#     ORDER BY Player_Attributes.overall_rating DESC;"""
#     cur.execute(s)
#     moji_igralci = cur.fetchall()
#     s = "SELECT team_long_name FROM Team WHERE team_api_id = 50000;"
#     cur.execute(s)
#     ime_ekipe = cur.fetchall() #.fetchone()   #dobimo tuple. V htmlju je treba extractat potem prvi element (ki je v tem primeru MojaEkipa)
#     return bottle.template("moja_ekipa.html", igralci=moji_igralci, ime_ekipe=ime_ekipe, poz=POZICIJE, f_cena=f_cena) #url=bottle.url)



# @get('/pregled_baze')
# def pregled_baze():
#     cur.execute("SELECT * FROM Country limit 10;")
#     Country = cur.fetchall()
#     cur.execute("SELECT * FROM League limit 10;")
#     League = cur.fetchall()
#     cur.execute("SELECT * FROM Match limit 10;")
#     Match = cur.fetchall()
#     cur.execute("SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_name in ('Lionel Messi')")
#     cur.execute("SELECT * FROM Player;")
#     #cur.execute("SELECT count(*) FROM Player where team_id not null;")
#     Player = cur.fetchall()
#     cur.execute("SELECT * FROM Player_Attributes limit 10;")
#     Player_Attributes = cur.fetchall()
#     cur.execute("SELECT * FROM Team;")
#     Team = cur.fetchall()
#     cur.execute("SELECT * FROM Team_Attributes limit 10;")
#     Team_Attributes = cur.fetchall()
#     return bottle.template("pregled_tabel.html", Country=Country, League=League, Match=Match, Player=Player, Player_Attributes=Player_Attributes, Team=Team, Team_Attributes=Team_Attributes)

# @get('/quick_match')
# def load_quick_match():
#     # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
#     home_team = 10194 # request.forms.get('home_team')
#     away_team = 10260 # request.forms.get('away_team')

#     # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
#     # s_home = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
#     # JOIN Team ON Player.team_id = Team.team_api_id 
#     # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     # WHERE Player.team_id = {home_team}
#     # ORDER BY Player_Attributes.overall_rating DESC;"""
#     # cur.execute(s_home) 
#     # home_igralci = cur.fetchall()

#     # s_away = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
#     # JOIN Team ON Player.team_id = Team.team_api_id 
#     # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     # WHERE Player.team_id = {away_team}
#     # ORDER BY Player_Attributes.overall_rating DESC;"""
#     # cur.execute(s_away) 
#     # away_igralci = cur.fetchall()

#     return template("quick_match.html", home_igralci=[], away_igralci=[], poz=POZICIJE)


# @post('/quick_match')
# def load_quick_match():
#     # TODO naj to bere iz drop down menija ali pa da pises ime ekipe in ti ponuja izbira (se bom se odlocil)
#     home_team = request.forms.get('home_team')
#     away_team = request.forms.get('away_team')

#     # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo   (ker ne moremo Joinat s Player_Attributes, ker nimamo pravega idja ali api_idja)
#     s_home = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
#     JOIN Team ON Player.team_id = Team.team_api_id 
#     JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     WHERE Player.team_id = {home_team}
#     ORDER BY Player_Attributes.overall_rating DESC;"""
#     cur.execute(s_home) 
#     home_igralci = cur.fetchall()

#     s_away = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
#     JOIN Team ON Player.team_id = Team.team_api_id 
#     JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     WHERE Player.team_id = {away_team}
#     ORDER BY Player_Attributes.overall_rating DESC;"""
#     cur.execute(s_away) 
#     away_igralci = cur.fetchall()

#     return template("quick_match.html", home_igralci=home_igralci, away_igralci=away_igralci, poz=POZICIJE)

# # TODO naredi tako da lahko izberes igralce in dodaj gumb odigraj tekmo

# @post('/simuliraj_tekmo')
# def simuliraj_tekmo():
#     seznam_home_igralcev = []
#     seznam_away_igralcev = []
#     # res = f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev)
#     return '2 : 1'



# # @get('/uredi_ekipo')
# # def uredi_ekipo():
# #     cur.execute("SELECT * FROM Player;")
# #     Player = cur.fetchall()
# #     return bottle.template("igralci.html", Player = Player)


# @get('/lestvica')
# def izberi_lestico():
#     return bottle.template("liga.html", lestvica=[])

# @post('/lestvica')
# def do_lestvica():
#     league_id = request.forms.get('liga')
#     sezona = request.forms.get('sezona')
#     krog = int(request.forms.get('krog'))

#     slovar_lest = model.izracunaj_lestvico(cur, league_id, sezona, krog)
#     lest = [(ekipa_id, Z, R, P, dani_goli, prejeti_goli) for  ekipa_id, (Z, R, P, dani_goli, prejeti_goli) in slovar_lest.items()]
#     #lest.sort()
#     lest_sortirana = sorted(lest, key=prvi_na_vrsti, reverse=True)   #sortiramo po tockah (prvi bo na prvem mestu)
#     # reverse=True poskrbi da gre od najvecjega stevila tock do najmanjsega
#     return bottle.template("liga.html", lestvica=lest_sortirana)

# #Spodnjo funkcijo uporabimo v def do_lestvica() zgoraj, da izracunamo stevilo tock in gol razliko. Po temu potem sortiramo lestvico. Najprej tocke potem gol razlika.
# def prvi_na_vrsti(elem):
#     return (elem[1] * 3 + elem[2], elem[4] - elem[5])  #uporabimo tuple
    

# @get('/naredi_ekipo')
# def naredi_ekipo():
#     # TODO * zamenjaj s ustreznimi stolpci
#     s = "SELECT * FROM Player WHERE team_id = 50000;"
#     cur.execute(s)
#     moji_igralci = cur.fetchall()
#     return bottle.template("izbor_igralcev.html", moji_igralci=moji_igralci, igralci=[])


# @post('/naredi_ekipo')
# def sestavi_ekipo():
#     ime_igralca = request.forms.get('igralec')
#     vratar = request.forms.get('vratar')
#     branilec = request.forms.get('branilec')
#     vezist = request.forms.get('vezist')
#     napadalec = request.forms.get('napadalec')
#     polozaji = []
#     if vratar != None:
#         polozaji += [1]
#     if branilec != None:
#         polozaji += [2,3,4,5]
#     if vezist != None:
#         polozaji += [6,7,8]
#     if napadalec != None:
#         polozaji += [9,10,11]
#     if len(polozaji) == 1:
#         polozaji = f"({polozaji[0]})"
#     else:
#         polozaji = tuple(polozaji)

#     s = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
#     JOIN Team ON Player.team_id = Team.team_api_id 
#     JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
#     WHERE Player.player_coordinate_y in {polozaji} AND Player.player_name like '%{ime_igralca}%' 
#     ORDER BY Player_Attributes.overall_rating DESC;"""
#     res = cur.execute(s) 
#     sez_igralcev = res.fetchall()
#     return bottle.template("izbor_igralcev.html", moji_igralci=[], igralci = sez_igralcev, poz=POZICIJE, f_cena=f_cena, url=bottle.url)

# def f_cena(r):
#         r = int(r) if r != None else 1
#         if r > 70:
#             return r * 100000
#         else:
#             return r * 1000

# @post('/kupi/<igralec_id>')
# def kupi(igralec_id):
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

# # TODO podobno kot kupi (rabil bom player_api_id), tako kot je narejeno v izbor_igralcev.html 56 vrstica
# # @post('/prodaj/<igralec_id>')
# # def prodaj(igralec_id):
# #     cur.execute(f"SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_api_id = {igralec_id};")
# #     player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y = tuple(cur.fetchone())
# #     # TODO preveri ce je ta igralec ze med kupljenimi
# #     # TODO denar se mora odsteti od budgeta
# #     print(player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y)
# #     s = f"""
# #         INSERT INTO Player
# #         (player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y) 
# #         VALUES ((SELECT MAX(player_api_id)+1 FROM Player), '{player_name}', (SELECT MAX(player_fifa_api_id)+1 FROM Player), '{birthday}', {50000}, {player_coordinate_x}, {player_coordinate_y});
# #     """ 
# #     cur.execute(s)
# #     con.commit()
# #     return redirect(url('/naredi_ekipo'))

# # @get('/lestvica/<league_id>')
# # def lestvica(league_id):
# #     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
# #     res = cur.execute(s)
# #     teams = res.fetchall()
# #     print(teams)
# #     return bottle.template("lestvica.html", ekipe=teams)


# # @get('/lestvica/<league_id>')
# # def lestvica(league_id):
# #     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
# #     res = cur.execute(s)
# #     teams = res.fetchall()
# #     print(teams)
# #     return bottle.template("lestvica.html", ekipe=teams)


# #da izpiše vse igralce
# @get('/ekipa/<ime_ekipe>')
# def ekipa(ime_ekipe):
#     s = f"""SELECT Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
#             JOIN Team ON Player.team_id = Team.team_api_id WHERE Team.team_long_name = '{ime_ekipe}';"""
#     print(s)
#     res = cur.execute(s) 
#     igralci = res.fetchall()
#     return bottle.template("ekipa.html", ime_ekipe = ime_ekipe, igralci = igralci)

# # @get('/igralec/<ime_igralca>')
# # def igralec(ime_igralca):
# #     s = f'''SELECT Player.birthday, Team.team_long_name, Team.team_short_name, 
# #             Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
# #             JOIN Team ON Player.team_id = Team.team_api_id
# #             WHERE Player.player_name = {ime_igralca}'''
# #     res = cur.execute(s)
# #     atributi = res.fetchall()
# #     return bottle.template("igralec.html",ime_igralca = ime_igralca)


# # @post('/lestvica')
# # def do_lestvica():
# #     league_id = request.forms.get('liga')
# #     sezona = request.forms.get('sezona')
# #     print(league_id, sezona)
# #     s = f"SELECT Team.team_long_name, Team.team_short_name FROM Team JOIN League ON Team.league_id = League.id where League.id = {league_id}"
# #     res = cur.execute(s)
# #     teams = res.fetchall()
# #     print(teams)
# #     return bottle.template("lestvica.html", ekipe=teams)





# baza = "baza_nogomet.db"
# con = sqlite3.connect(baza)
# cur = con.cursor()

# bottle.run(debug=True, reloader=True)



# # import bottle
# # import model

# # glavni_model = model.Model()

# # @bottle.route("/static/slikice/<filename>")    #ZA SLIKO
# # def serve_static_files(filename):
# #     return bottle.static_file(filename, root="./static/img")  

# # @bottle.route("/static/css/<filename>")    #ZA RDEČO barvo, dodamo to kar mamo na datoteki style.css
# # def serve_static_files(filename):
# #     return bottle.static_file(filename, root="./static/css") 

# # @bottle.get("/")
# # def glavna_stran():
    
# #     podatki = glavni_model.dobi_vse_uporabnike()
    
# #     return bottle.template(
# #         "glavna.html", uporabniki=podatki
# #         )




# # bottle.run(debug=True, reloader=True)'