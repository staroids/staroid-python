import requests
import logging
import json

class NamespaceApi:
    """Namespace api"""

    def __init__(self, cluster_api):
        self.__staroid = cluster_api.__staroid
        self.__cluster_api = cluster_api

    def get_all(self):
        r = self.__staroid._api_get(
            "orgs/{}/vc/{}/instance".format(
                self.__staroid.get_org(),

                ))
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            logging.error("Can not get clusters {}", r.status_code)
            return None
