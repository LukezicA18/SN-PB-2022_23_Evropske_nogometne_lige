import sqlite3
import random

baza = "baza_nogomet.db"
con = sqlite3.connect(baza)
cur = con.cursor()

POZICIJE = {1:"vratar", 2:"branilec", 3:"branilec", 4:"branilec", 5:"branilec", 6:"vezist", 7:"vezist", 8:"vezist", 9:"napadalec", 10:"napadalec", 11:"napadalec"}


print(["0 : 0", "0 : 1", "0 : 2", "0 : 3"] * 10)

# s = "SELECT Team.team_api_id, Team.team_long_name FROM Team ORDER BY team_long_name;"
# cur.execute(s)
# res =cur.fetchall()
# # for ekipa in res:
# #     print(ekipa[0])
# print(res)
# vse_ekipe = "\n".join([f"<option value={ekipa[0]}>{ekipa[1]}</option>" for ekipa in res])
# print(vse_ekipe)


# t = [["0 : 0"] * 100, "0 : 1", "0 : 2", "0 : 3", "1 : 0", "1 : 1", "1 : 2", "1 : 3", "2 : 0", "2 : 1", "2 : 2", "2 : 3", "3 : 0", "3 : 1", "3 : 2", "3 : 3"] 
# print(t)



def f_izracunaj_stohasticen_rezultat(seznam_domacih_igralcev, seznam_gostujocih_igralcev):
    utezi_ocen = slovar_ratingov = {
        'skupna_ocena': 0.6,
        'golman_ocena': 0.1,
        'branilec_ocena': 0.1,
        'vezist_ocena': 0.1,
        'napadalec_ocena': 0.1
    }
    s_domaci = f"""
        SELECT Player_Attributes.overall_rating, Player.player_coordinate_y FROM Player_Attributes JOIN Player ON Player.player_api_id = Player_Attributes.player_api_id
        WHERE Player.player_api_id in {tuple(seznam_domacih_igralcev)};
    """
    cur.execute(s_domaci)
    vsi = cur.fetchall()   # seznam tuple-ov, za vsak rating in pozicijo je en tuple
    print(vsi)
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
    print(rating_vratar_domaci)
    print(st_vratar_domaci)
    print(rating_branilec_domaci)
    print(st_branilec_domaci)
    print(rating_vezist_domaci)
    print(st_vezist_domaci)
    print(rating_napadalec_domaci)
    print(st_napadalec_domaci)
    print(rating_skupen_domaci)
    print(koliko_igralcev_domaci)
    #player_api_id, team_id, player_name, birthday, player_coordinate_x, player_coordinate_y, overall_rating, preferred_foot, cena = tuple(cur.fetchone())
    ni_vratarja_domaci = 0  # druga ekipa +
    if st_vratar_domaci == 0:
        ni_vratarja_domaci = 3
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

    slovar_ratingov_domaci = {
        'skupna_ocena': rating_skupen_domaci,
        'golman_ocena': rating_vratar_domaci,
        'branilec_ocena': rating_branilec_domaci,
        'vezist_ocena': rating_vezist_domaci,
        'napadalec_ocena': rating_napadalec_domaci
    }

    skupne_ocene_domacih = sum([utezi_ocen[key] * slovar_ratingov_domaci[key] for key in utezi_ocen])
    print(skupne_ocene_domacih)




    s_gostje = f"""
        SELECT Player_Attributes.overall_rating, Player.player_coordinate_y FROM Player_Attributes JOIN Player ON Player.player_api_id = Player_Attributes.player_api_id
        WHERE Player.player_api_id in {tuple(seznam_gostujocih_igralcev)};
    """
    cur.execute(s_gostje)
    vsi_g = cur.fetchall()   # seznam tuple-ov, za vsak rating in pozicijo je en tuple
    print(vsi_g)
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
    print(rating_vratar_gostujoci)
    print(st_vratar_gostujoci)
    print(rating_branilec_gostujoci)
    print(st_branilec_gostujoci)
    print(rating_vezist_gostujoci)
    print(st_vezist_gostujoci)
    print(rating_napadalec_gostujoci)
    print(st_napadalec_gostujoci)
    print(rating_skupen_gostujoci)
    print(koliko_igralcev_gostujoci)
    #player_api_id, team_id, player_name, birthday, player_coordinate_x, player_coordinate_y, overall_rating, preferred_foot, cena = tuple(cur.fetchone())
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

    slovar_ratingov_gostujoci = {
        'skupna_ocena': rating_skupen_gostujoci,
        'golman_ocena': rating_vratar_gostujoci,
        'branilec_ocena': rating_branilec_gostujoci,
        'vezist_ocena': rating_vezist_gostujoci,
        'napadalec_ocena': rating_napadalec_gostujoci
    }

    skupne_ocene_gostujocih = sum([utezi_ocen[key] * slovar_ratingov_gostujoci[key] for key in utezi_ocen])
    print(skupne_ocene_gostujocih)

    ## verjetnost, da zmaga posamezna ekipa
    zmaga_domaci_verjetnost= skupne_ocene_domacih / (skupne_ocene_domacih + skupne_ocene_gostujocih)
    zmaga_gostujoci_verjetnost = 1 - zmaga_domaci_verjetnost

    zmaga_domaci_verjetnost = int(zmaga_domaci_verjetnost * 100)
    zmaga_gostujoci_verjetnost = int(zmaga_gostujoci_verjetnost * 100)

    rezultati_zmaga_domaci = ["1 : 0", "2 : 0", "3 : 0", "2 : 1", "3 : 1", "3 : 2"] * zmaga_domaci_verjetnost
    rezultati_zmaga_gostujoci = ["0 : 1", "0 : 2", "0 : 3", "1 : 2", "1 : 3", "2 : 3"] * zmaga_gostujoci_verjetnost
    rezultat_izenacen_verjetno = ["0 : 0", "1 : 1"] * 40
    rezultat_izenacen_manj_verjetno = ["2 : 2", "3 : 3"] * 10

    smiselni_rezultati = rezultati_zmaga_domaci + rezultati_zmaga_gostujoci + rezultat_izenacen_verjetno + rezultat_izenacen_manj_verjetno

    #smiselni_rezultati = ["0 : 0", "0 : 1", "0 : 2", "0 : 3", "1 : 0", "1 : 1", "1 : 2", "1 : 3", "2 : 0", "2 : 1", "2 : 2", "2 : 3", "3 : 0", "3 : 1", "3 : 2", "3 : 3"]
    #smiselni_rezultati.extend(["0 : 0"] * 100)

    print(smiselni_rezultati)
    rezultat = random.choice(smiselni_rezultati)

    ni_vratarja_domaci = 0  # druga ekipa +
    if st_vratar_domaci == 0:
        ni_vratarja_domaci = 3
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

    domaci_goli = int(rezultat[0])
    gostujoci_goli = int(rezultat[-1])

    domaci_goli = domaci_goli + veliko_napadalcev_domaci + ni_vratarja_gostujoci + premalo_branilcev_gostujoci + premalo_vezistov_gostujoci
    gostujoci_goli = gostujoci_goli + veliko_napadalcev_domaci + ni_vratarja_gostujoci + premalo_branilcev_gostujoci + premalo_vezistov_gostujoci

    # ce zmaga na papirju slabsa ekipa, naredimo tako, da ne zmaga za prevec golov
    if domaci_goli > gostujoci_goli + 1 and rating_skupen_gostujoci > rating_skupen_domaci:
        gostujoci_goli += 1
    if domaci_goli < gostujoci_goli + 1 and rating_skupen_gostujoci < rating_skupen_domaci:
        domaci_goli += 1
    
    return f"{domaci_goli} : {gostujoci_goli}"




print(f_izracunaj_stohasticen_rezultat((155782,27316,30895,75489,167027,128456,41093,67334),(173955,39562)))