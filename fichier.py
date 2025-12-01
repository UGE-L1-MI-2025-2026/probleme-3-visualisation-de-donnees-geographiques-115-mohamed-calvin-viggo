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

#tmp_date("tmax","2025-05-12",données)

def cree_dico(donées):
    dictionnaire={}
    for dico in donées:
        tmp={"date":dico["date_obs"]}
        if dico["tmoy"]!=None:
            tmp["couleur"]=couleur(dico["tmoy"])
            dictionnaire[dico["departement"]]=tmp
        else:
            tmp["couleur"]=None
            dictionnaire[dico["departement"]]=tmp       
    return dictionnaire


def couleur(tmp):
    if 0<tmp<5:
        return "#FFC2AD" 
    if 5<tmp<10:
        return "#FFB299"
    if 10<tmp<15:
        return "#FFA285" 
    if 15<tmp<20:
        return "#FF9272" 
    if 20<tmp<25:
        return "#FF825F" 
    if 25<tmp<30:
        return "#FD704D"
    if 30<tmp<35:
        return "#FA5E3A" 
    if 30<tmp :
        return "#F54927" 

print (cree_dico(données))

