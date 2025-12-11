from fltk import *
from datetime import datetime, timedelta
from lecture_contour import charger_donnees_departements, longitude_vers_x, latitude_vers_y
from fichier import couleur, tmp_departement_date, données
from constantes import *

def formater_date_fr(dt_obj, format_type="full"):
    if format_type == "full":
        jour = str(dt_obj.day).zfill(2)
        mois = str(dt_obj.month).zfill(2)
        annee = str(dt_obj.year)
        return f"{jour}-{mois}-{annee}"
    elif format_type == "year":
        return str(dt_obj.year)
    return ""

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

def saisir_date_console(dates_disponibles):
    while True:
        print("\n--- Saisie de date ---")
        date_nouvelle_str_fr = input("Entrez la date (format JJ-MM-AAAA) : ")
        try:
            date_obj = datetime.strptime(date_nouvelle_str_fr, "%d-%m-%Y") 
            date_recherchee_iso = date_obj.strftime("%Y-%m-%d")
            if date_recherchee_iso in dates_disponibles:
                new_index = dates_disponibles.index(date_recherchee_iso)
                print(f"Date changée pour le {date_nouvelle_str_fr}.")
                return new_index
            else:
                print(f"ERREUR : La date {date_nouvelle_str_fr} n'est pas disponible dans les données.")
        except ValueError:
            print("ERREUR : Format de date non valide. Utilisez JJ-MM-AAAA (ex: 15-05-2025).")

def legende():
    """Dessine la légende en se basant sur la taille TOTALE de la fenêtre"""
    couleurs_legende = ["#2b83ba", "#4fb1a8", "#7fd36e", "#d6e85a",
                        "#ffd166", "#ff8a4c", "#ff5a2b", "#b2182b"]
    temps_legende = ["0-5°C", "5-10°C", "10-15°C", "15-20°C", "20-25°C", "25-30°C", "30-35°C", "+35°C"]
    
    largeur_barre = 30
    hauteur_totale = 500
    marge_droite = 20
    
    # On se cale sur le bord droit de la GRANDE fenêtre
    x2 = LARGEUR_FENETRE - marge_droite
    x1 = x2 - largeur_barre
    
    y_centre = HAUTEUR_FENETRE / 2
    y1 = y_centre - (hauteur_totale / 2)
    y2 = y_centre + (hauteur_totale / 2)
    
    rectangle(x1 - 60, y1 - 25, x2 + 10, y2 + 10, remplissage="white", couleur="black", epaisseur=1)
    texte(x1 - 15, y1 - 20, "Temp (°C)", taille=10, ancrage="w")

    n = len(couleurs_legende)
    hauteur_case = hauteur_totale / n
    for i, col in enumerate(couleurs_legende):
        y_haut = y1 + i * hauteur_case
        y_bas = y_haut + hauteur_case
        rectangle(x1, y_haut, x2, y_bas, remplissage=col, couleur=col, epaisseur=0)
        texte(x1 - 5, y_haut + hauteur_case/2, temps_legende[i], taille=9, ancrage="e")

def dessiner_regle(index_date, dates_dispo, date_min_dt, date_max_dt):
    # La règle est en bas de la fenêtre
    y_regle = HAUTEUR_FENETRE - 60  
    marge_x = 100
    largeur_regle = LARGEUR_FENETRE - 2 * marge_x
    
    ligne(marge_x, y_regle, LARGEUR_FENETRE - marge_x, y_regle, couleur='black', epaisseur=2)
    
    if not dates_dispo: return
    total_jours = (date_max_dt - date_min_dt).days
    if total_jours == 0: total_jours = 1
    
    date_actuelle_str = dates_dispo[index_date]
    try:
        date_actuelle_dt = datetime.strptime(date_actuelle_str, "%Y-%m-%d")
    except ValueError:
        return

    jours_passes = (date_actuelle_dt - date_min_dt).days
    position_x = marge_x + (jours_passes / total_jours) * largeur_regle
    
    cercle(position_x, y_regle, 5, remplissage='blue', couleur='blue')
    date_formattee = formater_date_fr(date_actuelle_dt, "full")
    texte(position_x, y_regle - 15, date_formattee, taille=10, ancrage="center", couleur='blue')
    
    texte(marge_x, y_regle + 15, formater_date_fr(date_min_dt, "year"), taille=10)
    texte(LARGEUR_FENETRE - marge_x, y_regle + 15, formater_date_fr(date_max_dt, "year"), taille=10, ancrage="ne")

