import requests
import logging
import json
from .commit import Commit

class Namespace:
    def __init__(self, json):
        self.__json = json

    def id(self):
        return int(self.__json["id"])

    def namespace(self):
        return self.__json["name"]

    def alias(self):
        return self.__json["instanceName"]

    def type(self):
        return self.__json["type"]
    
    def phase(self):
        return self.__json["phase"]

    def status(self):
        return self.__json["status"]

    def access(self):
        return self.__json["access"]

    def url(self):
        return self.__json["url"]

class NamespaceApi:
    """Namespace api"""

    def __init__(self, staroid, cluster):
        self.__staroid = staroid
        self.__cluster = cluster

    def get_all(self):
        r = self.__staroid._api_get(
            "orgs/{}/vc/{}/instance".format(
                self.__staroid.get_account(),
                self.__cluster.id()
            )
        )
        if r.status_code == 200:
            json_object_list = json.loads(r.text)
            namespace_list = []
            for js in json_object_list:
                namespace_list.append(Namespace(js))
            return namespace_list
        else:
            logging.error("Can not get clusters {}", r.status_code)
            return None

    def get(self, instance_name):
        namespaces = self.get_all()
        if namespaces == None:
            return None

        for ns in namespaces:
            if ns.alias() == instance_name:
                return ns

        return None

    def get_by_id(self, instance_id):
        r = self.__staroid._api_get(
            "orgs/{}/vc/{}/instance/{}".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                instance_id
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        else:
            logging.error("Can not get namespace {}", r.status_code)
            return None

    def create(self, instance_name, commit_url):
        c = Commit(commit_url)

        r = self.__staroid._api_post(
            "orgs/{}/vc/{}/instance".format(
                self.__staroid.get_account(),
                self.__cluster.id()
            ),
            {
                "provider": c.provider(),
                "owner": c.owner(),
                "repo": c.repo(),
                "branch": c.branch(),
                "commit": c.commit(),
                "instanceName": instance_name
            }
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        elif r.status_code == 409: # already exists
            return self.get(instance_name)
        else:
            logging.error("Can not create namespace {}", r.status_code)
            return None

    def delete(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_delete(
            "orgs/{}/vc/{}/instance/{}".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                ns.id()
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        else:
            logging.error("Can not delete namespace {}", r.status_code)
            return None


    def start(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_put(
            "orgs/{}/vc/{}/instance/{}/resume".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                ns.id()
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        else:
            logging.error("Can not start namespace {}", r.status_code)
            return None


    def stop(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_put(
            "orgs/{}/vc/{}/instance/{}/pause".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                ns.id()
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        else:
            logging.error("Can not stop namespace {}", r.status_code)
            return None


    def shell_start(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_post(
            "orgs/{}/vc/{}/instance/{}/shell".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                ns.id()
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return Namespace(js)
        else:
            logging.error("Can not start shell {}", r.status_code)
            return None

    def shell_stop(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_delete(
            "orgs/{}/vc/{}/instance/{}/shell".format(
                self.__staroid.get_account(),
                self.__cluster.id(),
                ns.id()
            )
        )
        if r.status_code == 200:
            return None
        else:
            logging.error("Can not stop shell {}", r.status_code)
            return None
