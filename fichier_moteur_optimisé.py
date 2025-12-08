from fltk import *
import json
import sys
from datetime import datetime, timedelta
from lecture_contour import charger_donnees_departements, longitude_vers_x, latitude_vers_y
from fichier import couleur, tmp_departement_date, données
from constantes import *

# --- fonction utilitaire pour formater la date ---
def formater_date_fr(dt_obj, format_type="full"):
    if format_type == "full":
        jour = str(dt_obj.day).zfill(2)
        mois = str(dt_obj.month).zfill(2)
        annee = str(dt_obj.year)
        return f"{jour}-{mois}-{annee}"
    elif format_type == "year":
        return str(dt_obj.year)
    return ""

# --- fonction pour extraire les dates ---
def get_dates(data):
    dates_set = set()
    if isinstance(data, dict):
        elements = data.values()
    elif isinstance(data, list):
        elements = data
    else:
        return []

    for e in elements:
        if isinstance(e, dict) and ("date_obs" in e or "date" in e):
             date_key = "date_obs" if "date_obs" in e else "date"
             dates_set.add(e[date_key])
    return sorted(list(dates_set))

# --- fonction pour trouver l'index proche ---
def trouver_index_proche(target_dt, dates_str_list):
    best_idx = 0
    min_diff = None
    for i, d_str in enumerate(dates_str_list):
        try:
            d_dt = datetime.strptime(d_str, "%Y-%m-%d")
            diff = abs((target_dt - d_dt).days)
            if min_diff is None or diff < min_diff:
                min_diff = diff
                best_idx = i
        except ValueError:
            continue
    return best_idx

# --- FONCTION SAISIE CONSOLE ---
def saisir_date_console(dates_disponibles):
    while True:
        print("\n--- Saisie de date ---")
        date_entree = input("Entrez la date (JJ-MM-AAAA) ou 'Q' pour annuler : ")
        if date_entree.upper() == 'Q': return None

        try:
            date_obj = datetime.strptime(date_entree, "%d-%m-%Y")
            date_iso = date_obj.strftime("%Y-%m-%d")
            
            if date_iso in dates_disponibles:
                print(f"Date changée : {date_entree}")
                return dates_disponibles.index(date_iso)
            else:
                print(f"Erreur : La date {date_entree} n'est pas dans les données.")
        except ValueError:
            print("Erreur format. Utilisez JJ-MM-AAAA.")

# --- RÈGLE GRADUÉE ---
def dessiner_regle(index_date, dates_dispo, date_min_dt, date_max_dt):
    y_regle = Hauteur - 60  
    marge_x = 100
    largeur_regle = Largeur - 2 * marge_x
    
    ligne(marge_x, y_regle, Largeur - marge_x, y_regle, couleur='black', epaisseur=2)
    
    if not dates_dispo: return

    total_jours = (date_max_dt - date_min_dt).days
    if total_jours == 0: total_jours = 1
    
    # Curseur
    date_actuelle_str = dates_dispo[index_date]
    try:
        date_actuelle_dt = datetime.strptime(date_actuelle_str, "%Y-%m-%d")
    except ValueError: return

    jours_passes = (date_actuelle_dt - date_min_dt).days
    position_x = marge_x + (jours_passes / total_jours) * largeur_regle
    
    cercle(position_x, y_regle, 5, remplissage='blue', couleur='blue')
    
    # Textes
    date_txt = formater_date_fr(date_actuelle_dt, "full")
    texte(position_x, y_regle - 15, date_txt, taille=10, ancrage="center", couleur='blue')
    texte(marge_x, y_regle + 15, formater_date_fr(date_min_dt, "year"), taille=10)
    texte(Largeur - marge_x, y_regle + 15, formater_date_fr(date_max_dt, "year"), taille=10, ancrage="ne")

# --- MAIN OPTIMISÉ ---
def main():
    cree_fenetre(Largeur, Hauteur)
    
    print("chargement de la carte...")
    try:
        departements = charger_donnees_departements("departements-20180101")
    except Exception as e:
        print(f"erreur chargement : {e}")
        return

    # --- OPTIMISATION VITESSE ---
    # On calcule les coordonnées d'écran UNE SEULE FOIS ici
    print("optimisation des traces en cours...")
    for d in departements:
        d["polygones_ecran"] = [] # On stocke les points convertis ici
        for poly in d["polygones"]:
            pts_ecran = []
            for pt in poly:
                lon, lat = pt
                x = longitude_vers_x(lon, Min_lon, Max_lon, Largeur)
                y = latitude_vers_y(lat, Min_lat, Max_lat, Hauteur)
                pts_ecran.append((x, y))
            d["polygones_ecran"].append(pts_ecran)
    # ----------------------------

    dates = get_dates(données)
    if len(dates) == 0: return

    try:
        date_min_dt = datetime.strptime(dates[0], "%Y-%m-%d")
        date_max_dt = datetime.strptime(dates[-1], "%Y-%m-%d")
    except ValueError: return

    index_date = 0 
    encours = True 
    refresh = True 
    temp_type = 'tmoy' 

    print("\n--- Commandes ---")
    print("Flèches G/D : Jour +/-")
    print("A / D : Mois +/-")
    print("G / F : Année +/-")
    print("S : Saisir une date")

    while encours:
        # On utilise attend_ev() pour éviter le crash
        ev = attend_ev() 
        
        if ev is not None:
            t = type_ev(ev)
            
            if t == 'Quitte':
                encours = False
            
            elif t == 'Touche':
                k = touche(ev)
                
                # Saisie
                if k in ['s', 'S']:
                    new_idx = saisir_date_console(dates)
                    if new_idx is not None:
                        index_date = new_idx
                        refresh = True
                
                # Jours
                elif k == 'Right':
                    if index_date < len(dates) - 1: index_date += 1; refresh = True
                elif k == 'Left':
                    if index_date > 0: index_date -= 1; refresh = True
                
                # Mois (approx 30j)
                elif k in ['d', 'D']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur + timedelta(days=30), dates)
                    refresh = True
                elif k in ['a', 'A', 'q', 'Q']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur - timedelta(days=30), dates)
                    refresh = True
                
                # Années
                elif k in ['f', 'F']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur + timedelta(days=365), dates)
                    refresh = True
                elif k in ['g', 'G']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur - timedelta(days=365), dates)
                    refresh = True

        if refresh:
            efface_tout()
            date_actuelle = dates[index_date]
            
            texte(10, 10, "Mois: A/D | Année: G/F", taille=12)
            texte(10, 30, "Touche 'S' pour saisir", taille=10)
            
            # --- DESSIN OPTIMISÉ ---
            for d in departements:
                try:
                    # On ne calcule que la couleur (rapide)
                    temp = tmp_departement_date(d['nom'], temp_type, date_actuelle, données)
                    c = couleur(temp)
                except: c = "grey"
                
                # On utilise les points DÉJÀ calculés (très rapide)
                for pts_ecran in d["polygones_ecran"]:
                    polygone(pts_ecran, couleur='black', remplissage=c, epaisseur=1)

            dessiner_regle(index_date, dates, date_min_dt, date_max_dt)
            mise_a_jour()
            refresh = False

    ferme_fenetre()

if __name__ == "__main__":
    main()