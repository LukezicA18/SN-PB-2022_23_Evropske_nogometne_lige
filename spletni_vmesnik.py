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
    liga_tuple = (liga)
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
    try:
        model.kupi(igralec_id)
    ## pogledamo ce je kaksna napaka
    except RuntimeError:
        return template("napake.html", besedilo="Imate premalo denarja")
    except Exception:
        return template("napake.html", besedilo="Igralec je že v ekipi Moja Ekipa.")
    return redirect(url('/naredi_ekipo'))


#podobno kot kupi (rabil bom player_api_id), tako kot je narejeno v izbor_igralcev.html 56 vrstica
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
    #home_team = request.forms.get('home_team')
    #away_team = request.forms.get('away_team')
    vse_ekipe = model.vse_ekipe()
    return template("quick_match.html", home_igralci=[], away_igralci=[], vse_ekipe = vse_ekipe, poz=model.POZICIJE) 


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
    home_team = request.forms.get('home_team')
    away_team = request.forms.get('away_team')

    if st_moja_ekipa < 15 and (home_team == 'Moja Ekipa' or away_team == 'Moja Ekipa'):
        return template("napake.html", besedilo="V ekipi Moja Ekipa je premalo igralcev. V kadru za tekmo jih mora biti vsaj 15.")

    #preverimo ce v kasni ekipi ni 11 igrlcev 
    koliko_home = len(seznam_domacih_igralcev)
    koliko_away = len(seznam_gostujocih_igralcev)
    if koliko_home < 11:
        return template("napake.html", besedilo=f"V prvi postavi domače ekipe ni 11 igralcev. Manjka še: {11 - koliko_home}")
    if koliko_home  > 11:
        return template("napake.html", besedilo=f"V prvi postavi domače ekipe ni 11 igralcev. Odveč jih je: {koliko_home - 11}")
    if koliko_away < 11:
        return template("napake.html", besedilo=f"V prvi postavi gostujoče ekipe ni 11 igralcev. Manjka še: {11 - koliko_away}")
    if koliko_away  > 11:
        return template("napake.html", besedilo=f"V prvi postavi gostujoče ekipe ni 11 igralcev. Odveč jih je: {koliko_away - 11}")
    
    domaca_ekipa = model.katera_ekipa(tuple(seznam_domacih_igralcev))
    gostujoca_ekipa = model.katera_ekipa(tuple(seznam_gostujocih_igralcev))

    res = model.f_izracunaj_stohasticen_rezultat(seznam_domacih_igralcev, seznam_gostujocih_igralcev) 

    return template("simulacija_tekme.html", rezultat = res, domaca_ekipa = domaca_ekipa, gostujoca_ekipa = gostujoca_ekipa)


#da izpiše vse igralce
@get('/ekipa/<ime_ekipe>')
def ekipa(ime_ekipe):
    ime_ekipe, igralci = model.ekipa_model(ime_ekipe)
    return template("ekipa.html", ime_ekipe=ime_ekipe, igralci=igralci)



bottle.run(debug=True, reloader=True)

