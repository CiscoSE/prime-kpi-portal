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
"""

Main access for environmental variables. You will need to restart the app to apply those changes

"""

import os

__author__ = "Santiago Flores Kanter (sfloresk@cisco.com)"


def get_db_host():
    return os.getenv("DB_HOST", "")


def get_db_port():
    return os.getenv("DB_PORT", "")


def get_db_name():
    return os.getenv("DB_NAME", "")


def get_db_password():
    return os.getenv("DB_PASSWORD", "")


def get_db_user():
    return os.getenv("DB_USER", "")

def get_prime_url():
    return os.getenv("PRIME_URL", "")

def get_prime_username():
    return os.getenv("PRIME_USER", "")

def get_prime_password():
    return os.getenv("PRIME_PASSWORD", "")