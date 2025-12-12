from fltk import *
import shapefile


# TÂCHE 1 : CHARGEMENT

def charger_donnees_departements(chemin_fichier):
    print(f"Chargement de {chemin_fichier}...")
    sf = shapefile.Reader(chemin_fichier)
    shapes_records = sf.shapeRecords()
    liste_departements = []

    for item in shapes_records:
        code_dep = item.record[0]
        nom_dep = item.record[1]
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
            "code": code_dep, "nom": nom_dep,
            "polygones": polygones
        }
        liste_departements.append(departement)
        
    return liste_departements


# TÂCHE 3 : PROJECTIONS

def longitude_vers_x(lon, min_lon, max_lon, largeur_ecran):
    return (lon - min_lon) * largeur_ecran / (max_lon - min_lon)

def latitude_vers_y(lat, min_lat, max_lat, hauteur_ecran):
    return hauteur_ecran - ((lat - min_lat) * hauteur_ecran / (max_lat - min_lat))

def pixel_vers_geo(x, y, min_lon, max_lon, min_lat, max_lat, larg, haut):
    lon = min_lon + (x / larg) * (max_lon - min_lon)
    lat = min_lat + ((haut - y) / haut) * (max_lat - min_lat)
    return lon, lat

# TÂCHE 2 : VERSION CORRIGÉE ET SÉCURISÉE

def dessiner_carte_avec_villes(donnees_deps, donnees_villes):
    # Paramètres de la fenêtre
    Largeur = 800
    Hauteur = 800

    cree_fenetre(Largeur, Hauteur)
    
    # Cadrage approximatif de la France 
    MIN_LON, MAX_LON = -5.5, 10.0
    MIN_LAT, MAX_LAT = 41.0, 51.5
    
    # 1. DESSIN DES CONTOURS 
    for dep in donnees_deps:
        for poly in dep["polygones"]:
            poly_ecran = [] 
            
            for point in poly:
                lon, lat = point
                x = longitude_vers_x(lon, MIN_LON, MAX_LON, Largeur)
                y = latitude_vers_y(lat, MIN_LAT, MAX_LAT, Hauteur)
                poly_ecran.append((x, y))
            
            polygone(poly_ecran, couleur='black', remplissage='')

    # 2. DESSIN DES VILLES 
    for ville in donnees_villes:
        
        # Conversion WGS84 => Pixels 
        x_ville = longitude_vers_x(ville["lon"], MIN_LON, MAX_LON, Largeur)
        y_ville = latitude_vers_y(ville["lat"], MIN_LAT, MAX_LAT, Hauteur)
        
        rayon = ville["taille"] # Taille du point (plus la ville est grande, plus le rayon est grand)
        
        # Dessin du point (cercle) et de l'étiquette
        cercle(x_ville, y_ville, rayon, couleur='red', remplissage='red')
        texte(x_ville + rayon + 2, y_ville - rayon, ville["nom"], couleur='blue')
        
    
    attend_ev()
    ferme_fenetre()

    ferme_fenetre()
if __name__ == "__main__":
    
    # 
    # Liste des 10 plus grandes villes métropolitaines 
    VILLES_FRANCE_TOP10 = [
    {"nom": "Paris", "lon": 2.35, "lat": 48.86, "taille": 8, "couleur": 'red'},     # 1
    {"nom": "Lyon", "lon": 4.85, "lat": 45.76, "taille": 6, "couleur": 'red'},      # 2
    {"nom": "Marseille", "lon": 5.37, "lat": 43.30, "taille": 6, "couleur": 'red'}, # 3
    {"nom": "Toulouse", "lon": 1.44, "lat": 43.60, "taille": 5, "couleur": 'red'},   # 4
    {"nom": "Bordeaux", "lon": -0.58, "lat": 44.84, "taille": 5, "couleur": 'red'}, # 5
    {"nom": "Lille", "lon": 3.06, "lat": 50.63, "taille": 4, "couleur": 'blue'},     # 6
    {"nom": "Nice", "lon": 7.27, "lat": 43.71, "taille": 4, "couleur": 'red'},      # 7
    {"nom": "Nantes", "lon": -1.55, "lat": 47.22, "taille": 4, "couleur": 'blue'},   # 8
    {"nom": "Strasbourg", "lon": 7.75, "lat": 48.58, "taille": 3, "couleur": 'blue'},# 9
    {"nom": "Rennes", "lon": -1.68, "lat": 48.11, "taille": 3, "couleur": 'blue'},   # 10
]
    
mes_deps = charger_donnees_departements("departements-20180101")
dessiner_carte_avec_villes(mes_deps, VILLES_FRANCE_TOP10)