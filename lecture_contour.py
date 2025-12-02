from shapefile_utils import *
from fltk import*

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

# TÂCHE 2 : DESSIN 
def dessiner_carte(donnees):
    # Paramètres de la fenêtre
    Largeur = 800
    Hauteur = 800

    cree_fenetre(Largeur, Hauteur)
    
    # Cadrage approximatif de la France , en gros ont la borne
    MIN_LON, MAX_LON = -5.5, 10.0
    MIN_LAT, MAX_LAT = 41.0, 51.5
    
    # Boucle pour dessiner chaque département
    for dep in donnees:
        # Un département peut avoir plusieurs morceaux (îles)
        for poly in dep["polygones"]:
            poly_ecran = [] # Liste pour les points convertis en pixels
            
            for point in poly:
                lon, lat = point
                
                # Conversion WGS84 => Pixels
                x = longitude_vers_x(lon, MIN_LON, MAX_LON, Largeur)
                y = latitude_vers_y(lat, MIN_LAT, MAX_LAT, Hauteur)
                
                poly_ecran.append((x, y))
            
            polygone(poly_ecran, couleur='black', remplissage='')

    attend_ev()
    attend_fermeture()

if __name__ == "__main__":
    mes_deps = charger_donnees_departements("departements-20180101")

    dessiner_carte(mes_deps)