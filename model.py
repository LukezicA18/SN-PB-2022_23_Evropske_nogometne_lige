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
    if manj100 != None:
        max_cena = 100
    elif manj80 != None:
        max_cena = 80
    elif manj60 != None:
        max_cena = 60
    elif manj40 != None:
        max_cena = 40
    elif manj20 != None:
        max_cena = 20

    s = f"""SELECT Player.player_api_id, Player.player_name, DATE(Player.birthday) AS birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, 
    Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot, Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.player_coordinate_y in {polozaji} AND Player.player_name like '%{ime_igralca}%' AND Team.team_long_name like '%{klub}%' AND Player_Attributes.player_cost <= {max_cena} AND Player.team_id != {moja_ekipa_id}
    ORDER BY Player_Attributes.overall_rating DESC;"""
    res = cur.execute(s) 
    sez_igralcev = res.fetchall()
    return sez_igralcev


def denar_na_zacetku():
    moja_ekipa_id = 50000
    s = f"SELECT budget FROM Account WHERE team_id = {moja_ekipa_id};"
    res = cur.execute(s)
    print(res)
    zacetni_budget = res.fetchone()[0]
    print(zacetni_budget)
    #print(zacetni_budget)
    return zacetni_budget


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
    # TODO preveri ce je ta igralec ze med kupljenimi
    s = f"SELECT COUNT(*) FROM Player WHERE team_id = {moja_ekipa_id} AND player_api_id = {player_api_id};"
    cur.execute(s)
    stevilo_enakih_v_moji_ekipi = cur.fetchone()[0]
    if stevilo_enakih_v_moji_ekipi != 0:
        raise Exception("Igralec je ze v MojaEkipa")
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
    #ce nimmo dovolj denarja
    else:
        raise RuntimeError("Ni dovolj denarja.")
    cur.execute(s)
    con.commit()


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
    # TODO preveri ce je ta igralec ze med kupljenimi, ce ni ga ne mores prodati!!!

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


# def kupi(igralec_id):
#     cur.execute(f"SELECT player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y FROM Player WHERE player_api_id = {igralec_id};")
#     player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y = tuple(cur.fetchone())
#     # TODO preveri ce je ta igralec ze med kupljenimi
#     # TODO denar se mora odsteti od budgeta
#     s = f"""
#         INSERT INTO Player
#         (player_api_id, player_name, player_fifa_api_id, birthday, team_id, player_coordinate_x, player_coordinate_y) 
#         VALUES ({player_api_id}, '{player_name}', (SELECT MAX(player_fifa_api_id)+1 FROM Player), '{birthday}', 50000, {player_coordinate_x}, {player_coordinate_y});
#     """ 
#     cur.execute(s)
#     con.commit()
####################################


def igralci_v_ekipi(team):
    # # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
    # s = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    # JOIN Team ON Player.team_id = Team.team_api_id 
    # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    # WHERE Player.team_id = {team}
    # ORDER BY Player_Attributes.overall_rating DESC;"""
    # cur.execute(s) 
    # res = cur.fetchall()
    # return res
    s = f"""SELECT Player.player_api_id, Player.player_name, DATE(Player.birthday) AS birthday, Team.team_long_name, Team.team_short_name,
    Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating, Player_Attributes.preferred_foot,
    Player_Attributes.player_cost FROM Player 
    JOIN Team ON Player.team_id = Team.team_api_id 
    JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    WHERE Player.team_id = {team};"""
    cur.execute(s) 
    res = cur.fetchall()
    return res

    # def igralci_v_ekipi(team):
    # # TODO pogruntaj zakaj select ne vrne igralcev za mojo ekipo
    # s = f"""SELECT Player.player_api_id, Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y, Player_Attributes.overall_rating FROM Player 
    # JOIN Team ON Player.team_id = Team.team_api_id 
    # JOIN Player_Attributes ON Player.player_api_id = Player_Attributes.player_api_id
    # WHERE Player.team_id = {team}
    # ORDER BY Player_Attributes.overall_rating DESC;"""
    # cur.execute(s) 
    # res = cur.fetchall()
    # return res

