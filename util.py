
import sqlite3


baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()

matches = cur.execute("select home_team_api_id, away_team_api_id, home_player_1, home_player_2, home_player_3, home_player_4, home_player_5, home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11, away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, away_player_6, away_player_7, away_player_8, away_player_9, away_player_10, away_player_11 from Match")
matches = matches.fetchall()

for match in matches:
    print(match)
    (home_team_api_id, 
    away_team_api_id,
    home_player_1,
    home_player_2,
    home_player_3,
    home_player_4,
    home_player_5,
    home_player_6,
    home_player_7,
    home_player_8,
    home_player_9,
    home_player_10,
    home_player_11,
    away_player_1,
    away_player_2,
    away_player_3,
    away_player_4,
    away_player_5,
    away_player_6,
    away_player_7,
    away_player_8,
    away_player_9,
    away_player_10,
    away_player_11) = match

    # home team
    for i in range(11):
        player_id = match[2+i]
        if player_id == None: continue
        s = f"""update Player 
            set team_id = {home_team_api_id} 
            where player_api_id = {player_id}"""
        cur.execute(s)
        con.commit()
    # away team
    for i in range(11):
        player_id = match[i+13]
        if player_id == None: continue
        s = f"""update Player 
                set team_id = {away_team_api_id}
                where player_api_id = {player_id}"""
        cur.execute(s)
        con.commit()



#na kateri poziciji je igralec

matches = cur.execute("""select home_team_api_id, away_team_api_id, home_player_X1, home_player_X2, home_player_X3, home_player_X4, home_player_X5,
                            home_player_X6, home_player_X7, home_player_X8, home_player_X9, home_player_X10, home_player_X11, away_player_X1, 
                            away_player_X2, away_player_X3, away_player_X4, away_player_X5, away_player_X6, away_player_X7, away_player_X8, 
                            away_player_X9, away_player_X10, away_player_X11, home_player_Y1, home_player_Y2, home_player_Y3, home_player_Y4,
                            home_player_Y5, home_player_Y6, home_player_Y7, home_player_Y8, home_player_Y9, home_player_Y10, home_player_Y11, 
                            away_player_Y1, away_player_Y2, away_player_Y3, away_player_Y4, away_player_Y5, away_player_Y6, away_player_Y7,
                            away_player_Y8, away_player_Y9, away_player_Y10, away_player_Y11, home_player_1, home_player_2, home_player_3,
                            home_player_4, home_player_5, home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11, 
                            away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, away_player_6, away_player_7, away_player_8, 
                            away_player_9, away_player_10, away_player_11
                            from Match""")
matches = matches.fetchall()

for match in matches:
    (home_team_api_id, away_team_api_id, home_player_X1, home_player_X2, home_player_X3, home_player_X4, home_player_X5, home_player_X6, home_player_X7, home_player_X8, home_player_X9, home_player_X10, home_player_X11, away_player_X1, 
                            away_player_X2, away_player_X3, away_player_X4, away_player_X5, away_player_X6, away_player_X7, away_player_X8, 
                            away_player_X9, away_player_X10, away_player_X11, home_player_Y1, home_player_Y2, home_player_Y3, home_player_Y4,
                            home_player_Y5, home_player_Y6, home_player_Y7, home_player_Y8, home_player_Y9, home_player_Y10, home_player_Y11, 
                            away_player_Y1, away_player_Y2, away_player_Y3, away_player_Y4, away_player_Y5, away_player_Y6, away_player_Y7,
                            away_player_Y8, away_player_Y9, away_player_Y10, away_player_Y11, home_player_1, home_player_2, home_player_3,
                            home_player_4, home_player_5, home_player_6, home_player_7, home_player_8, home_player_9, home_player_10, home_player_11, 
                            away_player_1, away_player_2, away_player_3, away_player_4, away_player_5, away_player_6, away_player_7, away_player_8, 
                            away_player_9, away_player_10, away_player_11) = match

     # home team and away team
    for i in range(22):
        player_x = match[2+i]
        player_y = match[24+i]
        player_id = match[46+i]
        if player_id == None: continue
        s = f""" update Player
            set player_coordinate_x = {player_x}, player_coordinate_y = {player_y}
            where player_api_id = {player_id}"""
        cur.execute(s)
        con.commit()