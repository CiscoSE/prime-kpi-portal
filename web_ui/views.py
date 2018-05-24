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
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import traceback
from django.http import HttpResponse
import threading
from .controllers.prime import PrimeController
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from web_ui.controllers import db
from web_ui import envs


# ====================>>>>>>>> Utils <<<<<<<<====================
class ModelsJSONResponse(HttpResponse):
    """
    An HttpResponse that renders django models its content into JSON.
    """

    def __init__(self, data, **kwargs):
        jsonData = serializers.serialize("json", data)
        #        content = JSONRenderer().render(jsonData)
        kwargs['content_type'] = 'application/json'
        super(ModelsJSONResponse, self).__init__(jsonData, **kwargs)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


# ====================>>>>>>>> Templates <<<<<<<<====================

def index(request):
    return render(request, 'web_app/index.html')


def home(request):
    return render(request, 'web_app/home.html')


def ap_metrics(request):
    return render(request, 'web_app/ap_metrics.html')


def settings(request):
    return render(request, 'web_app/settings.html')


# ====================>>>>>>>> APIs <<<<<<<<====================

@csrf_exempt
def api_collection(request):
    """
    Starts (POST) or Retrieve (GET) a collection
    :param request:
    :return:
    """
    if request.method == 'POST':
        try:
            # Check if collection is running
            for thread in threading.enumerate():
                if thread.name == 'collection':
                    if thread.isAlive():
                        raise Exception("Collection is already in process")

            # Do the collection
            primeController = PrimeController()
            threading.Thread(
                name=str("collection"),
                target=primeController.startCollection
            ).start()
            return JSONResponse("Ok")
        except Exception as e:
            print(traceback.print_exc())
            # return the error to web client
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
    elif request.method == 'GET':
        try:
            primeController = PrimeController()
            APMetricsList = primeController.getLastCollection()
            return ModelsJSONResponse(APMetricsList)
        except Exception as e:
            print(traceback.print_exc())
            # return the error to web client
            return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
    else:
        return JSONResponse("Bad request. " + request.method + " is not supported", status=400)


@csrf_exempt
def api_collection_status(request):
    """
    (GET) Retrieve the status of the collection thread. Starts the collection Daemon has not been started
    :param request:
    :return:
    """
    if request.method == 'GET':
        present = False
        # Starts the daemon if not present
        for thread in threading.enumerate():
            if thread.name == 'collectionDaemon':
                if thread.isAlive():
                    present = True

        if not present:
            primeController = PrimeController()
            threading.Thread(
                name=str("collectionDaemon"),
                target=primeController.runCollectionTimer
            ).start()

        for thread in threading.enumerate():
            if thread.name == 'collection':
                if thread.isAlive():
                    return JSONResponse({'status': 'alive'})
        return JSONResponse({'status': 'dead'})
    else:
        return JSONResponse("Bad request. " + request.method + " is not supported", status=400)


@csrf_exempt
def api_settings(request):
    """
    Retreive (GET) or change (POST) the settings for this app.
    :param request:
    :return:
    """
    try:
        if request.method == 'GET':
            primeController = PrimeController()
            APMetricsList = primeController.getLastCollection()
            lastCollectionTime = "never"

            dbSettings = db.getFirstSettings()
            if dbSettings == None:
                db.addSettings(collectionInterval=12)
            dbSettings = db.getFirstSettings()

            if len(APMetricsList) > 0:
                lastCollectionTime = APMetricsList[0].collection.startTime

            return JSONResponse({
                'collectionInterval': dbSettings.collectionInterval,
                'lastCollectionTime': lastCollectionTime
            })
        elif request.method == 'POST':
            payload = json.loads(request.body)
            dbSettings = db.getFirstSettings()
            newInterval = int(payload["collectionInterval"])
            if newInterval < 1:
                raise Exception("Collection interval must be equal or greater than 1")
            if dbSettings == None:
                db.addSettings(collectionInterval=newInterval)
            else:
                dbSettings.collectionInterval = newInterval
                dbSettings.save()
            return JSONResponse("Ok")
        else:
            return JSONResponse("Bad request. " + request.method + " is not supported", status=400)
    except Exception as e:
        print(traceback.print_exc())
        # return the error to web client
        return JSONResponse({'error': e.__class__.__name__, 'message': str(e)}, status=500)
