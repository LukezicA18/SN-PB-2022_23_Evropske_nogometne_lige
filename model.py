import sqlite3
import random

baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()

POZICIJE = {1:"vratar", 2:"branilec", 3:"branilec", 4:"branilec", 5:"branilec", 6:"vezist", 7:"vezist", 8:"vezist", 9:"napadalec", 10:"napadalec", 11:"napadalec"}


###### pri @get('/')
# funkciji moji_igralci() in ime_moje_ekipe uporabimo za prikaz prve strani
def moji_igralci():
    moja_ekipa_id = 50000
    s = f"""SELECT Player.player_api_id, Player.team_id, Player.player_name, DATE(Player.birthday) AS birthday, Player.player_coordinate_y,
    Player_Attributes.overall_rating, Player_Attributes.preferred_foot, Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_name IN (SELECT player_name FROM Player WHERE team_id = {moja_ekipa_id}) AND team_id != {moja_ekipa_id}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    # DATE(Player.birthday) AS birthday -----> tako vzamemo samo datum in ne tudi ure (00:... ne bo napisano)
    cur.execute(s)
    moji_igralci = cur.fetchall()
    return moji_igralci

def ime_moje_ekipe():
    moja_ekipa_id = 50000
    s = f"SELECT team_long_name FROM Team WHERE team_api_id = {moja_ekipa_id};"
    cur.execute(s)
    ime_ekipe = cur.fetchone() #dobimo tuple. V htmlju je treba extractat potem prvi element (ki je v tem primeru MojaEkipa)
    return ime_ekipe
#########


######### @get('/pregled_baze')
# funkcijo pregled() uporabimo za pregled baze (@get('/pregled_baze'))
def pregled():
    cur.execute("SELECT * FROM Country limit 10;")
    Country = cur.fetchall()
    cur.execute("SELECT * FROM League limit 10;")
    League = cur.fetchall()
    cur.execute("SELECT * FROM Match limit 10;")
    Match = cur.fetchall()
    # cur.execute("SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_name in ('Lionel Messi')")
    cur.execute("SELECT * FROM Player;")# order by id desc;")
    #cur.execute("SELECT count(*) FROM Player where team_id not null;")
    Player = cur.fetchall()
    cur.execute("SELECT * FROM Player_Attributes limit 10;")
    Player_Attributes = cur.fetchall()
    cur.execute("SELECT * FROM Team limit 10;")
    Team = cur.fetchall()
    cur.execute("SELECT * FROM Team_Attributes limit 10;")
    Team_Attributes = cur.fetchall()
    return Country, League, Match, Player, Player_Attributes, Team, Team_Attributes
#########


################### @post('/lestvica')
def naredi_lestvico(league_id, sezona, krog):
    slovar_lest = izracunaj_lestvico(league_id, sezona, krog)    #lestvica je zapisana v slovarju 
    lest = []
    for ekipa_id, (Z, R, P, dani_goli, prejeti_goli) in slovar_lest.items():
        s = f""" SELECT team_long_name FROM Team
                    WHERE team_api_id = {ekipa_id};
              """
        res = cur.execute(s)
        ime_ekipe = res.fetchall()      #namesto id-ja ekipe smo sedaj poiskali ime ekipe
        lest += [(ime_ekipe, Z, R, P, dani_goli, prejeti_goli)]

    lest_sortirana = sorted(lest, key=prvi_na_vrsti, reverse=True)    # sortiramo po tockah (prvi bo na prvem mestu)
                                                                      # reverse=True poskrbi da gre od najvecjega stevila tock do najmanjsega
                                                                      # uporabimo
    mesto = 0       # da zapisemo se na katerem mestu je bila posamezna ekipa
    koncna_lest = []
    for el in lest_sortirana:
        mesto += 1
        el = (mesto,) + el
        koncna_lest.append(el)                                                               
    return koncna_lest


# funkcijo uporabimo v funkciji do_lestvica() zgoraj, da izracunamo stevilo tock in gol razliko. Po temu potem sortiramo lestvico. Najprej tocke potem gol razlika.
def prvi_na_vrsti(elem):
    return (elem[1] * 3 + elem[2], elem[4] - elem[5])  #uporabimo tuple


def izracunaj_lestvico(league_id, season, krog=100):
    '''Vrne slovar ekip, z lestvico te ekipe.'''
    tekme = vse_tekme_v_sezoni(league_id, season, krog)   # za doloceno ligo, sezono in krog, si pogledamo vse tekme v tej ligi v tej sezoni do tega kroga
                                                          # torej pogledamo vse tekme do tukaj
    slovar_ekip = {}     # v tem slovarju bo za vsako ekip zapisana lestvica (kljuc je team_id, vrednost pa predstavlja tuple,
                         # v katerem so zapisane zmage, remiji, porazi, dani goli in prejeti goli te ekipe (torej ekipe s tkim idjem))
                         # {ekipa_id: (Z, R, P, dani_goli, prejeti_goli)}
    for stage, date, home_team_id, away_team_id, home_team_goals, away_team_goals in tekme:
        if home_team_id not in slovar_ekip:              # ekipo dodamo v slovar
            if home_team_goals > away_team_goals:        #torej je zmagala domaca ekipa
                slovar_ekip[home_team_id] = (1, 0, 0, home_team_goals, away_team_goals)
            elif home_team_goals < away_team_goals:
                slovar_ekip[home_team_id] = (0, 0, 1, home_team_goals, away_team_goals)
            elif home_team_goals == away_team_goals:
                slovar_ekip[home_team_id] = (0, 1, 0, home_team_goals, away_team_goals)
        else:                                    # ekipa je ze v slovarju, pristejemo Z, R ali P in dane in prejete gole
            if home_team_goals > away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[home_team_id]
                Z += 1
                R += 0
                P += 0
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                slovar_ekip[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif home_team_goals < away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[home_team_id]
                Z += 0
                R += 0
                P += 1
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                slovar_ekip[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif home_team_goals == away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[home_team_id]
                Z += 0
                R += 1
                P += 0
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                slovar_ekip[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
        if away_team_id not in slovar_ekip:        #enako naredimo se za gostujoce ekipe (ce naredimo samo za domace dobimo polovico lestvice, vsaka ekipa igra 19 krogov doma)
            if away_team_goals > home_team_goals:
                slovar_ekip[away_team_id] = (1, 0, 0, away_team_goals, home_team_goals)
            elif away_team_goals < home_team_goals:
                slovar_ekip[away_team_id] = (0, 0, 1, away_team_goals, home_team_goals)
            elif away_team_goals == home_team_goals:
                slovar_ekip[away_team_id] = (0, 1, 0, away_team_goals, home_team_goals)
        else:
            if away_team_goals > home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[away_team_id]
                Z += 1
                R += 0
                P += 0
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                slovar_ekip[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif away_team_goals < home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[away_team_id]
                Z += 0
                R += 0
                P += 1
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                slovar_ekip[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif away_team_goals == home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = slovar_ekip[away_team_id]
                Z += 0
                R += 1
                P += 0
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                slovar_ekip[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)        
    
    return slovar_ekip


#funkcijo uporabimo v zgornji funkciji izracunaj_lestvico(league_id, season, krog=100)
def vse_tekme_v_sezoni(league_id, season, stage=100):
    '''Pogleda vse tekme v sezoni v podani ligi do tega kroga.'''
    s2 = f"""
    SELECT stage, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal FROM Match
        WHERE league_id = {league_id} AND season = '{season}' AND stage <= {stage}
        ORDER BY league_id, stage;
    """
    res = cur.execute(s2)
    tekme = res.fetchall()
    return tekme
#############################################


#################### nakup_igralcev

# poiscemo igralce, da jih lahko kupimo (funkcija jih vrne glede na filtre, ki smo jih dali)
def seznam_igralcev_za_prikaz(ime_igralca, vratar, branilec, vezist, napadalec, klub, manj20, manj40, manj60, manj80, manj100):
    moja_ekipa_id = 50000
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
    
    max_cena = 1000  #zelo_veliko
    if manj20 != None:
        max_cena = 20
    elif manj40 != None:
        max_cena = 40
    elif manj60 != None:
        max_cena = 60
    elif manj80 != None:
        max_cena = 80
    elif manj100 != None:
        max_cena = 100
    
    # s = f"""SELECT Player.player_name FROM Player 
    # JOIN Team ON Player.team_id = Team.team_api_id 
    # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    # WHERE Player.team_id = {moja_ekipa_id};"""
    # res = cur.execute(s)
    # moji_igralci_tuple = res.fetchall()

    s = f"""SELECT Player.player_api_id, Player.player_name, DATE(Player.birthday) AS birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, 
    Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot, Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_coordinate_y in {polozaji} AND Player.player_name like '%{ime_igralca}%' AND Team.team_long_name like '%{klub}%' AND Player_Attributes.player_cost <= {max_cena} AND Player.team_id != {moja_ekipa_id}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    res = cur.execute(s) 
    sez_igralcev = res.fetchall()
    return sez_igralcev


# da vidimo kaksen je zacetni budget (preberemo iz tabele Account)
def denar_na_zacetku():
    moja_ekipa_id = 50000
    s = f"SELECT budget FROM Account WHERE team_id = {moja_ekipa_id};"
    res = cur.execute(s)
    print(res)
    zacetni_budget = res.fetchone()[0]
    print(zacetni_budget)
    return zacetni_budget


# ko pritisnemo kupi se izvede ta funkcija
def kupi(igralec_id):
    moja_ekipa_id = 50000
    zacetni_budget = denar_na_zacetku()
    s = f"""SELECT Player.player_api_id, Player.team_id, Player.player_name, DATE(Player.birthday) AS birthday, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot, Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_api_id = {igralec_id}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    cur.execute(s)
    player_api_id, team_id, player_name, birthday, player_coordinate_x, player_coordinate_y, overall_rating, preferred_foot, cena = tuple(cur.fetchone())
    # preveri ce je ta igralec ze med kupljenimi
    s = f"SELECT COUNT(*) FROM Player WHERE team_id = {moja_ekipa_id} AND player_api_id = {player_api_id};"
    cur.execute(s)
    stevilo_enakih_v_moji_ekipi = cur.fetchone()[0]
    if stevilo_enakih_v_moji_ekipi != 0:
        raise Exception("Igralec je že v ekipi Moja Ekipa.")
    # preverimo ce imamo dovolj denarja 
    if cena <= zacetni_budget:
        # izracunamo koliko denarja nam ostane
        nov_budget = zacetni_budget - cena
        cur.execute(f"UPDATE Account SET budget = {nov_budget} WHERE team_id = {moja_ekipa_id}")
        s = f"""
            INSERT INTO Player
            (player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y) 
            VALUES ({player_api_id}, '{player_name}', (SELECT MAX(player_fifa_api_id)+1 FROM Player), '{birthday}', 50000, {player_coordinate_x}, {player_coordinate_y});
            """ 
    #ce nimamo dovolj denarja
    else:
        raise RuntimeError("Ni dovolj denarja.")
    cur.execute(s)
    con.commit()


