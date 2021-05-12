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


class Submissions:

    def __init__(self):
        self.submissions = self.get_submission_data()
        self.newest_submits = self.collect_accepted_submissions(self.submissions)
        for contest in self.newest_submits:
            path = PROJECT_PATH + ROOT + contest
            os.makedirs(path, exist_ok=True)

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)

