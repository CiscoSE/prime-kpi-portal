"""
Copyright (c) 2018 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""
from jinja2 import Environment
from jinja2 import FileSystemLoader
import os
import requests
import json
from . import db
import datetime
import time
import threading
from .. import envs
import base64

DIR_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
JSON_TEMPLATES = Environment(loader=FileSystemLoader(DIR_PATH + '/json_templates'))

# Disable https warnings
requests.packages.urllib3.disable_warnings()


class PrimeController:
    url = envs.get_prime_url()

    def makeCall(self, p_url, method, data=""):
        """
        Single exit point for all APIs calls for Prime Infrastructure
        :param p_url:
        :param method:
        :param data:
        :return:
        """
        credentials = envs.get_prime_username() + ":" + envs.get_prime_password()

        headers = {
            'Authorization': "Basic " + base64.b64encode(bytes(credentials, "utf-8")).decode("utf-8")
        }
        if method == "POST":
            response = requests.post(self.url + p_url, data=data, headers=headers, verify=False)
        elif method == "GET":
            response = requests.get(self.url + p_url, headers=headers, verify=False)
        else:
            raise Exception("Method " + method + " not supported by this controller")
        if 199 > response.status_code > 300:
            errorMessage = json.loads(response.text)["errorDocument"]["message"]
            raise Exception("Error: status code" + str(response.status_code) + " - " + errorMessage)
        return response

    def getAPs(self):
        """
        Return a list of access points
        :return:
        """
        pURL = "/webacs/api/v3/data/AccessPointDetails.json"
        response = self.makeCall(p_url=pURL, method="GET")
        print(response.text)
        APs = json.loads(response.text)["queryResponse"]["entityId"]
        return APs

    def getAPDetail(self, apDetailId):
        """
        Return detail data of an specific access point
        :param apDetailId:
        :return:
        """
        pURL = "/webacs/api/v3/data/AccessPointDetails/" + apDetailId + ".json"
        response = json.loads(self.makeCall(p_url=pURL, method="GET").text)
        APDetail = None
        if len(response["queryResponse"]["entity"]) > 0:
            APDetail = json.loads(self.makeCall(p_url=pURL, method="GET").text)["queryResponse"]["entity"][0]
        return APDetail

    def getClientCount(self):
        """
        Returns the sum of all 2.4G and 5G clients
        :return:
        """
        fiveGCount = 0
        twoPointFourGCount = 0
        # Get APs
        APs = self.getAPs()
        for AP in APs:
            apDetail = self.getAPDetail(apDetailId=AP["$"])
            print(apDetail)
            fiveGCount += int(apDetail["accessPointDetailsDTO"]["clientCount_5GHz"])
            twoPointFourGCount += int(apDetail["accessPointDetailsDTO"]["clientCount_2_4GHz"])
            # Return details
        return {
            "fiveGClients": fiveGCount,
            "twoPointFourGClients": twoPointFourGCount
        }

    def getRFLoadStats(self):
        """
         Return the RF Load stats list. Mainly for ChannelUtilization and PoorCoverageClients
        """
        result = []
        pURL = "/webacs/api/v3/data/RFLoadStats.json"
        rfLoadStatsList = json.loads(self.makeCall(p_url=pURL, method="GET").text)["queryResponse"]["entityId"]
        for rfLoadStat in rfLoadStatsList:
            pURL = rfLoadStat["@url"].replace(self.url, "") + ".json"
            response = json.loads(self.makeCall(p_url=pURL, method="GET").text)
            if len(response) > 0:
                rfLoadDetail = response["queryResponse"]["entity"][0]
                result.append(rfLoadDetail)
        return result

    def getRFStats(self):
        """
        Gets RF Stats data. Mainly for PowerOutput
        :return:
        """
        result = []
        pURL = "/webacs/api/v3/data/RFStats.json"
        rfStatsList = json.loads(self.makeCall(p_url=pURL, method="GET").text)["queryResponse"]["entityId"]
        for rfStat in rfStatsList:
            pURL = rfStat["@url"].replace(self.url, "") + ".json"
            response = json.loads(self.makeCall(p_url=pURL, method="GET").text)
            if len(response) > 0:
                rfStatDetail = response["queryResponse"]["entity"][0]
                result.append(rfStatDetail)
        return result

    def getRFCounters(self):
        """
        Gets RF Counters data. Mainly for multipleRetryCount, retryCount, rxFragmentCount and txFragmentCount
        :return:
        """
        result = []
        pURL = "/webacs/api/v3/data/RFCounters.json"
        rfCountersList = json.loads(self.makeCall(p_url=pURL, method="GET").text)["queryResponse"]["entityId"]
        for rfCounter in rfCountersList:
            pURL = rfCounter["@url"].replace(self.url, "") + ".json"
            response = json.loads(self.makeCall(p_url=pURL, method="GET").text)
            if len(response) > 0:
                rfCounterDetail = response["queryResponse"]["entity"][0]
                result.append(rfCounterDetail)
        return result

    def startCollection(self):
        """
        Collects data from Prime and save it to a database
        :return:
        """
        print("Starting collection... ")
        # Access Points
        APs = self.getAPs()
        print("Getting the RF Stats")
        RFLoadStatsList = self.getRFStats()
        print("Getting the RF Counters")
        RFCountList = self.getRFCounters()
        print("Getting the RF Load Stats")
        RFLoadDetailList = self.getRFLoadStats()

        db.addCollection(startTime=datetime.datetime.now())
        collection = db.getLastCollection()

        progress = 0
        print("Adding collection to database... ")
        print("Progress 0%")
        for AP in APs:

            apDetail = self.getAPDetail(apDetailId=AP["$"])
            ChannelUtilization = 0
            PoorCoverageClients = 0
            txPowerOutput = 0
            txFragmentCount = 0
            rxFragmentCount = 0
            retryCount = 0
            multipleRetryCount = 0

            for RFLoadDetail in RFLoadDetailList:
                if RFLoadDetail["rfLoadStatsDTO"]["macAddress"] == apDetail["accessPointDetailsDTO"]["macAddress"]:
                    ChannelUtilization = RFLoadDetail["rfLoadStatsDTO"]["channelUtilization"]
                    PoorCoverageClients = RFLoadDetail["rfLoadStatsDTO"]["poorCoverageClients"]
                    break

            for RFStatsDetail in RFLoadStatsList:
                if RFStatsDetail["rfStatsDTO"]["macAddress"] == apDetail["accessPointDetailsDTO"]["macAddress"]:
                    txPowerOutput = RFStatsDetail["rfStatsDTO"]["txPowerOutput"]
                    break

            for RFCount in RFCountList:
                if RFCount["rfCountersDTO"]["macAddress"] == apDetail["accessPointDetailsDTO"]["macAddress"]:
                    txFragmentCount = RFCount["rfCountersDTO"]["txFragmentCount"]
                    rxFragmentCount = RFCount["rfCountersDTO"]["rxFragmentCount"]
                    retryCount = RFCount["rfCountersDTO"]["retryCount"]
                    multipleRetryCount = RFCount["rfCountersDTO"]["multipleRetryCount"]
                    break

            db.addAPMetrics(collection=collection,
                            name=apDetail["accessPointDetailsDTO"]["name"],
                            fiveGClients=apDetail["accessPointDetailsDTO"]["clientCount_5GHz"],
                            twoGClients=apDetail["accessPointDetailsDTO"]["clientCount_2_4GHz"],
                            channelUtilization=ChannelUtilization,
                            poorCoverageClients=PoorCoverageClients,
                            txPowerOutput=txPowerOutput,
                            txFragmentCount=txFragmentCount,
                            rxFragmentCount=rxFragmentCount,
                            retryCount=retryCount,
                            multipleRetryCount=multipleRetryCount)
            progress += 1
            print("Progress: " + "%.2f" % (progress / len(APs) * 100) + "%")

    def getLastCollection(self):
        collection = db.getLastCollection()
        APMetricsList = db.getAPMetrics(collection=collection)
        return APMetricsList

    def runCollectionTimer(self):
        """
        To be used as a background task. Check the last collection against
        the interval set in the env variables. Will create a collection per that interval
        :param interval: HOURS
        :return:
        """

        # Add default settings in case is the first time this runs
        settings = db.getFirstSettings()
        if settings == None:
            db.addSettings(collectionInterval=12)

        while True:
            # Update the settings
            settings = db.getFirstSettings()
            collect = True
            # Check if a collection is in place (can be triggered manually by the user)
            for thread in threading.enumerate():
                if thread.name == 'collection':
                    if thread.isAlive():
                        collect = False
            # If collect is still true, then check the interval
            if collect:
                lastCollection = self.getLastCollection()
                if len(lastCollection) > 0:
                    lastCollectionTime = lastCollection[0].collection.startTime
                    if (lastCollectionTime + datetime.timedelta(
                            seconds=settings.collectionInterval * 3600)) > datetime.datetime.now(
                        datetime.timezone.utc):
                        collect = False

            # If collect is still true, then do the collection
            if collect:
                threading.Thread(
                    name=str("collection"),
                    target=self.startCollection
                ).start()

            time.sleep(3600)
