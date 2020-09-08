import requests
import logging
import json

CLUSTER_ID_MAP={
    "gcp us-west1": 1,
    "aws us-west2": 2
}

class SKE:
    def __init__(self, json):
        self.__json = json

    def name(self):
        return self.__json["name"]

    def cloud(self):
        return self.__json["cloud"]

    def region(self):
        return self.__json["region"]

class Cluster:
    def __init__(self, json):
        self.__json = json

    def id(self):
        return int(self.__json["id"])

    def name(self):
        return self.__json["name"]

    def ske(self):
        return SKE(self.__json["ske"])

    def org_id(self):
        return int(self.__json["orgId"])
    
    def type(self):
        return self.__json["type"]


class ClusterApi:
    """Cluster api"""

    def __init__(self, staroid):
        self.__staroid = staroid

    def get(self, name):
        clusters = self.get_all()
        cluster_found = None
        for c in clusters:
            if c.name() == name:
                cluster_found = c
                break

        return cluster_found

    def get_all(self):
        r = self.__staroid._api_get("orgs/{}/vc".format(self.__staroid.get_account()))
        if r.status_code == 200:
            json_object_list = json.loads(r.text)
            cluster_list = []
            for js in json_object_list:
                cluster_list.append(Cluster(js))

            return cluster_list
        else:
            logging.error("Can not get clusters {}", r.status_code)
            return None

    def create(self, name, cluster="gcp us-west1"):
        r = self.__staroid._api_post(
            "orgs/{}/vc".format(self.__staroid.get_account()),
            {
                "name": name,
                "clusterId": CLUSTER_ID_MAP[cluster]
            }
        )

        if r.status_code == 200:
            json_object = json.loads(r.text)
            return Cluster(json_object)
        elif r.status_code == 409: # already exists
            return self.get(name)
        else:
            logging.error("Can not create clusters {}", r.status_code)
            return None


    def delete(self, name):
        cluster_to_del = self.get(name)
        if cluster_to_del != None:
            r = self.__staroid._api_delete(
                "orgs/{}/vc/{}".format(self.__staroid.get_account(), cluster_to_del.id())
            )
        else:
            return None

        if r.status_code == 200:
            return cluster_to_del
        else:
            logging.error("Can not delete clusters {}", r.status_code)
            return None
