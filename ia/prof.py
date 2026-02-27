import random
from typing import Literal

from ia import JeuDict, MoteurIA


class IAnulle(MoteurIA):
    nom = "Nulle"

    def __init__(
        self, joueur_id: str, ncases: int, max_tours: int, temps_ko: int
    ) -> None:
        self.joueur_id = joueur_id
        self.ncases = ncases
        self.max_tours = max_tours
        self.temps_ko = temps_ko

        self.a_deja_pondu = False
        self.premier_tour_joueur = True
        self.fleur_cible = None

    def ponte(
        self, jeu: JeuDict, cout_ponte: int
    ) -> Literal["OUV", "BOU", "ECL", "RIEN"]:
        if self.a_deja_pondu:
            return "RIEN"

        self.a_deja_pondu = True
        return "OUV"

    def action_abeilles(
        self, jeu: JeuDict
    ) -> list[tuple[str, int, int, Literal["DEPLACEMENT", "BUTINAGE"]]]:
        if self.premier_tour_joueur:
            self.fleur_cible = jeu["fleurs"][0]
            self.premier_tour_joueur = False

        abeille = jeu["moi"]["abeilles"][0]

        if abeille["nectar"] > 0:
            cible = jeu["moi"]["position"]
        else:
            cible = self.fleur_cible

            if abs(abeille["position"]["x"] - cible["x"]) <= 1 and abs(abeille["position"]["y"] - cible["y"]) <= 1:
                return [
                    (abeille["id"], cible["x"], cible["y"], "BUTINAGE")
                ]
        dx = dy = 0

        if abeille["position"]["x"] < cible["x"]:
            dx = 1
        elif abeille["position"]["x"] > cible["x"]:
            dx = -1
        elif abeille["position"]["y"] < cible["y"]:
            dy = 1
        elif abeille["position"]["y"] > cible["y"]:
            dy = -1
        
        return [
            (abeille["id"], abeille["position"]["x"] + dx, abeille["position"]["y"] + dy, "DEPLACEMENT")
        ]