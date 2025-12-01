import json

with open("sortie.json", "r", encoding="utf-8") as f:
    données = json.load(f)


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



def couleur(tmp):
    if 0<tmp<5:
        return "#FFB299" 
    if 5<tmp<10:
        return "#FFA285"
    if 10<tmp<15:
        return "#FF9272" 
    if 15<tmp<20:
        return "#FF825F" 
    if 20<tmp<25:
        return "#FD704D" 
    if 30<tmp<35:
        return "#FA5E3A" 
    if 30<tmp :
        return "#F54927" 


