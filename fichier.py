import json

with open("tmp.json", "r", encoding="utf-8") as f:
    données = json.load(f)


def tmp_departement_date(dpt,tmp,date,données):
    for i in range(len(données)):
        if données[i]["departement"] == dpt:
            if données[i]["date_obs"]==date:
                return données[i][str(tmp)]


def couleur(tmp):
    if 0<tmp<5:
        return "#273CF5" 
    if 5<tmp<10:
        return "#FFB299"
    if 10<tmp<15:
        return "#FFA285" 
    if 15<tmp<20:
        return "#FF9272" 
    if 20<tmp<25:
        return "#FF825F" 
    if 25<tmp<30:
        return "#F57927"
    if 30<tmp<35:
        return "#F55427" 
    if 35<tmp :
        return "#DE1F14" 