def main():
    # 1. On crée la fenêtre avec la taille TOTALE (incluant la marge pour la légende)
    cree_fenetre(LARGEUR_FENETRE, HAUTEUR_FENETRE)
    
    print("chargement de la carte...")
    try:
        departements = charger_donnees_departements("departements-20180101")
    except Exception as e:
        print(f"erreur chargement carte : {e}")
        return

    # OPTIMISATION ET CADRAGE
    for d in departements:
        d["polygones_ecran"] = []
        for poly in d["polygones"]:
            pts_ecran = []
            for pt in poly:
                lon, lat = pt
                
                # A. Calcul des coordonnées locales (sur la carte seule)
                x_local = longitude_vers_x(lon, Min_lon, Max_lon, Largeur)
                y_local = latitude_vers_y(lat, Min_lat, Max_lat, Hauteur)
                
                # B. Ajout du décalage pour placer la carte dans la grande fenêtre
                x_final = x_local + X_DEBUT
                y_final = y_local + Y_DEBUT
                
                pts_ecran.append((x_final, y_final))
                
            d["polygones_ecran"].append(pts_ecran)

    dates = get_dates(données)
    if not dates:
        ferme_fenetre()
        return

    try:
        date_min_dt = datetime.strptime(dates[0], "%Y-%m-%d")
        date_max_dt = datetime.strptime(dates[-1], "%Y-%m-%d")
    except ValueError:
        return

    index_date = 0 
    encours = True 
    refresh = True 
    temp_type = 'tmoy' 

    print("\n--- Commandes ---")
    print("Flèches: jour suivant/précédent")
    print("Touche 'D': Saisie de date par la console.")
    print("Touches 'T'/'Y': Mois +/-")
    print("Touches 'G'/'H': Année +/-")

    while encours:
        ev = attend_ev()
        
        if ev is not None:
            t = type_ev(ev)
            if t == 'Quitte':
                encours = False
            elif t == 'Touche':
                touche_actuelle = touche(ev)
                
                if touche_actuelle in ['d', 'D']:
                    nouvel_index = saisir_date_console(dates)
                    if nouvel_index is not None:
                        index_date = nouvel_index
                        refresh = True
                
                elif touche_actuelle == 'Right':
                    if index_date < len(dates) - 1: index_date += 1; refresh = True
                elif touche_actuelle == 'Left':
                    if index_date > 0: index_date -= 1; refresh = True
                
                elif touche_actuelle in ['y', 'Y']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur + timedelta(days=30), dates)
                    refresh = True
                elif touche_actuelle in ['t', 'T']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur - timedelta(days=30), dates)
                    refresh = True
                
                elif touche_actuelle in ['h', 'H']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur + timedelta(days=365), dates)
                    refresh = True
                elif touche_actuelle in ['g', 'G']:
                    cur = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    index_date = trouver_index_proche(cur - timedelta(days=365), dates)
                    refresh = True

        if refresh:
            efface_tout()
            date_actuelle = dates[index_date]
            
            texte(10, 10, f"Mois: T/Y | Année: G/H", taille=12, couleur='black')
            texte(10, 30, "Touche 'D' pour saisir une date", taille=10, couleur='black')
            
            for d in departements:
                try:
                    temp = tmp_departement_date(d['nom'], temp_type, date_actuelle, données)
                    c = couleur(temp)
                except: c = "grey"
                
                for pts_ecran in d["polygones_ecran"]:
                    polygone(pts_ecran, couleur='black', remplissage=c, epaisseur=1)

            dessiner_regle(index_date, dates, date_min_dt, date_max_dt)
            legende() # Maintenant elle aura sa place à droite
            
            mise_a_jour()
            refresh = False

    ferme_fenetre()

if __name__ == "__main__":
    main()