from fltk import *
import netCDF4
import sys

# --- IMPORTATION DU TRAVAIL DE MOHAMED UNIQUEMENT ---
try:
    from lecture_contour import charger_donnees_departements, longitude_vers_x, latitude_vers_y
except ImportError as e:
    print("ERREUR : Il manque le fichier 'lecture_contour.py'.")
    print(e)
    sys.exit()

# --- FONCTION COULEUR (Adaptée de Viggo pour être plus robuste) ---
def get_couleur_viggo(tmp):
    # Gestion des cas manquants (températures négatives ou trous dans la logique originale)
    if tmp is None: return "grey"
    if tmp <= 0: return "#4A90E2"    # Bleu froid pour températures négatives
    if 0 < tmp < 5: return "#FFB299" 
    if 5 <= tmp < 10: return "#FFA285"
    if 10 <= tmp < 15: return "#FF9272" 
    if 15 <= tmp < 20: return "#FF825F" 
    if 20 <= tmp < 25: return "#FD704D"
    if 25 <= tmp < 30: return "#FC6644" # Ajout pour combler le trou
    if 30 <= tmp < 35: return "#FA5E3A" 
    if 35 <= tmp: return "#F54927"
    return "grey" # Sécurité

# --- CONSTANTES ---
MIN_LON, MAX_LON = -5.5, 10.0
MIN_LAT, MAX_LAT = 41.0, 51.5
LARGEUR_ECRAN, HAUTEUR_ECRAN = 800, 800

# --- PARTIE CALVIN : GESTIONNAIRE NETCDF ---
class MoteurDCENT:
    def __init__(self, chemin_fichier):
        try:
            self.ds = netCDF4.Dataset(chemin_fichier, 'r')
            print(f"Chargement NetCDF réussi : {chemin_fichier}")
            
            # Détection automatique de la variable de température
            # On cherche 'tas', 'tempanomaly' ou 'temperature'
            noms_possibles = ['tas', 'tempanomaly', 'temperature', 't2m']
            self.var_temp = None
            for nom in noms_possibles:
                if nom in self.ds.variables:
                    self.var_temp = nom
                    break
            
            # Si pas trouvé, on prend la première variable 3D (temps, lat, lon)
            if self.var_temp is None:
                for v in self.ds.variables:
                    if len(self.ds.variables[v].shape) == 3:
                        self.var_temp = v
                        break
            
            print(f"Variable utilisée : {self.var_temp}")

            self.temps = self.ds.variables['time']
            self.lats = self.ds.variables['lat'][:]
            self.lons = self.ds.variables['lon'][:]
            self.dates = netCDF4.num2date(self.temps[:], units=self.temps.units)
            self.nb_steps = len(self.dates)
            
        except Exception as e:
            print(f"Erreur chargement NetCDF : {e}")
            self.nb_steps = 0

    def get_date_str(self, index):
        if 0 <= index < self.nb_steps:
            return self.dates[index].strftime("%d/%m/%Y")
        return "Date Inconnue"

    def get_temp_at_coord(self, lat_cible, lon_cible, index_temps):
        if self.nb_steps == 0 or self.var_temp is None: return 0
        
        # Trouver l'index le plus proche dans la grille
        idx_lat = (abs(self.lats - lat_cible)).argmin()
        idx_lon = (abs(self.lons - lon_cible)).argmin()
        
        try:
            val = self.ds.variables[self.var_temp][index_temps, idx_lat, idx_lon]
            # Si c'est une valeur masquée (ex: océan), on renvoie None ou 0
            if hasattr(val, 'mask') and val.mask: return 0
            return val
        except:
            return 0

    def close(self):
        if hasattr(self, 'ds'):
            self.ds.close()

def calculer_centre_departement(departement):
    somme_lon, somme_lat, nb_points = 0, 0, 0
    for poly in departement["polygones"]:
        for (lon, lat) in poly:
            somme_lon += lon
            somme_lat += lat
            nb_points += 1
    if nb_points == 0: return (46.0, 2.0)
    return (somme_lat / nb_points, somme_lon / nb_points)

# --- BOUCLE PRINCIPALE ---
def main():
    cree_fenetre(LARGEUR_ECRAN, HAUTEUR_ECRAN)
    
    print("Chargement des contours...")
    try:
        departements = charger_donnees_departements("departements-20180101")
    except Exception as e:
        print(f"Erreur lors du chargement des départements : {e}")
        # Si ça plante, on crée une liste vide pour ne pas crasher tout de suite
        departements = []

    # Pré-calcul des centres
    for dep in departements:
        dep['centre'] = calculer_centre_departement(dep)

    print("Chargement du climat...")
    # Assure-toi que le fichier s'appelle bien dcent_data.nc
    moteur = MoteurDCENT("dcent_data.nc") 
    
    index_jour = 0
    en_cours = True
    
    # Premier affichage forcé
    mise_a_jour_necessaire = True

    while en_cours:
        ev = donne_ev()
        
        if ev is not None:
            if type_ev(ev) == 'Quitte':
                en_cours = False
            elif type_ev(ev) == 'Touche':
                touche_nom = touche(ev)
                if touche_nom == 'Right':
                    if index_jour < moteur.nb_steps - 1:
                        index_jour += 1
                        mise_a_jour_necessaire = True
                elif touche_nom == 'Left':
                    if index_jour > 0:
                        index_jour -= 1
                        mise_a_jour_necessaire = True

        if mise_a_jour_necessaire:
            efface_tout()
            
            # Affichage Date
            date_str = moteur.get_date_str(index_jour)
            texte(10, 10, f"Date : {date_str}", taille=20)
            
            # Dessin Carte
            for dep in departements:
                lat_c, lon_c = dep['centre']
                temp = moteur.get_temp_at_coord(lat_c, lon_c, index_jour)
                coul = get_couleur_viggo(temp)
                
                for poly in dep["polygones"]:
                    poly_ecran = []
                    for point in poly:
                        lon, lat = point
                        x = longitude_vers_x(lon, MIN_LON, MAX_LON, LARGEUR_ECRAN)
                        y = latitude_vers_y(lat, MIN_LAT, MAX_LAT, HAUTEUR_ECRAN)
                        poly_ecran.append((x, y))
                    
                    polygone(poly_ecran, couleur='black', remplissage=coul, epaisseur=1)
            
            mise_a_jour()
            mise_a_jour_necessaire = False # On attend le prochain événement

    moteur.close()
    ferme_fenetre()

if __name__ == "__main__":
    main()