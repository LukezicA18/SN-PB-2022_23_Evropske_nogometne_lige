import sqlite3

def izracunaj_lestvico(cur, league_id, season, krog=100):

    tekme = vse_tekme_v_sezoni(cur, league_id, season, krog)
    # {ekipa_id: (Z, R, P, dani_goli, prejeti_goli)}
    sl = {}

    for stage, date, home_team_id, away_team_id, home_team_goals, away_team_goals in tekme:
        if home_team_id not in sl:
            if home_team_goals > away_team_goals:
                sl[home_team_id] = (1, 0, 0, home_team_goals, away_team_goals)
            elif home_team_goals < away_team_goals:
                sl[home_team_id] = (0, 0, 1, home_team_goals, away_team_goals)
            elif home_team_goals == away_team_goals:
                sl[home_team_id] = (0, 1, 0, home_team_goals, away_team_goals)
        else:
            if home_team_goals > away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
                Z += 1
                R += 0
                P += 0
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif home_team_goals < away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
                Z += 0
                R += 0
                P += 1
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif home_team_goals == away_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[home_team_id]
                Z += 0
                R += 1
                P += 0
                dani_goli += home_team_goals
                prejeti_goli += away_team_goals
                sl[home_team_id] = (Z, R, P, dani_goli, prejeti_goli)
        if away_team_id not in sl:
            if away_team_goals > home_team_goals:
                sl[away_team_id] = (1, 0, 0, away_team_goals, home_team_goals)
            elif away_team_goals < home_team_goals:
                sl[away_team_id] = (0, 0, 1, away_team_goals, home_team_goals)
            elif away_team_goals == home_team_goals:
                sl[away_team_id] = (0, 1, 0, away_team_goals, home_team_goals)
        else:
            if away_team_goals > home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
                Z += 1
                R += 0
                P += 0
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif away_team_goals < home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
                Z += 0
                R += 0
                P += 1
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)
            elif away_team_goals == home_team_goals:
                Z, R, P, dani_goli, prejeti_goli = sl[away_team_id]
                Z += 0
                R += 1
                P += 0
                dani_goli += away_team_goals
                prejeti_goli += home_team_goals
                sl[away_team_id] = (Z, R, P, dani_goli, prejeti_goli)        
    
    return sl




def vse_tekme_v_sezoni(cur, league_id, season, stage=100):
    s2 = f"""
    SELECT 
        stage, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal
        FROM Match
        WHERE league_id = {league_id} AND season = '{season}' AND stage <= {stage}
        ORDER BY league_id, stage;
    """
    res = cur.execute(s2)
    tekme = res.fetchall()
    return tekme






# def uvoziSQL(cur, datoteka):
#     with open(datoteka) as f:
#         koda = f.read()
#         cur.executescript(koda)
    
# with sqlite3.connect(baza_datoteka) as baza:
#     cur = baza.cursor()
#     # uvoziSQL(cur, "poskus.sql")
#     uvoziSQL(cur, "country.sql")
#     uvoziSQL(cur, "league.sql")
#     uvoziSQL(cur, "match.sql")
#     uvoziSQL(cur, "player.sql")
#     uvoziSQL(cur, "player_attributes.sql")
#     uvoziSQL(cur, "team.sql")
#     uvoziSQL(cur, "team_attributes.sql")
# exit()


# print("Katere tabele so v bazi?")
# with sqlite3.connect(baza_datoteka) as con:
#     cur = con.cursor()
#     res = cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
#     print(res.fetchall())

# print("Katere vrstice so v tabeli?")
# with sqlite3.connect(baza_datoteka) as con:
#     cur = con.cursor()
#     cur.execute("SELECT COUNT(*) FROM Match WHERE league_id = 1729")
#     #print(cur.fetchall())    ## fetchall kliče tolikokrat doker se ne izprazni vse (če bi potem poklicali še enkrat fetchall bi dobili prazno)
#     for podatek in cur:
#         print(podatek)



# TODO: Tukaj moramo ustvariti bazo, če je še ni

#baza.pripravi_vse(conn)   #naj naredi baza vse kar je treba delati

#class Model:
    #def dobi_vse_uporabnike(self):
        #with conn:
            #cur = conn.execute("""
            #SELECT * FROM uporabnik
            #""")
            #return cur.fetchall()



# IZBRIŠEMO ODVEČNE FIFA KARTICE
# SELECT * FROM Player_Attributes
# JOIN (
#   SELECT player_api_id, MAX(date) AS max_date FROM Player_Attributes
#   GROUP BY player_api_id
# ) AS recent_dates
# ON Player_Attributes.player_api_id = recent_dates.player_api_id
# WHERE Player_Attributes.date = recent_dates.max_date AND date > '2015-01-01 00:00:00';