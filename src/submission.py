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


def collect_accepted_submissions(submissions):
    # IDで昇順ソートすると古い順になる
    sorted_data = sorted(submissions, key=lambda x: x['id'])
    submits = {}  # 各問題ごとに最新の提出に更新する
    for data in sorted_data:
        # ACだった提出だけ対象
        if data["result"] != "AC":
            continue
        submits[data["problem_id"]] = data

    # コンテストごとにまとめる
    result = {}
    for sub in submits.values():
        if not sub["contest_id"] in result:
            result[sub["contest_id"]] = []
        result[sub["contest_id"]].append(sub)

    return result


class Submissions:

    def __init__(self):
        self.submissions = get_submission_data()
        self.newest_submits = collect_accepted_submissions(self.submissions)
        for contest in self.newest_submits:
            path = PROJECT_PATH + ROOT + contest
            os.makedirs(path, exist_ok=True)

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)
