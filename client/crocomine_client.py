"""
Le module crocomine_client contient la classe CrocomineClient
permettant d'accéder de façon transparente à un serveur Crocomine.
"""

from pprint import pprint
from typing import Dict, Any, Tuple, List
import requests

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2021, Université de technologie de Compiègne"
__license__ = "LGPL-3.0"
__version__ = "1.0.0"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"

# Déclaration des types utilisés

Status = str
Msg = str
Info = Dict[str, Any]
Infos = List[Info]
GridInfos = Dict[str, Any]


class CrocomineClient:
    """Cette classe permet d'accéder de façon transparente à un serveur Crocomine."""

    def __init__(self, server: str, group: str, members: str, password: str, log: bool = False):
        self._basename = server + "/crocomine"
        self._members = members
        self._id = group
        self._token = "Not defined"
        self._password = password
        self.log = log

        self._session = requests.Session()
        self.register()

    def _format_data(self, i=None, j=None, animal=None, password=None):
        data = {
            "id": self._id,
            "members": self._members,
            "token": self._token,
        }

        if not i is None and not j is None:
            data["pos"] = [i, j]

        if animal:
            data["animal"] = animal
        
        if password:
            data["password"] = password

        return data

    def _request(self, cmd: str, data: Dict[str, Any]) -> Dict[str, Any]:
        req = self._session.post(f"{self._basename}/{cmd}", json=data)

        if req.status_code != requests.codes.ok:
            print("Erreur requête:", req.text)
            req.raise_for_status()

        answer = req.json()

        if self.log:
            print("[log] REQUEST to server:", cmd)
            print("[log]", end="")
            pprint(data)
            print("[log] ANSWER:")
            print("[log]", end="")
            pprint(answer)
            print()

        return answer

    def register(self) -> Tuple[Status, Msg]:
        """Permet de s'inscrire à un serveur Crocomine."""

        data = self._format_data(password=self._password)
        res = self._request("register", data)
        if "token" in res:
            self._token = res["token"]

        return res["status"], res["msg"]

    def new_grid(self) -> Tuple[Status, Msg, GridInfos]:
        """Passe à la grille suivante."""

        data = self._format_data()
        res = self._request("new_grid", data)

        if res["status"] != "OK":
            return res["status"], res["msg"], {}
        return res["status"], res["msg"], res["grid_infos"]

    def discover(self, i: int, j: int) -> Tuple[Status, Msg, Infos]:
        """Découvre la case (i,j)."""

        data = self._format_data(i, j)
        res = self._request("discover", data)

        if res["status"] != "OK":
            return res["status"], res["msg"], []
        return res["status"], res["msg"], res["infos"]

    def guess(self, i: int, j: int, animal: str):
        """Devine que la case (i,j) est de type ```animal```"""

        data = self._format_data(i, j, animal)
        res = self._request("guess", data)

        if res["status"] != "OK":
            return res["status"], res["msg"], []
        return res["status"], res["msg"], res["infos"]

    def chord(self, i: int, j: int) -> Tuple[Status, Msg, Infos]:
        """Propose un accord sur la case (i,j)."""

        data = self._format_data(i, j)
        res = self._request("chord", data)

        if res["status"] != "OK":
            return res["status"], res["msg"], []
        return res["status"], res["msg"], res["infos"]