# to funkcijo rabim, da vidim vse ekipe in njihove id-je, tako lahko v html lazje zapisem, ni treba vsake ekipe posebej, ampak mi potem nekaj ne dela v html, tako da sem samo naredil to funkcijo v nekem drugem oknu in skopiral rezultat v html
def vse_ekipe():
    s = f"SELECT Team.team_api_id, Team.team_long_name FROM Team ORDER BY team_long_name;"
    cur.execute(s)
    ekipe =cur.fetchall()    # dobim seznam, ki ima notri tuple. Prvi element posamezneka tupla je team_id, drugi pa team_long_name
    vse_ekipe = "\n".join([f"<option value='{ekipa[0]}'>{ekipa[1]}</option>" for ekipa in ekipe])
    return vse_ekipe

def id_ekipe_v_ime(ekipa_id):
    s = f"SELECT team_long_name FROM Team WHERE team_api_id = {ekipa_id};"
    cur.execute(s)
    res = cur.fetchone()[0]
    return res

def id_lige_v_ime(liga_id):
    s = f"SELECT name FROM League WHERE id = {liga_id};"
    cur.execute(s)
    res = cur.fetchone()[0]
    return res

def ekipa_model(ime_ekipe):
    s = f"""SELECT Player.player_name, Player.birthday, Team.team_long_name, Team.team_short_name, Player.player_coordinate_x, Player.player_coordinate_y FROM Player 
            JOIN Team ON Player.team_id = Team.team_api_id WHERE Team.team_long_name = '{ime_ekipe}';"""
    res = cur.execute(s) 
    igralci = res.fetchall()
    return ime_ekipe, igralci

def f_izracunaj_stohasticen_rezultat(seznam_home_igralcev, seznam_away_igralcev):
    s_home = f"""
        SELECT overall_rating from Player_Attributes 
        WHERE player_api_id in {tuple(seznam_home_igralcev)}
    """
    cur.execute(s_home)
    vsi = cur.fetchall()
    home_rating = sum(x[0] for x in vsi)
    s_away = f"""
        SELECT overall_rating from Player_Attributes 
        WHERE player_api_id in {tuple(seznam_away_igralcev)}
    """
    cur.execute(s_away)
    vsi = cur.fetchall()
    away_rating = sum(x[0] for x in vsi)
    print(home_rating, away_rating)
    smiselni_rezultati = ["0 : 0", "0 : 1", "0 : 2", "0 : 3", "1 : 0", "1 : 1", "1 : 2", "1 : 3", "2 : 0", "2 : 1", "2 : 2", "2 : 3", "3 : 0", "3 : 1", "3 : 2", "3 : 3"] 
    return random.choice(smiselni_rezultati) + f" home rating:{home_rating}, away rating:{away_rating}"


# import sqlite3

# def izracunaj_lestvico(cur, league_id, season, krog=100):

#     tekme = vse_tekme_v_sezoni(cur, league_id, season, krog)
#     # {ekipa_id: (Z, R, P, dani_goli, prejeti_goli)}
#     sl = {}

