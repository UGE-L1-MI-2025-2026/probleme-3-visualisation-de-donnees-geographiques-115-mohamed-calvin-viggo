from fltk import *
from datetime import datetime, timedelta
from lecture_contour import charger_donnees_departements, longitude_vers_x, latitude_vers_y
from fichier import couleur, tmp_departement_date, données
from constantes import *

# --- fonction utilitaire pour formater la date ---
def formater_date_fr(dt_obj, format_type="full"):
    """convertit un objet datetime en format personnalisé """
    if format_type == "full":
        jour = str(dt_obj.day).zfill(2)
        mois = str(dt_obj.month).zfill(2)
        annee = str(dt_obj.year)
        return f"{jour}-{mois}-{annee}"
    elif format_type == "year":
        return str(dt_obj.year)
    return ""

#fonction pour extraire les dates
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

#fonction pour trouver l'index de la date la plus proche
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

#NOUVELLE FONCTION : BOUCLE DE SAISIE DE DATE AVEC VÉRIFICATION
def saisir_date_console(dates_disponibles):
    while True:
        print("\n--- Saisie de date ---")
        date_nouvelle_str_fr = input("Entrez la date (format JJ-MM-AAAA) : ")

        try:
            # Validation de l'entrée utilisateur (JJ-MM-AAAA)
            date_obj = datetime.strptime(date_nouvelle_str_fr, "%d-%m-%Y") 
            
            # Conversion au format des données (AAAA-MM-JJ)
            date_recherchee_iso = date_obj.strftime("%Y-%m-%d")
            
            if date_recherchee_iso in dates_disponibles:
                new_index = dates_disponibles.index(date_recherchee_iso)
                print(f"Date changée pour le {date_nouvelle_str_fr}.")
                return new_index # Renvoie l'index et sort de la boucle
            else:
                print(f"ERREUR : La date {date_nouvelle_str_fr} n'est pas disponible dans les données.")
                # La boucle continue
                
        except ValueError:
            print("ERREUR : Format de date non valide. Utilisez JJ-MM-AAAA (ex: 15-05-2025).")
            # La boucle continue

# fonction pour le dessin de la règle graduée
def dessiner_regle(index_date, dates_dispo, date_min_dt, date_max_dt):
    # position y de la règle
    y_regle = Hauteur - 60  
    marge_x = 100
    largeur_regle = Largeur - 2 * marge_x
    
    # dessin de la ligne principale
    ligne(marge_x, y_regle, Largeur - marge_x, y_regle, couleur='black', epaisseur=2)
    
    if not dates_dispo: return

    # calcul des jours totaux pour l'échelle
    total_jours = (date_max_dt - date_min_dt).days
    if total_jours == 0: total_jours = 1
    
    # calcul de la position du curseur
    date_actuelle_str = dates_dispo[index_date]
    try:
        date_actuelle_dt = datetime.strptime(date_actuelle_str, "%Y-%m-%d")
    except ValueError:
        return

    jours_passes = (date_actuelle_dt - date_min_dt).days
    
    position_x = marge_x + (jours_passes / total_jours) * largeur_regle
    
    # dessin du curseur (la date actuelle)
    cercle(position_x, y_regle, 5, remplissage='blue', couleur='blue')
    
    # affichage de la date sélectionnée (AU DESSUS de la barre)
    date_formattee = formater_date_fr(date_actuelle_dt, "full")
    texte(position_x, y_regle - 15, date_formattee, taille=10, ancrage="center", couleur='blue')
    
    # affichage des bornes (EN DESSOUS)
    texte(marge_x, y_regle + 15, formater_date_fr(date_min_dt, "year"), taille=10)
    texte(Largeur - marge_x, y_regle + 15, formater_date_fr(date_max_dt, "year"), taille=10, ancrage="ne")

# fonction principale
def main():
    cree_fenetre(Largeur, Hauteur)
    
    print("chargement de la carte...")
    try:
        departements = charger_donnees_departements("departements-20180101")
    except Exception as e:
        print(f"erreur chargement carte : {e}")
        return

    dates = get_dates(données)
    
    if len(dates) == 0:
        print("Aucune date trouvée")
        ferme_fenetre()
        return

    # preparation des dates pour la regle
    try:
        date_min_dt = datetime.strptime(dates[0], "%Y-%m-%d")
        date_max_dt = datetime.strptime(dates[-1], "%Y-%m-%d")
    except ValueError:
        print("Erreur format dates données")
        return

    index_date = 0 
    encours = True 
    refresh = True 
    temp_type = 'tmoy' 

    print("\n--- Mode interactif activé ---")
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
                
                # Saisie de date par console (TOUCHE S maintenant, car D est pris)
                if touche_actuelle in ['d', 'D']:
                    
                    nouvel_index = saisir_date_console(dates)
                    
                    if nouvel_index is not None:
                        index_date = nouvel_index
                        refresh = True
                        
                # Nnavigation Jour (Flèches) - 1 jour
                elif touche_actuelle == 'Right':
                    if index_date < len(dates) - 1: index_date += 1; refresh = True
                elif touche_actuelle == 'Left':
                    if index_date > 0: index_date -= 1; refresh = True

                # navigation Mois (T/Y) - approx 30 jours
                elif touche_actuelle in ['t', 'T']: # Avancer mois
                    current_dt = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    target_dt = current_dt - timedelta(days=30)
                    index_date = trouver_index_proche(target_dt, dates)
                    refresh = True
                elif touche_actuelle in ['y', 'Y']: # Reculer mois
                    current_dt = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    target_dt = current_dt + timedelta(days=30)
                    index_date = trouver_index_proche(target_dt, dates)
                    refresh = True

                # navigation Année (G/H) - approx 365 jours
                elif touche_actuelle in ['g', 'G']: # Avancer année
                    current_dt = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    target_dt = current_dt - timedelta(days=365)
                    index_date = trouver_index_proche(target_dt, dates)
                    refresh = True
                elif touche_actuelle in ['h', 'H']: # Reculer année
                    current_dt = datetime.strptime(dates[index_date], "%Y-%m-%d")
                    target_dt = current_dt + timedelta(days=365)
                    index_date = trouver_index_proche(target_dt, dates)
                    refresh = True

        if refresh:
            efface_tout()
            date_actuelle = dates[index_date]
            
            # AFFICHAGE INFO
            texte(10, 10, f"Mois: T/Y | Année: G/H", taille=12, couleur='black')
            texte(10, 30, "Touche 'D' pour saisir une date", taille=10, couleur='black')
            
            #CARTE ET COULEURS
            for d in departements:
                nom = d['nom']
                
                try:
                    temp = tmp_departement_date(nom, temp_type, date_actuelle, données)
                    c = couleur(temp)
                except Exception:
                    c = "grey" 
                
                for poly in d["polygones"]:
                    pts_ecran = []
                    for pt in poly:
                        lon, lat = pt
                        x = longitude_vers_x(lon, Min_lon, Max_lon, Largeur)
                        y = latitude_vers_y(lat, Min_lat, Max_lat, Hauteur)
                        pts_ecran.append((x, y))
                    
                    polygone(pts_ecran, couleur='black', remplissage=c, epaisseur=1)

            dessiner_regle(index_date, dates, date_min_dt, date_max_dt)
            
            legende()

            mise_a_jour()
            refresh = False

    ferme_fenetre()

if __name__ == "__main__":
    main()