import sqlite3

baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()


s = f"""SELECT Team.team_long_name, Team.team_short_name FROM Team 
        JOIN League ON Team.league_id = League.id
        JOIN Match ON Match.h
        limit 10
    """






league_id = 1729
season = '2015/2016'

s = izracunaj_lestvico(cur, league_id, season)
print(len(s))
for x in sorted(s.values()):
    print(x)