# ko pritisnemo prodaj se izvede ta funkcija
def prodaj(igralec_id):
    moja_ekipa_id = 50000
    zacetni_budget = denar_na_zacetku()
    s = f"""SELECT Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_api_id = {igralec_id}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    #Player.player_api_id, Player.team_id, Player.player_name, DATE(Player.birthday) AS birthday, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot,
    cur.execute(s)
    cena, = tuple(cur.fetchone())
    #player_api_id, team_id, player_name, birthday, player_coordinate_x, player_coordinate_y, overall_rating, preferred_foot, 
    nov_budget = zacetni_budget + cena
    cur.execute(f"UPDATE Account SET budget = {nov_budget} WHERE team_id = {moja_ekipa_id}")
    s = f"DELETE FROM Player WHERE player_api_id = {igralec_id} AND team_id = {moja_ekipa_id};" 
    cur.execute(s)
    con.commit()


# da vidimo, koliko imamo trenutno denarja
def koliko_denarja():
    moja_ekipa_id = 50000
    s = f"SELECT budget FROM Account WHERE team_id = {moja_ekipa_id};"
    cur.execute(s)
    trenutni_budget = cur.fetchone() #dobimo tuple. V htmlju je treba extractat potem prvi element (ki je v tem primeru MojaEkipa)
    return trenutni_budget

# da vidimo koliko igralcev je trenutno v nasi ekipi
def stevilo_igralcev_v_ekipi():
    moja_ekipa_id = 50000
    s = f"SELECT COUNT(*) FROM Player WHERE team_id = {moja_ekipa_id};"
    cur.execute(s)
    stevilo_igralcev = cur.fetchone()
    return stevilo_igralcev


# def f_cena(r):
#     r = int(r) if r != None else 1
#     if r > 70:
#         return r + 10
#     else:
#         return r - 10

####################################


################## quick match
# pogleda kateri igralci so trenutno v moji ekipi
def igralci_v_ekipi(team):
    s = f"""SELECT Player.player_api_id, Player.player_name, DATE(Player.birthday) AS birthday, Team.team_long_name, Team.team_short_name,
    Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot,
    Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.team_id = {team};"""
    cur.execute(s) 
    res = cur.fetchall()
    return res

# to funkcijo rabim, da vidim vse ekipe in njihove id-je, tako lahko v html lazje zapisem, ni treba vsake ekipe posebej, ampak mi potem nekaj ne dela v html, tako da sem samo naredil to funkcijo v nekem drugem oknu in skopiral rezultat v html
def vse_ekipe():
    s = f"SELECT Team.team_api_id, Team.team_long_name FROM Team ORDER BY team_long_name;"
    cur.execute(s)
    ekipe =cur.fetchall()    # dobim seznam, ki ima notri tuple. Prvi element posamezneka tupla je team_id, drugi pa team_long_name
    vse_ekipe = "\n".join([f"<option value='{ekipa[0]}'>{ekipa[1]}</option>" for ekipa in ekipe])
    return vse_ekipe

# iz danega idja ekipe dobimo ime ekipe
def id_ekipe_v_ime(ekipa_id):
    s = f"SELECT team_long_name FROM Team WHERE team_api_id = {ekipa_id};"
    cur.execute(s)
    res = cur.fetchone()[0]
    return res

# iz danega idija lige dobimo ime lige
def id_lige_v_ime(liga_id):
    s = f"SELECT name FROM League WHERE id = {liga_id};"
    cur.execute(s)
    res = cur.fetchone()[0]
    return res


# doloci kaksen je rezultat tekme
def f_izracunaj_stohasticen_rezultat(seznam_domacih_igralcev, seznam_gostujocih_igralcev):
    utezi_ocen = slovar_ratingov = {
        'skupna_ocena': 0.6,
        'golman_ocena': 0.1,
        'branilec_ocena': 0.1,
        'vezist_ocena': 0.1,
        'napadalec_ocena': 0.1
    }
    ### domaci igralci
    # pogledamo kateri domaci igralci so v prvi postavi (kaksni so ratingi in na katerem polozaju igrajo)
    s_domaci = f"""
        SELECT Player_Attributes.overall_rating, Player.player_coordinate_y FROM Player_Attributes JOIN Player ON Player.player_api_id = Player_Attributes.player_api_id
        WHERE Player.player_api_id in {tuple(seznam_domacih_igralcev)};
    """
    cur.execute(s_domaci)
    vsi = cur.fetchall()   # seznam tuple-ov, za vsak rating in pozicijo je en tuple
    # pogledamo kaksni so ratingi na vsaki poziciji in koliko igralcev je na posamezni poziciji
    rating_vratar_domaci = 0
    st_vratar_domaci = 0
    rating_branilec_domaci = 0
    st_branilec_domaci = 0
    rating_vezist_domaci = 0
    st_vezist_domaci = 0
    rating_napadalec_domaci = 0
    st_napadalec_domaci = 0
    rating_skupen_domaci = 0
    koliko_igralcev_domaci = 0
    for el in vsi:
        rating = el[0]
        pozicija = POZICIJE[el[1]]
        print(rating, pozicija)
        if pozicija == 'vratar':
            rating_vratar_domaci += rating
            st_vratar_domaci += 1
            rating_skupen_domaci += rating
            koliko_igralcev_domaci += 1
        if pozicija == 'branilec':
            rating_branilec_domaci += rating
            st_branilec_domaci += 1
            rating_skupen_domaci += rating
            koliko_igralcev_domaci += 1
        if pozicija == 'vezist':
            rating_vezist_domaci += rating
            st_vezist_domaci += 1
            rating_skupen_domaci += rating
            koliko_igralcev_domaci += 1
        if pozicija == 'napadalec':
            rating_napadalec_domaci += rating
            st_napadalec_domaci += 1
            rating_skupen_domaci += rating
            koliko_igralcev_domaci += 1
    # pogledamo nekaj cudnih primerov, ce se to zgodi bomo na koncu pristeli gole (ker ce nimas v golu golmana (ampak igralca) zagotovo dobis vec golov)
    ni_vratarja_domaci = 0  # druga ekipa +
    if st_vratar_domaci == 0:
        ni_vratarja_domaci = 2
    if st_vratar_domaci > 1:      # ce je vec vratarjev, jih v skupnem ratingu ne bomo steli (v ratingu vratarjev, ki ga bomo mnozili z 0,1 se vedno ostanejo) 
        rating_skupen_domaci -= rating_vratar_domaci // st_vratar_domaci
    premalo_branilcev_domaci = 0  # druga ekipa +
    if st_branilec_domaci < 3:
        premalo_branilcev_domaci = 2
    premalo_vezistov_domaci = 0  # druga ekipa +
    if st_vezist_domaci < 2:
        premalo_vezistov_domaci = 1
    veliko_napadalcev_domaci = 0   # domaci +
    if st_napadalec_domaci > 3:
        veliko_napadalcev_domaci = 1

    # naredimo slovar z vsemi ratingi v domaci ekipi, kljuci so isti kot v slovarju utezi_ocen
    slovar_ratingov_domaci = {
        'skupna_ocena': rating_skupen_domaci,
        'golman_ocena': rating_vratar_domaci,
        'branilec_ocena': rating_branilec_domaci,
        'vezist_ocena': rating_vezist_domaci,
        'napadalec_ocena': rating_napadalec_domaci
    }
    # po formuli dobimo skupne ocene domacih (to bomo uporabili za izracun verjetnosti, da zmaga domaci (oz gostujoci))
    skupne_ocene_domacih = sum([utezi_ocen[key] * slovar_ratingov_domaci[key] for key in utezi_ocen])
    print(skupne_ocene_domacih)

    ### pogledamo gostujoce igralce
    s_gostje = f"""
        SELECT Player_Attributes.overall_rating, Player.player_coordinate_y FROM Player_Attributes JOIN Player ON Player.player_api_id = Player_Attributes.player_api_id
        WHERE Player.player_api_id in {tuple(seznam_gostujocih_igralcev)};
    """
    cur.execute(s_gostje)
    vsi_g = cur.fetchall()   # seznam tuple-ov, za vsak rating in pozicijo je en tuple
    # pogledamo posamezne ratinge za gostujoce
    rating_vratar_gostujoci = 0
    st_vratar_gostujoci = 0
    rating_branilec_gostujoci = 0
    st_branilec_gostujoci = 0
    rating_vezist_gostujoci = 0
    st_vezist_gostujoci = 0
    rating_napadalec_gostujoci = 0
    st_napadalec_gostujoci = 0
    rating_skupen_gostujoci = 0
    koliko_igralcev_gostujoci = 0
    for el in vsi_g:
        rating = el[0]
        pozicija = POZICIJE[el[1]]
        print(rating, pozicija)
        if pozicija == 'vratar':
            rating_vratar_gostujoci += rating
            st_vratar_gostujoci += 1
            rating_skupen_gostujoci += rating
            koliko_igralcev_gostujoci += 1
        if pozicija == 'branilec':
            rating_branilec_gostujoci += rating
            st_branilec_gostujoci += 1
            rating_skupen_gostujoci += rating
            koliko_igralcev_gostujoci += 1
        if pozicija == 'vezist':
            rating_vezist_gostujoci += rating
            st_vezist_gostujoci += 1
            rating_skupen_gostujoci += rating
            koliko_igralcev_gostujoci += 1
        if pozicija == 'napadalec':
            rating_napadalec_gostujoci += rating
            st_napadalec_gostujoci += 1
            rating_skupen_gostujoci += rating
            koliko_igralcev_gostujoci += 1

    # pogledamo cudne primere
    ni_vratarja_gostujoci = 0  # druga ekipa +
    if st_vratar_gostujoci == 0:
        ni_vratarja_gostujoci = 3
    if st_vratar_gostujoci > 1:      # ce je vec vratarjev, jih v skupnem ratingu ne bomo steli (v ratingu vratarjev, ki ga bomo mnozili z 0,1 se vedno ostanejo) 
        rating_skupen_gostujoci -= rating_vratar_gostujoci // st_vratar_gostujoci
    premalo_branilcev_gostujoci = 0  # druga ekipa +
    if st_branilec_gostujoci < 3:
        premalo_branilcev_gostujoci = 2
    premalo_vezistov_gostujoci = 0  # druga ekipa +
    if st_vezist_gostujoci < 2:
        premalo_vezistov_gostujoci = 1
    veliko_napadalcev_gostujoci = 0   # gostujoci +
    if st_napadalec_gostujoci > 3:
        veliko_napadalcev_gostujoci = 1

    # kljuci so isti kot pri utezi_ocen
    slovar_ratingov_gostujoci = {
        'skupna_ocena': rating_skupen_gostujoci,
        'golman_ocena': rating_vratar_gostujoci,
        'branilec_ocena': rating_branilec_gostujoci,
        'vezist_ocena': rating_vezist_gostujoci,
        'napadalec_ocena': rating_napadalec_gostujoci
    }

    # po formuli izracunamo
    skupne_ocene_gostujocih = sum([utezi_ocen[key] * slovar_ratingov_gostujoci[key] for key in utezi_ocen])
    print(skupne_ocene_gostujocih)

    ## verjetnost, da zmaga posamezna ekipa
    zmaga_domaci_verjetnost= skupne_ocene_domacih / (skupne_ocene_domacih + skupne_ocene_gostujocih)
    zmaga_gostujoci_verjetnost = 1 - zmaga_domaci_verjetnost

    # pgledamo procente, zaokrozimo na celo stevilo
    zmaga_domaci_verjetnost = int(zmaga_domaci_verjetnost * 100)
    zmaga_gostujoci_verjetnost = int(zmaga_gostujoci_verjetnost * 100)

    # mozni rezultati
    rezultati_zmaga_domaci = ["1 : 0", "2 : 0", "3 : 0", "2 : 1", "3 : 1", "3 : 2"] * (zmaga_domaci_verjetnost + 3) ## +3 zato, ker imajo prednost domacega igrisca
    if zmaga_gostujoci_verjetnost < 3:        #ce bi se to slucajno nekako zgodilo
        rezultati_zmaga_gostujoci = ["0 : 1", "0 : 2", "0 : 3", "1 : 2", "1 : 3", "2 : 3"] * (zmaga_gostujoci_verjetnost)
    rezultati_zmaga_gostujoci = ["0 : 1", "0 : 2", "0 : 3", "1 : 2", "1 : 3", "2 : 3"] * (zmaga_gostujoci_verjetnost - 3)  #v gosteh je tezje
    rezultat_izenacen_verjetno = ["0 : 0", "1 : 1"] * 50
    rezultat_izenacen_manj_verjetno = ["2 : 2", "3 : 3"] * 10

    smiselni_rezultati = rezultati_zmaga_domaci + rezultati_zmaga_gostujoci + rezultat_izenacen_verjetno + rezultat_izenacen_manj_verjetno

    #smiselni_rezultati = ["0 : 0", "0 : 1", "0 : 2", "0 : 3", "1 : 0", "1 : 1", "1 : 2", "1 : 3", "2 : 0", "2 : 1", "2 : 2", "2 : 3", "3 : 0", "3 : 1", "3 : 2", "3 : 3"]
    #smiselni_rezultati.extend(["0 : 0"] * 100)

    # pogledamo rezultat (z random izbiro)
    rezultat = random.choice(smiselni_rezultati)

    domaci_goli = int(rezultat[0])
    gostujoci_goli = int(rezultat[-1])

    # pristejemo gole za cudne primere
    domaci_goli = domaci_goli + veliko_napadalcev_domaci + ni_vratarja_gostujoci + premalo_branilcev_gostujoci + premalo_vezistov_gostujoci
    gostujoci_goli = gostujoci_goli + veliko_napadalcev_gostujoci + ni_vratarja_domaci + premalo_branilcev_domaci + premalo_vezistov_domaci

    # ce zmaga na papirju slabsa ekipa, naredimo tako, da ne zmaga za prevec golov
    if domaci_goli > gostujoci_goli + 1 and rating_skupen_gostujoci > rating_skupen_domaci:
        domaci_goli -= 1
    if domaci_goli + 1 < gostujoci_goli and rating_skupen_gostujoci < rating_skupen_domaci:
        gostujoci_goli -= 1
    
    return f"{domaci_goli} : {gostujoci_goli}"


# pogleda koliko igralcev je v nasi ekipi
def stevilo_igralcev_v_moji_ekipi():
    moja_ekipa_id = 50000
    s = f"SELECT COUNT(*) FROM Player WHERE team_id = {moja_ekipa_id}"
    cur.execute(s)
    res = cur.fetchone()[0]
    return res

# v kateri ekipi so igralci v tuplu idji_igralcev
def katera_ekipa(idji_igralcev):
    # grdo (poizkusi tudi kako drugace)
    s = f"""SELECT Team.team_long_name FROM Team JOIN Player ON Team.team_api_id = Player.team_id 
        WHERE Player.player_api_id IN {idji_igralcev}
        GROUP BY team_long_name
        HAVING COUNT(*) = 11;"""
    cur.execute(s)
    res = cur.fetchone()[0]
    return res
#############

### ekipa/<ime_ekipe>
# jo uporabimo, da vidimo igralce posamezne ekipe
def ekipa_model(ime_ekipe):
    s = f"""SELECT Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
            JOIN Team ON Player.team_id = Team.team_api_id WHERE Team.team_long_name = '{ime_ekipe}';"""
    res = cur.execute(s) 
    igralci = res.fetchall()
    return ime_ekipe, igralci
