import json

with open("sortie.json", "r", encoding="utf-8") as f:
    données = json.load(f)

 
""""
with open("sortie", "w", encoding="utf-8") as f:
    json.dump(données, f, sort_keys=True, indent=4)
"""



def temp_moy_departement(données):
    dico={}
    for i in range(len(données)):
        dico[données[i]["departement"]]=données[i]["tmoy"]
    return dico 

#print(temp_moy_departement(données))

def tmp_departement(dpt,tmp,données):
    for i in range(len(données)):
        if données[i]["departement"] == dpt:
            return données[i][str(tmp)]

#tmp_departement("Charente","tmoy",données)

def tmp_departement_date(dpt,tmp,date,données):
    for i in range(len(données)):
        if données[i]["departement"] == dpt:
            if données[i]["date_obs"]==date:
                return données[i][str(tmp)]

#tmp_departement_date("Charente","tmoy","2025-05-12",données)

def tmp_date(tmp,date,données):
    for i in range(len(données)):
        if données[i]["date_obs"] == date:
            return données[i][str(tmp)]

#tmp_date("tmax","2025-05-12",données)

def dico_couleur(date,données):
    dico={}
    dico1={}
    for i in range(len(données)):
        if données[i]["date_obs"] == date:
            dico[données[i]["departement"]]=dico1
            

    print (dico)


dico_couleur("2025-05-12",données)
print(len(données))
#dico de dico avec le departemnt: la date la temperature et couleur hexa en focntion de la tmp moy