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
from web_ui.models import *

"""******** Generics ********"""


def save_entity(entity):
    entity.save()


"""******** AP Metrics ********"""


def getAPMetrics(**db_filter):
    return APMetrics.objects.all().filter(**db_filter)


def getFirstAPMetrics(**db_filters):
    apMetrics = APMetrics.objects.all().filter(**db_filters)
    if len(apMetrics) == 0:
        return None
    return apMetrics[0]


def addAPMetrics(**kwargs):
    return APMetrics(**kwargs).save()


def deleteAPMetrics(name):
    ap_list = APMetrics.objects.filter(Name=name)
    if len(ap_list) > 0:
        ap_list[0].delete()


def addCollection(**kwargs):
    return Collection(**kwargs).save()


def getLastCollection():
    return Collection.objects.latest('startTime')


def addSettings(**kwargs):
    return Settings(**kwargs).save()


def getFirstSettings(**db_filters):
    settings = Settings.objects.all().filter(**db_filters)
    if len(settings) == 0:
        return None
    return settings[0]
