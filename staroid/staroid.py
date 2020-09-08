import os, stat
import yaml
import logging
import requests
import json
from pathlib import Path
from shutil import which
import platform
import subprocess
import wget

from .cluster import ClusterApi
from .namespace import NamespaceApi

CHISEL_VERSION="1.6.0"
CHISEL_ARCH_MAP={
    "x86_64": "amd64",
    "i386": "386"
}

class Org:
    def __init__(self, json):
        self.__json = json

    def name(self):
        return self.__json["name"]

    def provider(self):
        return self.__json["provider"]

    def id(self):
        return int(self.__json["id"])

class User:
    def __init__(self, json):
        self.__json = json

    def name(self):
        return self.__json["name"]

    def provider(self):
        return self.__json["provider"]

    def principal(self):
        return self.__json["principal"]


class Staroid:
    """Staroid client object"""

    def __init__(self, access_token=None, account=None, config_path=None, cache_dir=None, chisel_path=None):
        self.__api_addr = "https://staroid.com/api"
        self.__access_token = None
        self.__account = None
        self.__cache_dir = cache_dir
        self.__chisel_path = chisel_path

        if self.__cache_dir == None:
            self.__cache_dir = "{}/.staroid".format(str(Path.home()))

        # 1. set from configs
        self.__read_config(config_path)

        # 2. set from env
        if "STAROID_ACCESS_TOKEN" in os.environ:
            self.__access_token = os.environ["STAROID_ACCESS_TOKEN"]

        if "STAROID_ACCOUNT" in os.environ:
            self.__account = os.environ["STAROID_ACCOUNT"]

        # 3. set from args
        if access_token != None:
            self.__access_token = access_token
        
        if account != None:
            self.__account = account

        # if account is not set, set default user account
        if self.__account == None:
            user = self.get_user()
            if user != None:
                self.__account = "{}/{}".format(user.provider(), user.principal())

    def __read_config(self, config_path):
        if config_path == None:
            config_path = "{}/.staroid/config.yaml".format(str(Path.home()))

        try:
            with open(config_path, "r") as f:
                logging.info("Read configuration from " + config_path)
                data = yaml.load(f, Loader=yaml.FullLoader)
                self.__access_token = data.get("access_token", None)
                self.__account = data.get("account", None)
        except EnvironmentError:
            pass

    def create_or_get_cache_dir(self, module = ""):
        "create (if not exists) or return cache dir path for module"
        cache_dir = "{}/{}".format(self.__cache_dir, module)
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        return cache_dir

    def __check_cmd(self, cmd):
        if which(cmd) == None:
            raise Exception("'{}' command not found".format(cmd))

    def __download_chisel_if_not_exists(self):
        # check gunzip available
        self.__check_cmd("gunzip")

        if self.__chisel_path == None:
            # download chisel binary for secure tunnel if not exists
            uname = platform.uname()
            uname.system.lower()
            if uname.machine not in CHISEL_ARCH_MAP.keys():
                raise Exception("Can not download chisel automatically. Please download manually from 'https://github.com/jpillora/chisel/releases/download/v{}' and set 'chisel_path' argument".format(CHISEL_VERSION))

            download_url = "https://github.com/jpillora/chisel/releases/download/v{}/chisel_{}_{}_{}.gz".format(
                CHISEL_VERSION, CHISEL_VERSION, uname.system.lower(), CHISEL_ARCH_MAP[uname.machine])
            cache_bin = self.create_or_get_cache_dir("bin")
            chisel_path = "{}/chisel".format(cache_bin)

            if not os.path.exists(chisel_path):
                # download
                filename = wget.download(download_url, cache_bin)

                # extract
                subprocess.run(["gunzip", "-f", filename])

                # rename
                subprocess.run(["mv", filename.replace(".gz", ""), chisel_path])

                # chmod
                os.chmod(chisel_path, stat.S_IRWXU)

            self.__chisel_path = chisel_path

    def get_chisel_path(self):
        self.__download_chisel_if_not_exists()
        return self.__chisel_path

    def cluster(self):
        c = ClusterApi(self)
        return c

    def namespace(self, cluster):
        n = NamespaceApi(self, cluster)
        return n

    def get_access_token(self):
        return self.__access_token

    def get_account(self):
        return self.__account

    def with_account(self, account):
        self.__account = account
        return self

    def get_user(self):
        "read user information"
        if self.__access_token == None:
            return None

        r = self._api_get("auth/user")
        if r.status_code == 200:
            js = json.loads(r.text)
            return User(js)
        else:
            return None

    def get_all_accounts(self):
        r = self._api_get("orgs/")
        if r.status_code == 200:
            org_object_list = json.loads(r.text)
            org_list = []
            for js in org_object_list:
                org_list.append(Org(js))

            return org_list
        else:
            logging.error("Can't get accounts")
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

    def _api_post(self, path, payload=None):
        url = self.__get_request_url(path);
        headers = self.__get_request_headers()

        r = requests.post(url, headers=headers, data=json.dumps(payload))
        return r

    def _api_put(self, path, payload=None):
        url = self.__get_request_url(path);
        headers = self.__get_request_headers()

        r = requests.put(url, headers=headers, data=json.dumps(payload))
        return r

    def _api_delete(self, path):
        url = self.__get_request_url(path);
        headers = self.__get_request_headers()

        r = requests.delete(url, headers=headers)
        return r
