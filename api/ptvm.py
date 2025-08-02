import requests
import logging
import json
import time
import datetime
proxies = {"http": "10.10.10.10:8080",
           "https": "10.10.10.10:8080"}


"""
1. added proxy
2. added exportByPDQLByGroup - Экспорт данных в CSV файл на базе PDQL запроса с 
учетом группы активов и ошибки 404
"""

"""
Добавлено в бибилиотеку:
getGroupsInfo - для получения списка групп и их id
"""


class PTVM(object):
    login = ""
    password = ""
    ptvm_host = ""
    ptvm_api_port = 3334
    ptvm_front_port = 443
    client_secret = ""
    access_token = ""
    sleepBetweenQueryPDQLAndGettingDATA = 10  # sleep between 2 requests: search and get data by pdqlToken

    def __init__(self, host, client_secret, login, password):
        requests.packages.urllib3.disable_warnings()
        self.logger = logging.getLogger('PTVM.' + __name__)
        self.ptvm_host = host
        self.login = login
        self.client_secret = client_secret
        self.password = password

    def connect(self):
        """ установка соединения, получение access токена"""
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {"grant_type": "password", "client_id": "mpx", "client_secret": self.client_secret,
                    "scope": "mpx.api", "response_type": "code id_token token",
                    "username": self.login, "password": self.password}
            #"scope": "authorization offline_access mpx.api ptkb.api"
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_api_port) + "/connect/token"
            #r = requests.Session()
            #r = requests.post(url, data=data, headers=headers, proxies=proxies, verify=False) #With proxy
            r = requests.post(url, data=data, headers=headers, verify=False)
            print('Debug: ', url)
            print('Debug: ', data)
            print('Debug: ', headers)
            print('Debug: ', r.json())
            self.access_token = r.json()["access_token"]
            self.authHeader = {'Authorization': 'Bearer ' + self.access_token}
            self.logger.debug("Got access token")
        except:
            self.logger.error("unable to get token ", exc_info=True)

    def getGroupsInfo(self):
        """ Получение списка групп активов """
        tasks = {}
        try:
            url = "https://" + self.ptvm_host + ":" + str(
                self.ptvm_front_port) + "/api/assets_temporal_readmodel/v2/groups/hierarchy"
            r = requests.get(url, headers=self.authHeader, proxies=proxies, verify=False)
            assets_groups = r.json()
            print(assets_groups)

        except:
            self.logger.error("unable to get groups ", exc_info=True)
        return tasks

    def scanTaskStart(self, taskId):
        """ запуск задачи скана по идентификатору задачи"""
        try:
            data = {}
            url = "https://" + self.ptvm_host + ":" + str(
                self.ptvm_front_port) + "/api/scanning/v3/scanner_tasks/" + taskId + "/start"
            r = requests.post(url, headers=self.authHeader, data=data, verify=False)
        except:
            self.logger.error("unable to start task " + taskId, exc_info=True)

    def scanTaskStop(self, taskId):
        """ остановка задачи скана по идентификатору задачи"""
        try:
            data = {}
            url = "https://" + self.ptvm_host + ":" + str(
                self.ptvm_front_port) + "/api/scanning/v3/scanner_tasks/" + taskId + "/stop"
            r = requests.post(url, headers=self.authHeader, data=data, verify=False)
        except:
            self.logger.error("unable to stop task " + taskId, exc_info=True)

    def getScanTasks(self):
        """ Получение списка задач сканирования """
        tasks = {}
        try:
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/scanning/v3/scanner_tasks"
            r = requests.get(url, headers=self.authHeader, verify=False)
            tasks = r.json()

        except:
            self.logger.error("unable to get scam tasks ", exc_info=True)
        return tasks

    def queryPDQL(self, pdql):
        """ Выполнение PDQL запроса, возвращается токен доступа к результатам (сами данные не возвращаются их необходимо запрашивать по токену с помощью getDataByPDQLToken) """
        token = None
        try:
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
            data = {"pdql": pdql, "includeNestedGroups": "true", "utcOffset": "+03:00"}
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid"
            r = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, verify=False)
            print('Debug :', r.json())
            token = r.json()["token"]
        except:
            self.logger.error("unable to query PDQL " + pdql, exc_info=True)
        return token

    #From assets groups
    def queryPDQLbyGroup(self, pdql, groupid):
        """ Выполнение PDQL запроса, возвращается токен доступа к результатам (сами данные не возвращаются их необходимо запрашивать по токену с помощью getDataByPDQLToken) """
        token = None
        try:
            headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
            data = {"pdql": pdql, "selectedGroupIds": groupid, "includeNestedGroups": "true", "utcOffset": "+03:00"}
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid"
            #r = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, verify=False) #with proxy
            r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)
            print('Debug :', r.json())
            token = r.json()["token"]
        except:
            self.logger.error("unable to query PDQL " + pdql, exc_info=True)
        return token

    def getDataByPDQLToken(self, pdqlToken, limit):
        """  Запрос данных по pdqlToken, возвращается limit записей. Перед вызовом лучше вводить таймаутом, т.к. иногда возникает ситуация, когда ничего не возвращается."""
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid/data?limit=" + str(
            limit) + "&pdqlToken=" + pdqlToken
        r = requests.get(url, headers=self.authHeader, proxies=proxies, verify=False)
        print('Debug :', r.json())
        response = r.json()
        records = response["records"]
        return records

    def getHostIdByIP(self, ip):
        """ Поиска идентификатора ассета по IP адресу """
        id = None
        pdql = "filter(Host.IpAddress = " + ip + ")| select(@Host, Host.OsName, Host.@UpdateTime, Host.IpAddress)"
        token = self.queryPDQL(pdql)
        time.sleep(self.sleepBetweenQueryPDQLAndGettingDATA)
        if token != None:
            records = self.getDataByPDQLToken(token, 10)
            if len(records) == 1:
                id = records[0]["@Host"]["id"]
            else:
                logger.warn("More than one record found for " + ip)
        return id

    def getHostIdsByPDQL(self, pdql, limit=1000):
        """ Поиска идентификатора ассета по PDQL запросу """
        ids = []
        token = self.queryPDQL(pdql)
        time.sleep(self.sleepBetweenQueryPDQLAndGettingDATA)
        if token != None:
            records = self.getDataByPDQLToken(token, limit)
            for rec in records:
                ids.append(rec["@Host"]["id"])

        return ids

    def exportByPDQL(self, pdql, fileName):
        """ Экспорт данных в CSV файл на базе PDQL запроса """
        try:
            token = self.queryPDQL(pdql)
            time.sleep(self.sleepBetweenQueryPDQLAndGettingDATA)
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid/export?pdqlToken=" + token
            r = requests.get(url, headers=self.authHeader, verify=False)
            open(fileName, 'wb').write(r.content)
        except:
            self.logger.error("unable exportByPDQL ", exc_info=True)

    #Export with group ID
    def exportByPDQLByGroup(self, pdql, fileName, sleep_time, gr):
        """ Экспорт данных в CSV файл на базе PDQL запроса с учетом группы активов и ошибки 404"""
        count = 0
        limit = True
        while limit and count <= 10:
            token = self.queryPDQLbyGroup(pdql, gr)
            print('Using token: ', token)
            url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid/export?pdqlToken=" + token
            time.sleep(sleep_time)
            try:
                #r = requests.get(url, headers=self.authHeader, proxies=proxies, verify=False) #with proxy
                r = requests.get(url, headers=self.authHeader, verify=False)
            except:
                self.logger.error("unable exportByPDQL ", exc_info=True)
            else:
                if r.status_code == 404:
                    sleep_time += 120 # sleep +2 minute
                    count += 1
                    print('{}, status is 404, waiting : {} seconds, try - {} out of 10'.format(datetime.datetime.now(), sleep_time, count))
                else:
                    limit = False
                    open(fileName, 'wb').write(r.content)
                    print('{} - Done!'.format(datetime.datetime.now()))

    #Замер времени между запросами
    def exportByPDQLByGroupWtime(self, pdql, fileName, gr):
        """ Экспорт данных в CSV файл на базе PDQL запроса """
        token = self.queryPDQLbyGroup(pdql, gr)
        url = "https://" + self.ptvm_host + ":" + str(self.ptvm_front_port) + "/api/assets_temporal_readmodel/v1/assets_grid/export?pdqlToken=" + token
        print('Using token: ', token)
        limit = True
        print('Start :', datetime.datetime.now())
        while limit:
            try:
                r = requests.get(url, headers=self.authHeader, proxies=proxies, verify=False)
                print(r.status_code)
            except:
                print('Waiting :', datetime.datetime.now())
                time.sleep(60)  # sleep 1 minute
            else:
                if r.status_code == 404:
                    print('Waiting :', datetime.datetime.now())
                    time.sleep(60)  # sleep 1 minute
                else:
                    limit = False
                    open(fileName, 'wb').write(r.content)
                    print('Done! :', datetime.datetime.now())

    def removeAssets(self, ids):
        """ удаление ассетов по массиву ID"""
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/assets_processing/v1/asset_operations/removeAssets"
        data = {"assetsIds": ids}
        r = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

    def getLastScanJob(self, scanId, limit=1000):
        """ получение последней задачи по идентификатору скана"""
        details = None
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/scanning/v2/scanner_tasks/" + scanId + "/runs?limit=" + str(
            limit) + "&withErrors=false"
        response = requests.get(url, headers=self.authHeader, verify=False)
        response = response.json()
        details = response["items"][0]
        return details

    def getScanJobs(self, scanId, errorStatus, status, limit=5000):
        """ получение результатов скана """
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/scanning/v2/runs/" + scanId + "/jobs?errorStatus=" + errorStatus + "&limit=" + str(
            limit) + "&orderby=startedAt+desc&status=" + status
        response = requests.get(url, headers=self.authHeader, verify=False)
        response = response.json()
        records = response["items"]
        return records

    def getJobDetails(self, jobId):
        """ Полуение журнала подзадачи"""
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/scanning/v2/jobs/" + jobId + "/job_errors?limit=50&offset=0&orderBy=occurredAt+desc"
        response = requests.get(url, headers=self.authHeader, verify=False)
        response = response.json()
        records = response["items"]
        return records

    def getScanWithFaildAuth(self, taskId):
        """ Полуение хостов, на которых не прошла аутентфикация"""
        result = []
        scanJob = self.getLastScanJob(taskId)
        if scanJob != None:
            scanId = scanJob["id"]
            jobCount = scanJob["jobCount"]
            scanJobs = self.getScanJobs(scanId, "fail", "finished", jobCount + 30)
            for s in scanJobs:
                target = s["targets"][0]
                jobs = self.getJobDetails(s["id"])
                for j in jobs:
                    if j["type"] in ["Transports.SSH.PKIAuthError", "Transports.DisconnectionError",
                                     "Transports.LoginFailedError"]:
                        result.append(target)
                        break

        return result

    def getAssetDetails(self, assetId):
        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/assets_processing/v2/assets_input/assets/" + assetId
        response = requests.get(url, headers=self.authHeader, verify=False)
        respData = response.json()
        return respData

    def addAssetTag(self, assetId, tagName, tagValue):
        respData = self.getAssetDetails(assetId)
        reqdata = self._buildUpdateAssetDetails(assetId)

    def updateAssetDetails(self, assetId, dataToUpdate):
        """dataToUpdate - dict - ключ значение"""
        respData = self.getAssetDetails(assetId)
        reqData = {"softs": {"added": [], "changed": [], "removed": []}, "noTtl": "true", "scanningIntervals": {},
                   "key": {"properties": []}, "os": {"properties": {}}}

        props = respData["os"]["properties"]
        newProps = []
        for p in props:
            name = p["name"]
            newP = {}
            newP["name"] = name
            if name == "(Core.Host).UF_Tag":
                oldtags = set()
                newTagsSet = {}
                if p["value"] != None:
                    oldtags = set(p["value"].split(" "))
                if "addtags" in dataToUpdate:
                    newTagsSet = oldtags.union(set(dataToUpdate["addtags"].split(" ")))
                if "removetags" in dataToUpdate:
                    newTagsSet = oldtags - (set(dataToUpdate["removetags"].split(" ")))
                if "tags" in dataToUpdate:
                    newTagsSet = set(dataToUpdate["tags"].split(" "))
                newTags = " ".join(list(newTagsSet))
                newP["value"] = newTags
                print("!!!TAG " + str(list(newTagsSet)))
            elif name in dataToUpdate:
                newP["value"] = dataToUpdate[name]
            else:
                newP["value"] = p["value"]
            newProps.append(newP)

        reqData["os"]["properties"] = newProps
        reqData["os"]["ports"] = respData["os"]["ports"]
        if "id" in respData["os"]:
            reqData["os"]["id"] = respData["os"]["id"]
        key = respData["key"]
        for k in key:
            if k["name"] == "hostname" and len(k["values"]) == 0:
                print("WARNING HOSTNAME IS NULL")
                k["values"] = [respData["os"]["ports"][0]["ip"]]
        reqData["key"]["properties"] = key

        url = "https://" + self.ptvm_host + ":" + str(
            self.ptvm_front_port) + "/api/assets_processing/v2/assets_input/assets/" + assetId
        # print(json.dumps(reqData))
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}
        response = requests.put(url, data=json.dumps(reqData), headers=headers, verify=False)

        # print(response.status_code)




