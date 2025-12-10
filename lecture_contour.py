from shapefile import *
from fltk import *
from constantes import *


def legende():
    couleur=["#2b83ba", "#4fb1a8", "#7fd36e", "#d6e85a",
            "#ffd166", "#ff8a4c", "#ff5a2b", "#b2182b"]
    tmp=["0-5°C", "5-10°C", "10-15°C", "15-20°C", "20-25°C", "25-30°C", "30-35°C", "+35°C"]
    x2=LARGEUR_FENETRE - 8
    x1=x2-44
    y1=0
    y2=HAUTEUR_FENETRE
    n=len(couleur)
    hauteur=(y2 - y1) / n
    rectangle(x1 - 4, y1, x2 + 4, y2, remplissage="#f7f7f7", couleur="#666666", epaisseur=1)
    for i, couleurs in enumerate(couleur):
        y0 = y1 + i * hauteur
        ya = y0 + hauteur
        rectangle(x1, y0, x2, ya, remplissage=couleurs, couleur=couleurs, epaisseur=0)
    for i, tmps in enumerate(tmp):
        y = y1 + i * hauteur + hauteur / 2
        texte(x1 - 8, y, chaine=tmps, taille=12, ancrage="e")
    texte(723, 8, chaine="Temp (°C)", taille=12, ancrage="w")  



# TÂCHE 1 : CHARGEMENT DES DONNÉES 
def charger_donnees_departements(chemin_fichier):
    print(f"Chargement de {chemin_fichier}...")
    sf = Reader(chemin_fichier)
    shapes_records = sf.shapeRecords()
    liste_departements = []

    for item in shapes_records:
        # Récupération des infos
        code_dep = item.record[0]
        nom_dep = item.record[1]
        
        # Gestion des îles (découpage des polygones)
        points_bruts = item.shape.points
        parts = item.shape.parts 
        
        polygones = [] 
        if len(parts) <= 1:
            polygones.append(points_bruts)
        else:
            for i in range(len(parts)):
                debut = parts[i]
                if i < len(parts) - 1:
                    fin = parts[i+1]
                    polygones.append(points_bruts[debut:fin])
                else:
                    polygones.append(points_bruts[debut:])
        
        departement = {
            "code": code_dep, 
            "nom": nom_dep,
            "polygones": polygones
        }
        liste_departements.append(departement)
        
    return liste_departements

# TÂCHE 3 : PROJECTION (CONVERSION GÉO -> ÉCRAN)
def longitude_vers_x(lon, min_lon, max_lon, largeur_ecran):
    """Transforme une longitude en position X sur l'écran"""
    return (lon - min_lon) * largeur_ecran / (max_lon - min_lon)

def latitude_vers_y(lat, min_lat, max_lat, hauteur_ecran):
    """Transforme une latitude en position Y sur l'écran"""
    return hauteur_ecran - ((lat - min_lat) * hauteur_ecran / (max_lat - min_lat))

# TÂCHE 2 : DESSIN AVEC FLTK
def dessiner_carte(donnees):
    
    
    cree_fenetre(LARGEUR_FENETRE, HAUTEUR_FENETRE)
    
    
    legende()
    # 3. Boucle principale de dessin
    for dep in donnees:
        for poly in dep["polygones"]:
            poly_ecran = [] 
            
            for point in poly:
                lon, lat = point
                
                # Conversion WGS84 -> Pixels pour l'espace CARTE
                x_local = longitude_vers_x(lon, Min_lon, Max_lon, Largeur)
                y_local = latitude_vers_y(lat, Min_lat, Max_lat, Hauteur)
                
                # Réajustement des pixels à l'intérieur de la FENÊTRE
                x_final = x_local + X_DEBUT
                y_final = y_local + Y_DEBUT
                
                poly_ecran.append((x_final, y_final))
            
            # Dessin : remplissage='' laisse la zone blanche à l'intérieur
            polygone(poly_ecran, couleur='black', remplissage='')

    # Gestion de la fenêtre
    attend_ev()
    ferme_fenetre()

if __name__ == "__main__":
    mes_deps = charger_donnees_departements("departements-20180101")

    dessiner_carte(mes_deps)
