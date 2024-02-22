# https://github.com/Art-of-WiFi/UniFi-API-client/tree/master/src
# https://www.youtube.com/watch?v=t-_wVzULmUY

import json
import netrc
import os
import requests
from requests.models import CaseInsensitiveDict
import urllib3

from .logger import LogLevel, Logger
from .typing import ApiTarget, PoeMode, MacAddr


class UnifiApiClient:
    logger = Logger("UnifiRestApi", LogLevel.INFO)
    defaultHeaders = {
        "Accept": "application/json; charset=UTF-8",
        "Content-Type": "application/json; charset=UTF-8",
    }

    def __init__(self, server: str, site: str = "default", verify: bool = True):
        self.__site = site
        self.__server = server
        self.__cookie = None

        self.__verify = verify
        if not verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.__isRunningUnifiOs()

    def __storeCookies(self, headers: CaseInsensitiveDict):
        # update only when a new csrf has been offered
        token = headers.get("x-updated-csrf-token", None)
        if token is None:
            return
        self.__csrf = token
        self.__cookie = headers.get("set-cookie")
        # self.__expiry = headers.get("x-token-expire-time")

    def __getHeaders(self) -> dict:
        h = self.defaultHeaders.copy()
        if self.__cookie:
            h.update({"Cookie": self.__cookie, "X-CSRF-Token": self.__csrf})
        return h

    def __getProxy(self, target: ApiTarget = ApiTarget.NETWORK) -> str | None:
        if self.__isConsoleOs and target is not ApiTarget.OS:
            return f"proxy/{target.value}"
        return None

    def __getSite(self, site: bool = True) -> str | None:
        if site:
            return f"s/{self.__site}"
        return None

    def __getUrl(self, path: str | None = None, **kwds) -> str:
        target = kwds.pop("target", ApiTarget.NETWORK)
        site = kwds.pop("site", True)
        url = "/".join(
            filter(
                None,
                (
                    "https:/",
                    self.__server,
                    self.__getProxy(target),
                    "api" if path else None,
                    self.__getSite(site),
                    path,
                ),
            )
        )
        return url

    def __isRunningUnifiOs(self):
        self.__isConsoleOs = False
        r = self.__get(path=None, data=None, target=ApiTarget.OS, site=False)
        if r.status_code == 200:
            self.__isConsoleOs = True
            self.logger.info("connecting to '%s' running Unifi OS", self.__server)
        else:
            self.__isConsoleOs = False
            self.logger.info("connecting to '%s'", self.__server)

    def __processAnyErrors(self, response: requests.Response):
        rc = 200 <= response.status_code < 300
        if rc:
            ct = response.headers.get("Content-Type", "")
            if not ct.startswith("application/json"):
                return

        # print(f"{response.status_code}\n{response.headers}\n{response.text}")
        j = response.json()
        if "meta" in j:
            rc = j["meta"]["rc"] == "ok"
        if not rc:
            if "message" in j:
                message = j.get("message")
            elif "meta" in j:
                message = j["meta"]["msg"]
            else:
                message = "<nodef>"
                self.logger.error("error occured, but no message found")
                self.logger.debug("no message found in '%s'", j)

            raise requests.exceptions.RequestsWarning(
                response.request.url, response.status_code, message
            )

    def __getDataFromResponse(self, response: requests.Response) -> dict:
        ct = response.headers.get("Content-Type", "")
        if not ct.startswith("application/json"):
            return {}

        data = response.json()
        if "meta" in data:
            data = data["data"]

        if self.logger.getLevel() is LogLevel.DEBUG:
            request = response.request
            self.logger.debug("requested '%s'", request.url)
            j = json.loads(request.body or "{}")
            if "password" in j:
                j["password"] = "<redacted>"
            for line in json.dumps(j, indent=4).splitlines():
                self.logger.debug("    %s", line)
            self.logger.debug(
                "response '%i' from '%s'", response.status_code, self.__server
            )
            for line in json.dumps(data, indent=4).splitlines():
                self.logger.debug("    %s", line)
        return data

    def __request(self, method: str, data={}, **kwds):
        api = self.__getUrl(**kwds)
        headers = self.__getHeaders()
        r = requests.request(
            method, api, json=data, headers=headers, verify=self.__verify
        )
        self.__processAnyErrors(r)
        self.__storeCookies(r.headers)
        return r

    def __put(self, **kwds):
        return self.__request("PUT", **kwds)

    def __post(self, **kwds):
        return self.__request("POST", **kwds)

    def __get(self, **kwds):
        return self.__request("GET", **kwds)

    def ping(self) -> bool:
        self.logger.info("pinging")
        r = self.__get(path="ping", data=None, target=ApiTarget.OS, site=False)
        self.__getDataFromResponse(r)
        if r.status_code == 204:
            self.logger.debug("server '%s' is active", self.__server)
            return True
        return False

    def status(self) -> bool:
        r = self.__get(path="status", data=None, target=ApiTarget.OS, site=False)
        if r.status_code == 204:
            self.logger.info("status '%s'", self.__server)
            return True
        return False

    def sysinfo(self) -> bool:
        r = self.__get(path="stat/sysinfo", data=None)
        loglevel = self.logger.setLevel(LogLevel.DEBUG)
        self.__getDataFromResponse(r)
        self.logger.setLevel(loglevel)
        return r.status_code == 200

    def login(self, netrcFile: str) -> bool:
        fn = os.path.expanduser(netrcFile)
        nr = netrc.netrc(fn)
        auth = nr.authenticators(self.__server)

        user = auth[0] if auth else "<nodef>"
        data = {"username": user, "password": auth[2] if auth else "<nodef>"}
        path = "auth/login" if self.__isConsoleOs else "login"
        r = self.__post(path=path, data=data, target=ApiTarget.OS, site=False)

        self.__getDataFromResponse(r)
        if r.status_code != 200:
            return False
        self.logger.info("successfully logged into '%s' as '%s'", self.__server, user)
        return True

    def logout(self):
        if not self.__cookie:
            return False

        api = "logout"
        if self.__isConsoleOs:
            api = f"auth/{api}"
        r = self.__post(path=api, target=ApiTarget.OS, site=False)
        if r.status_code != 200:
            return False

        del self.__csrf
        self.__cookie = None
        self.logger.info("logout of '%s'", self.__server)
        return True

    def cyclePoePortPower(self, mac: MacAddr, port: int) -> bool:
        data = {"mac": mac.value, "port_idx": port, "cmd": "power-cycle"}
        r = self.__post(path="cmd/devmgr", data=data)
        if r.status_code != 200:
            return False
        self.logger.info("power cycle port '%s' on device '%s'", port, mac)
        return True

    def setPoeModeByPortProfileName(self, poeMode: PoeMode, name: str):
        nr = self.__put(path="list/portconf", data={"name": name})
        data = self.__getDataFromResponse(nr)
        id = data[0]["_id"] if data else None

        r = self.__put(path=f"rest/portconf/{id}", data={"poe_mode": poeMode.value})
        data = self.__getDataFromResponse(r)

        if r.status_code != 200:
            return False
        self.logger.info(
            f"port profile '{id}' named '{name}' - poe_mode %s '{poeMode.value}'",
            "set to" if data else "already",
        )
        return True

    def getDeviceDetails(self, mac: MacAddr | None = None, port: int | None = None):
        if mac is not None:
            data = {"macs": [mac.value]}
        else:
            data = None
        r = self.__post(path="stat/device", data=data)

        if r.status_code != 200:
            return {}
        d = self.__getDataFromResponse(r)
        if mac is not None:
            d = d[0]
            if d["mac"] != mac:
                raise RuntimeError(f'getDeviceDetails requested {mac} got {d["mac"]}')
            elif port is not None:
                p = [p for p in d["port_overrides"] if p["port_idx"] == port]
                if len(p) != 1:
                    raise RuntimeError(f"getDeviceDetails {mac} port {port} not found")
                d = p[0]
        return d
