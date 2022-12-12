
def ustvari_tabele(conn):
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS
            uporabnik(
                uid INTEGER PRIMARY KEY,
                username TEXT,
                name TEXT
            )
            """
        )

def napolni_nujne_podatke(conn):
    with conn:
        conn.execute("""
            INSERT INTO uporabnik
            (username, name) VALUES
            ("email@gmail.com", "ime")
            """)

def pripravi_vse(conn):
    ustvari_tabele(conn)
    napolni_nujne_podatke(conn)
