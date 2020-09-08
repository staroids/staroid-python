import requests
import logging
import json
import subprocess
import atexit
import time
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
        self.__tunnel_processes = {}

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
            return js
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

    def get_all_resources(self, instance_name):
        ns = self.get(instance_name)
        if ns == None:
            return None

        r = self.__staroid._api_get(
            "namespace/{}".format(
                ns.namespace()
            )
        )
        if r.status_code == 200:
            js = json.loads(r.text)
            return js
        else:
            logging.error("Can not get namespace resources {}", r.status_code)
            return None

    def _is_tunnel_running(self, instance_name):
        if instance_name in self.__tunnel_processes:
            p = self.__tunnel_processes[instance_name]
            p.poll()
            return p.returncode == None
        else:
            return False

    def start_tunnel(self, instance_name, tunnels):
        if self._is_tunnel_running(instance_name):
            return

        chisel_path = self.__staroid.get_chisel_path()

        ns = self.get(instance_name)
        if ns == None:
            return None
        resources = self.get_all_resources(instance_name)

        shell_service = None
        for s in resources["services"]["items"]:
            if "labels" in s["metadata"]:
                if "resource.staroid.com/system" in s["metadata"]["labels"]:
                    if s["metadata"]["labels"]["resource.staroid.com/system"] == "shell":
                        shell_service = s
                        break                        

        if shell_service == None:
            raise Exception("Shell service not found")

        tunnel_server = "https://p{}-{}--{}".format("57682", shell_service["metadata"]["name"], ns.url()[len("https://"):])
        cmd = [
            chisel_path,
            "client",
            "--header",
            "Authorization: token {}".format(self.__staroid.get_access_token()),
            "--keepalive",
            "10s",
            tunnel_server
        ]
        cmd.extend(tunnels)
        self.__tunnel_processes[instance_name]=subprocess.Popen(cmd)
        atexit.register(self.__cleanup)

    def __cleanup(self):
        timeout_sec = 5
        for p in self.__tunnel_processes.values(): # list of your processes
            p_sec = 0
            for second in range(timeout_sec):
                if p.poll() == None:
                    time.sleep(1)
                    p_sec += 1
            if p_sec >= timeout_sec:
                p.kill() # supported from python 2.6

    def stop_tunnel(self, instance_name):
        if self._is_tunnel_running(instance_name):
            self.__tunnel_processes[instance_name].kill()
            del self.__tunnel_processes[instance_name]

