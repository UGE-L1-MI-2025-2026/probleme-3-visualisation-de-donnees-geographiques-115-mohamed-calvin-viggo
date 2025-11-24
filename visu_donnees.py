import shapefile
sf = shapefile.Reader("departements-20180101") #ouverture du fichier shapefile
sf.records() # visualisation de toutes les entrées du fichier
[..., Record 47: ['77', 'Seine-et-Marne', 'FR102', 'fr:Seine-et-Marne', 5927.0], ...]
seine_et_marne = sf.shape(47) # Récupération de l'entrée correspondant à la Seine-et-Marne
seine_et_marne.bbox # Les points extrémaux de la seine-et-marne
[2.3923284961351237, 48.12014561527111, 
3.559220826259302, 49.11789167125887]
seine_et_marne.points # La liste des points du contour de la Seine-et-Marne
[(2.3923284961351237, 48.335929161584076), 
 (2.393003669902668, 48.336290983108846), 
 (2.3940130169559044, 48.3356802622364), ...]