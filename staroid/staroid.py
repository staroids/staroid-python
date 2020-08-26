import os
import yaml
import logging
import requests
import json
from .cluster import ClusterApi

class Staroid:
    """Staroid client object"""

    def __init__(self, access_token=None, org=None, config_path="~/.staroid/config.yaml"):
        self.__api_addr = "https://staroid.com/api"
        self.__read_config(config_path)

        if access_token != None:
            self.__access_token = access_token
        
        if org != None:
            self.__org = org

    def __read_config(self, config_path):
        try:
            with open(config_path, "r") as f:
                logging.info("Read configuration from " + config_path)
                data = yaml.load(f, Loader=yaml.FullLoader)
                self.__access_token = data.get("access_token", None)
                self.__org = data.get("default_org", None)
        except EnvironmentError:
            pass


    def cluster(self):
        c = ClusterApi(self)
        return c

    def get_access_token(self):
        return self.__access_token

    def get_org(self):
        return self.__org

    def with_org(self, org):
        self.__org = org
        return self

    def get_all_orgs(self):
        r = self._api_get(self, "orgs/")
        if r.status_code == 200:
            return json.loads(r.text)
        else:
            logging.error("Can't get orgs")
            return None

    def __get_request_url(self, path):
        request_url = "{}/{}".format(self.__api_addr, path)
        return request_url

    def __get_request_headers(self):
        headers = {
            "Authorization": "token {}".format(self.__access_token),
            "Content-Type": "application/json"
        }
        return headers

    def _api_get(self, path):
        url = self.__get_request_url(path);
        headers = self.__get_request_headers()

        r = requests.get(url, headers=headers)
        return r

    
    def _api_post(self, path, payload):
        url = self.__get_request_url(path);
        headers = self.__get_request_headers()

        r = requests.get(url, headers=headers, data=json.dumps(payload))
        return r
