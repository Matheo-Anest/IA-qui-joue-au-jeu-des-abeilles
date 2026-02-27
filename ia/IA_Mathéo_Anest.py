import random
from typing import Literal
from ia import JeuDict, MoteurIA


class ANEST(MoteurIA):
    nom = "Mathéo ANEST"

    def __init__(
        self, joueur_id: str, ncases: int, max_tours: int, temps_ko: int
    ) -> None:
        self.joueur_id = joueur_id
        self.ncases = ncases
        self.max_tours = max_tours
        self.temps_ko = temps_ko
        self.a_deja_pondu = False
        self.fleurs_vides = []
        self.abeilles_data = {}
        self.bourdons_attribues = 0
        self.lst_id_ennemis = None

    def ponte(
        self, jeu: JeuDict, cout_ponte: int
    ) -> Literal["OUV", "BOU", "ECL", "RIEN"]:
        if len(jeu["autres_joueurs"]) == 1:
            if len(jeu["fleurs"]) >= 12:
                s_bou, s_ouv = 3, 4
            elif len(jeu["fleurs"]) == 8:
                s_bou, s_ouv = 2, 3
            else:
                s_bou, s_ouv = 1, 2
        elif len(jeu["autres_joueurs"]) == 2:
            if len(jeu["fleurs"]) >= 12:
                s_bou, s_ouv = 2, 3
            elif len(jeu["fleurs"]) == 8:
                s_bou, s_ouv = 2, 2
            else:
                s_bou, s_ouv = 0, 1
        else:
            if len(jeu["fleurs"]) >= 12:
                s_bou, s_ouv = 2, 3
            elif len(jeu["fleurs"]) == 8:
                s_bou, s_ouv = 2, 2
            else:
                s_bou, s_ouv = 0, 1
            
        compteur_bourdons = 0
        compteur_ouvrieres = 0
        for abeille in jeu["moi"]["abeilles"]:
            if abeille["position"] == jeu["moi"]["position"]:
                return "RIEN"
            if abeille["abeille_type"] == "BOU":
                compteur_bourdons += 1
            elif abeille["abeille_type"] == "OUV":
                compteur_ouvrieres += 1
                
        if len(jeu["moi"]["abeilles"]) % 2 == 0 and jeu["moi"]["nectar"] >= cout_ponte:
            if compteur_ouvrieres < s_ouv:
                return "OUV"
            elif compteur_bourdons < s_bou:
                return "BOU"
        elif len(jeu["moi"]["abeilles"]) % 2 == 1 and jeu["moi"]["nectar"] >= cout_ponte:
            if compteur_bourdons < s_bou:
                return "BOU"
            elif compteur_ouvrieres < s_ouv:
                return "OUV"
        return "RIEN"

    def action_abeilles(
        self, jeu: JeuDict
    ) -> list[tuple[str, int, int, Literal["DEPLACEMENT", "BUTINAGE"]]]:
        
        actions = []

        self.init_ennemis(jeu)
        cases_interdites = self.cases_interdites(jeu)
        fleurs_cibles = []
        for fleur in self.abeilles_data.values():
            if fleur["fleur_cible"] is not None:
                fleurs_cibles.append(fleur["fleur_cible"])

        for abeille in jeu["moi"]["abeilles"]:
            if abeille["ko_temps"] > 0:
                continue

            abeille_id = abeille["id"]
            if abeille_id not in self.abeilles_data:
                self.abeilles_data[abeille_id] = {
                    "fleur_cible": None, "nectar_abeille_precedent": 0,
                    "stock_nectar_precedent": 0, "action_precedente_butinage": False,
                    "id_joueur_cible": None, "mode_retour": False
                }
            data_abeille = self.abeilles_data[abeille_id]

            self.verifie_fleur_vide(abeille, data_abeille, jeu)

            if abeille["abeille_type"] == "BOU":
                cible = self.choix_bourdon(abeille, data_abeille, jeu)
            else:
                cible, doit_butiner = self.choix_ouvriere(abeille, data_abeille, jeu, fleurs_cibles)
                
                if doit_butiner:
                    data_abeille["nectar_abeille_precedent"] = abeille["nectar"]
                    data_abeille["stock_nectar_precedent"] = jeu["moi"]["nectar"]
                    data_abeille["action_precedente_butinage"] = True
                    actions.append((abeille["id"], cible["x"], cible["y"], "BUTINAGE"))
                    continue

            dx, dy = self.calcul_mouvement(abeille, cible, cases_interdites)

            data_abeille["nectar_abeille_precedent"] = abeille["nectar"]
            data_abeille["action_precedente_butinage"] = False

            if dx != 0 or dy != 0:
                actions.append((abeille["id"], abeille["position"]["x"] + dx, abeille["position"]["y"] + dy, "DEPLACEMENT"))
                cases_interdites.append((abeille["position"]["x"] + dx, abeille["position"]["y"] + dy))
                if (abeille["position"]["x"], abeille["position"]["y"]) in cases_interdites:
                    cases_interdites.remove((abeille["position"]["x"], abeille["position"]["y"]))

        return actions

    def init_ennemis(self, jeu):
        if self.lst_id_ennemis is None:
            self.lst_id_ennemis = []
            if len(jeu["autres_joueurs"]) == 3:
                for j in jeu["autres_joueurs"]:
                    if j["position"]["x"] == jeu["moi"]["position"]["x"] or j["position"]["y"] == jeu["moi"]["position"]["y"]:
                        self.lst_id_ennemis.append(j["id"])
            else:
                for j in jeu["autres_joueurs"]:
                    self.lst_id_ennemis.append(j["id"])
            self.lst_id_ennemis.sort()

    def cases_interdites(self, jeu):
        cases = []
        for a in jeu["moi"]["abeilles"]: cases.append((a["position"]["x"], a["position"]["y"]))
        for j in jeu["autres_joueurs"]:
            for a in j["abeilles"]: cases.append((a["position"]["x"], a["position"]["y"]))
        for i in range(-1, self.ncases + 1):
            cases.extend([(-1, i), (self.ncases, i), (i, -1), (i, self.ncases)])
        for j in jeu["autres_joueurs"]:
            for x in range(4):
                for y in range(4):
                    cases.append((abs(j["position"]["x"] - x), abs(j["position"]["y"] - y)))
        return cases

    def verifie_fleur_vide(self, abeille, data_abeille, jeu):
        if data_abeille["action_precedente_butinage"]:
            if abeille["nectar"] == data_abeille["nectar_abeille_precedent"] and \
               jeu["moi"]["nectar"] == data_abeille["stock_nectar_precedent"] and \
               abeille["nectar"] < abeille["max_nectar"]:
                
                coords = (data_abeille["fleur_cible"]["x"], data_abeille["fleur_cible"]["y"])
                if coords not in self.fleurs_vides:
                    self.fleurs_vides.append(coords)
                data_abeille["fleur_cible"] = None
                
                if abeille["nectar"] > 0:
                    data_abeille["mode_retour"] = True

    def choix_bourdon(self, abeille, data_abeille, jeu):
        if data_abeille["id_joueur_cible"] is None:
            if len(self.lst_id_ennemis) > 0:
                index = self.bourdons_attribues % len(self.lst_id_ennemis)
                data_abeille["id_joueur_cible"] = self.lst_id_ennemis[index]
                self.bourdons_attribues += 1

        joueur_vise = None
        for j in jeu["autres_joueurs"]:
            if j["id"] == data_abeille["id_joueur_cible"]:
                joueur_vise = j
                break
        
        cible_pos = None
        
        if joueur_vise:
            dist_min = 9999
            for ennemi in joueur_vise["abeilles"]:
                if ennemi["abeille_type"] == "OUV" and ennemi["ko_temps"] == 0:
                    d = abs(ennemi["position"]["x"] - abeille["position"]["x"]) + abs(ennemi["position"]["y"] - abeille["position"]["y"])
                    if d < dist_min:
                        dist_min = d
                        cible_pos = ennemi["position"]
            if cible_pos is None:
                cible_pos = joueur_vise["position"]
        
        if cible_pos is None:
            cible_pos = abeille["position"]

        data_abeille["fleur_cible"] = cible_pos
        return data_abeille["fleur_cible"] or abeille["position"]

    def choix_ouvriere(self, abeille, data_abeille, jeu, fleurs_cibles):
        if data_abeille["fleur_cible"] is None:
            dist_min = self.ncases * 2
            for fleur in jeu["fleurs"]:
                if (fleur["x"], fleur["y"]) in self.fleurs_vides or fleur in fleurs_cibles:
                    continue
                dist = abs(fleur["x"] - abeille["position"]["x"]) + abs(fleur["y"] - abeille["position"]["y"])
                if dist < dist_min:
                    dist_min = dist
                    data_abeille["fleur_cible"] = fleur

        dist_base_x = abs(abeille["position"]["x"] - jeu["moi"]["position"]["x"])
        dist_base_y = abs(abeille["position"]["y"] - jeu["moi"]["position"]["y"])
        zone_confiance = self.ncases // 4
        est_loin = (dist_base_x > zone_confiance or dist_base_y > zone_confiance)

        if abeille["nectar"] == 0:
            data_abeille["mode_retour"] = False
        
        if abeille["nectar"] == abeille["max_nectar"] or (abeille["nectar"] >= 5 and est_loin):
            data_abeille["mode_retour"] = True

        if data_abeille["mode_retour"]:
            cible = jeu["moi"]["position"]
        else:
            cible = data_abeille["fleur_cible"] or abeille["position"]

        doit_butiner = False
        if abs(abeille["position"]["x"] - cible["x"]) <= 1 and abs(abeille["position"]["y"] - cible["y"]) <= 1:
            if cible != abeille["position"]:
                doit_butiner = True
            
        return cible, doit_butiner

    def calcul_mouvement(self, abeille, cible, cases_interdites):
        dx, dy = 0, 0
        
        dir_x = 0
        if cible["x"] > abeille["position"]["x"]:
            dir_x = 1
        elif cible["x"] < abeille["position"]["x"]:
            dir_x = -1
        
        dir_y = 0
        if cible["y"] > abeille["position"]["y"]:
            dir_y = 1
        elif cible["y"] < abeille["position"]["y"]:
            dir_y = -1
        
        dist_x = abs(cible["x"] - abeille["position"]["x"])
        dist_y = abs(cible["y"] - abeille["position"]["y"])

        if dist_x > dist_y:
            if dir_x != 0 and (abeille["position"]["x"] + dir_x, abeille["position"]["y"]) not in cases_interdites:
                dx = dir_x
            elif dir_y != 0 and (abeille["position"]["x"], abeille["position"]["y"] + dir_y) not in cases_interdites:
                dy = dir_y
            elif dir_y != 0 and (abeille["position"]["x"], abeille["position"]["y"] - dir_y) not in cases_interdites:
                dy = -dir_y
            elif dir_x != 0 and (abeille["position"]["x"] - dir_x, abeille["position"]["y"]) not in cases_interdites:
                dx = -dir_x
        else:
            if dir_y != 0 and (abeille["position"]["x"], abeille["position"]["y"] + dir_y) not in cases_interdites:
                dy = dir_y
            elif dir_x != 0 and (abeille["position"]["x"] + dir_x, abeille["position"]["y"]) not in cases_interdites:
                dx = dir_x
            elif dir_x != 0 and (abeille["position"]["x"] - dir_x, abeille["position"]["y"]) not in cases_interdites:
                dx = -dir_x
            elif dir_y != 0 and (abeille["position"]["x"], abeille["position"]["y"] - dir_y) not in cases_interdites:
                dy = -dir_y
                
        return dx, dy