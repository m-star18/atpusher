import datetime
import html
import os
import re
import subprocess

import git
import requests
from selenium import webdriver
import chromedriver_binary

from const import (
    USER_ID,
    API_PATH,
    ROOT,
    PROJECT_PATH,
)


def get_submission_data():
    api_url = API_PATH + USER_ID
    response = requests.get(api_url)
    json_data = response.json()

    return json_data
