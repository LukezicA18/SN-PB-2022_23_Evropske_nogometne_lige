import sqlite3

baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()


s = "SELECT Team.team_api_id, Team.team_long_name FROM Team ORDER BY team_long_name;"
cur.execute(s)
res =cur.fetchall()
# for ekipa in res:
#     print(ekipa[0])
print(res)
vse_ekipe = "\n".join([f"<option value={ekipa[0]}>{ekipa[1]}</option>" for ekipa in res])
print(vse_ekipe)