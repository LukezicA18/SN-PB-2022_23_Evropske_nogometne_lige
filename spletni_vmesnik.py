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
    return template("moja_ekipa.html", igralci=moji_igralci, ime_ekipe=ime_ekipe, poz = model.POZICIJE) #f_cena = model.f_cena)  #f_cena tukaj ne pisemo kot funkcije, ne dodamo ()


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
    return template("liga.html", lestvica=[], liga = "")

@post('/lestvica')
def do_lestvica():
    league_id = request.forms.get('liga')
    sezona = request.forms.get('sezona')
    krog = int(request.forms.get('krog'))
    lest_sortirana = model.naredi_lestvico(league_id, sezona, krog)
    liga = model.id_lige_v_ime(league_id)   #da lahko damo naslov (napisemo kakatero lestvico gledamo)
    return template("liga.html", lestvica=lest_sortirana, liga = liga)



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

    #moji_igralci = model.moji_igralci()   #ce zlim, da so tudi ko iscem nove igralce moji igralci napisani

    sez_igralcev = model.seznam_igralcev_za_prikaz(ime_igralca, vratar, branilec, vezist, napadalec, klub, manj20, manj40, manj60, manj80, manj100)
    vsota_denarja = model.koliko_denarja()
    stevilo_igralcev = model.stevilo_igralcev_v_ekipi()
    return template("izbor_igralcev.html", denar = vsota_denarja, stevilo_igralcev = stevilo_igralcev, moji_igralci=[], igralci = sez_igralcev, poz=model.POZICIJE, url=bottle.url)   #ce zelim da so igralci tudi k iscem nove izpisani: moji_igralci = moji_igralci

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
    # bere iz drop down menija (lahko bi tudi, da pises ime ekipe in ti ponuja izbira)
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')
    vse_ekipe = model.vse_ekipe()
    return template("quick_match.html", home_igralci=[], away_igralci=[], vse_ekipe = vse_ekipe, poz=model.POZICIJE)  # vse ekipe trenutno ne bi rabil, ker nekaj ne dela


@post('/quick_match')
def load_quick_match():
    # bere iz drop down menija (lahko bi tudi, da pises ime ekipe in ti ponuja izbira)
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')

    home_igralci, away_igralci = model.igralci_v_ekipi(home_team), model.igralci_v_ekipi(away_team)
    vse_ekipe = model.vse_ekipe()

    domaci_ime = model.id_ekipe_v_ime(home_team)
    gostje_ime = model.id_ekipe_v_ime(away_team)

    return template("quick_match.html", home_igralci=home_igralci, away_igralci=away_igralci, vse_ekipe =vse_ekipe, domaci = domaci_ime, gostje = gostje_ime, poz=model.POZICIJE)   # vse ekipe trenutno ne bi rabil, ker nekaj ne dela


# @post('/simuliraj_tekmo')
# def simuliraj_tekmo():
#     seznam_home_igralcev = []
#     seznam_away_igralcev = []
#     # res = f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev)
#     return '2 : 1'

@post('/simuliraj_tekmo')
def simuliraj_tekmo():
    # grdo ampak deluje
    max_stevilo_igralcev_izmed_vseh_ekip = 30   # vec kot 30 igralcev nima nobena ekipa (zelimo zajeti vse igralce)
    seznam_domacih_igralcev = []
    seznam_gostujocih_igralcev = []
    for i in range(max_stevilo_igralcev_izmed_vseh_ekip):
        id_home = request.forms.get(str(i))  # tisti, ki so odkljukani ne bodo None
        if id_home != None:                  # to pomeni, da je v prvi postavi
            seznam_domacih_igralcev.append(id_home)   
        id_away = request.forms.get(str(i+max_stevilo_igralcev_izmed_vseh_ekip))
        if id_away != None: 
            seznam_gostujocih_igralcev.append(id_away)

    #ce je v ekipi manj kot 15 igralcev 
    st_moja_ekipa = model.stevilo_igralcev_v_moji_ekipi()
    # kasneje naredi se za splosno ekipo
    if st_moja_ekipa < 15:
        return f"V ekipi Moja Ekipa je premalo igralcev. V kadru za tekmo jih mora biti vsaj 15."

    #preverimo ce v kasni ekipi ni 11 igrlcev 
    koliko_home = len(seznam_domacih_igralcev)
    koliko_away = len(seznam_gostujocih_igralcev)
    if koliko_home < 11:
        return f"V prvi postavi domače ekipe ni 11 igralcev. Manjka še: {11 - koliko_home}"
    if koliko_home  > 11:
        return f"V prvi postavi domače ekipe ni 11 igralcev. Odveč jih je: {koliko_home - 11}"
    if koliko_away < 11:
        return f"V prvi postavi gostujoče ekipe ni 11 igralcev. Manjka še: {11 - koliko_away}"
    if koliko_away  > 11:
        return f"V prvi postavi gostujoče ekipe ni 11 igralcev. Odveč jih je: {koliko_away - 11}"
    
    domaca_ekipa = model.katera_ekipa(tuple(seznam_domacih_igralcev))
    gostujoca_ekipa = model.katera_ekipa(tuple(seznam_gostujocih_igralcev))

    res = model.f_izracunaj_stohasticen_rezultat(seznam_domacih_igralcev, seznam_gostujocih_igralcev)    

    return template("simulacija_tekme.html", rezultat = res, domaca_ekipa = domaca_ekipa, gostujoca_ekipa = gostujoca_ekipa)



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