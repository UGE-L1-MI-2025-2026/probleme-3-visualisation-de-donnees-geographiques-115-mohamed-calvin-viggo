import json

with open("tmp.json", "r", encoding="utf-8") as f:
    données = json.load(f)

def temp_moy_departement(données):
    dico={}
    for i in range(len(données)):
        dico[données[i]["departement"]]=données[i]["tmoy"]

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
        
def couleur(tmp):
    if 0<tmp<5:
        return "#2b83ba" 
    if 5<tmp<10:
        return "#4fb1a8"
    if 10<tmp<15:
        return "#7fd36e" 
    if 15<tmp<20:
        return "#d6e85a" 
    if 20<tmp<25:
        return "#ffd166" 
    if 25<tmp<30:
        return "#ff8a4c"
    if 30<tmp<35:
        return "#ff5a2b" 
    if 35<tmp :
        return "#b2182b" 
    return "#080808"
