import sqlite3


def uvoziSQL(cur, datoteka):
    with open(datoteka) as f:
        koda = f.read()
        cur.executescript(koda)
    
baza = "baza_nogomet.db"
ponostavi_bazo = True

if ponostavi_bazo:
    with sqlite3.connect(baza) as conn:
        cur = conn.cursor()
        # uvoziSQL(cur, "nogometne_lige.sql")
        uvoziSQL(cur, "podatki/country.sql")
        uvoziSQL(cur, "podatki/league.sql")
        uvoziSQL(cur, "podatki/match.sql")
        uvoziSQL(cur, "podatki/player.sql")
        uvoziSQL(cur, "podatki/player_attributes.sql")
        uvoziSQL(cur, "podatki/team.sql")
        uvoziSQL(cur, "podatki/team_attributes.sql")

with sqlite3.connect(baza) as con:
    cur = con.cursor()
    res = cur.execute("SELECT * FROM Country limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM League limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM Match limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM Player limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM Player_Attributes limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM Team limit 10;")
    print(res.fetchall())
    res = cur.execute("SELECT * FROM Team_Attributes limit 10;")
    print(res.fetchall())

    res = cur.execute("SELECT COUNT(*) FROM Country;")
    print(f"Country {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM League;")
    print(f"League {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM Match;")
    print(f"Match {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM Player;")
    print(f"Player {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM Player_Attributes;")
    print(f"Player_Attributes {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM Team;")
    print(f"Team {res.fetchone()}")
    res = cur.execute("SELECT COUNT(*) FROM Team_Attributes;")
    print(f"Team_Attributes {res.fetchone()}")