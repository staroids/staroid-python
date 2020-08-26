import requests
import logging
import json

class Cluster:
    """Cluster object"""

    def __init__(self, staroid=None):
        self.__staroid = staroid

    def get_all(self):
        r = self.__staroid._api_get("orgs/{}/vc".format(self.__staroid.get_org()))
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            logging.error("Can not get clusters {}", r.status_code)
            return None