#     for stage, date, home_team_id, away_team_id, home_team_goals, away_team_goals in tekme:
#         if home_team_id not in sl:
#             if home_team_goals > away_team_goals:
#                 sl[home_team_id] = (1, 0, 0, home_team_goals, away_team_goals)
#             elif home_team_goals < away_team_goals:
#                 sl[home_team_id] = (0, 0, 1, home_team_goals, away_team_goals)
#             elif home_team_goals == away_team_goals:
#                 sl[home_team_id] = (0, 1, 0, home_team_goals, away_team_goals)
#         else:
#             if home_team_goals > away_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
#                 Z += 1
#                 R += 0
#                 P += 0
#                 dani_goli += home_team_goals
#                 prejeti_goli += away_team_goals
#                 sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
#             elif home_team_goals < away_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
#                 Z += 0
#                 R += 0
#                 P += 1
#                 dani_goli += home_team_goals
#                 prejeti_goli += away_team_goals
#                 sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
#             elif home_team_goals == away_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
#                 Z += 0
#                 R += 1
#                 P += 0
#                 dani_goli += home_team_goals
#                 prejeti_goli += away_team_goals
#                 sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
#         if away_team_id not in sl:
#             if away_team_goals > home_team_goals:
#                 sl[away_team_id] = (1, 0, 0, away_team_goals, home_team_goals)
#             elif away_team_goals < home_team_goals:
#                 sl[away_team_id] = (0, 0, 1, away_team_goals, home_team_goals)
#             elif away_team_goals == home_team_goals:
#                 sl[away_team_id] = (0, 1, 0, away_team_goals, home_team_goals)
#         else:
#             if away_team_goals > home_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
#                 Z += 1
#                 R += 0
#                 P += 0
#                 dani_goli += away_team_goals
#                 prejeti_goli += home_team_goals
#                 sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
#             elif away_team_goals < home_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
#                 Z += 0
#                 R += 0
#                 P += 1
#                 dani_goli += away_team_goals
#                 prejeti_goli += home_team_goals
#                 sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
#             elif away_team_goals == home_team_goals:
#                 Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
#                 Z += 0
#                 R += 1
#                 P += 0
#                 dani_goli += away_team_goals
#                 prejeti_goli += home_team_goals
#                 sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)        
    
#     return sl




# def vse_tekme_v_sezoni(cur, league_id, season, stage=100):
#     s2 = f"""
#     SELECT 
#         stage, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal
#         FROM Match
#         WHERE league_id = {league_id} AND season = '{season}' AND stage <= {stage}
#         ORDER BY league_id, stage;
#     """
#     res = cur.execute(s2)
#     tekme = res.fetchall()
#     return tekme






# # def uvoziSQL(cur, datoteka):
# #     with open(datoteka) as f:
# #         koda = f.read()
# #         cur.executescript(koda)
    
# # with sqlite3.connect(baza_datoteka) as baza:
# #     cur = baza.cursor()
# #     # uvoziSQL(cur, "poskus.sql")
# #     uvoziSQL(cur, "country.sql")
# #     uvoziSQL(cur, "league.sql")
# #     uvoziSQL(cur, "match.sql")
# #     uvoziSQL(cur, "player.sql")
# #     uvoziSQL(cur, "player_attributes.sql")
# #     uvoziSQL(cur, "team.sql")
# #     uvoziSQL(cur, "team_attributes.sql")
# # exit()


# # print("Katere tabele so v bazi?")
# # with sqlite3.connect(baza_datoteka) as con:
# #     cur = con.cursor()
# #     res = cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
# #     print(res.fetchall())

# # print("Katere vrstice so v tabeli?")
# # with sqlite3.connect(baza_datoteka) as con:
# #     cur = con.cursor()
# #     cur.execute("SELECT COUNT(*) FROM Match WHERE league_id = 1729")
# #     #print(cur.fetchall())    ## fetchall kliče tolikokrat doker se ne izprazni vse (če bi potem poklicali še enkrat fetchall bi dobili prazno)
# #     for podatek in cur:
# #         print(podatek)



# # TODO: Tukaj moramo ustvariti bazo, če je še ni

# #baza.pripravi_vse(conn)   #naj naredi baza vse kar je treba delati

# #class Model:
#     #def dobi_vse_uporabnike(self):
#         #with conn:
#             #cur = conn.execute("""
#             #SELECT * FROM uporabnik
#             #""")
#             #return cur.fetchall()



# # IZBRIŠEMO ODVEČNE FIFA KARTICE
# # SELECT * FROM Player_Attributes
# # JOIN (
# #   SELECT player_api_id, MAX(date) AS max_date FROM Player_Attributes
# #   GROUP BY player_api_id
# # ) AS recent_dates
# # ON Player_Attributes.player_api_id = recent_dates.player_api_id
# # WHERE Player_Attributes.date = recent_dates.max_date AND date > '2015-01-01 00:00:00';