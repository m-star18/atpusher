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
    # If you sort by ID in ascending order, the order will be oldest first.
    sorted_data = sorted(submissions, key=lambda x: x['id'])
    submits = {}  # Update to the latest submission for each issue.
    for data in sorted_data:
        # For submissions that were AC only.
        if data["result"] != "AC":
            continue
        submits[data["problem_id"]] = data

    # Organize by contest
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
        self.repo = git.Repo()
        for contest in self.newest_submits:
            path = PROJECT_PATH + ROOT + contest
            os.makedirs(path, exist_ok=True)

        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=self.options)

    def run(self):
        os.chdir(PROJECT_PATH)
        for submissions in self.newest_submits.values():
            for sub in submissions:
                # 問題番号の取得
                problem_num = sub["problem_id"][-1]

                # 古い問題の場合には数字になっているので、アルファベットに戻す
                if problem_num.isdigit():
                    problem_num = chr(int(problem_num) + ord('a') - 1)

                # 作成するファイルへのパス
                path = ROOT + sub["contest_id"] + "/" + problem_num
                # 拡張子の設定（C++, Python, PyPyのみ）
                if "C++" in sub["language"]:
                    path += ".cpp"
                elif "Py" in sub["language"]:
                    path += ".py"

                # 既に提出コードがある場合は取得せず、次の問題の提出を探す
                if os.path.isfile(path):
                    continue

                # 提出ページへアクセス
                sub_url = "https://atcoder.jp/contests/" + sub["contest_id"] + "/submissions/" + str(sub["id"])
                self.driver.get(sub_url)

                # 提出コードの取得
                code = self.driver.find_element_by_id("submission-code")

                # code.text は提出時に含めていない空白が期待に反して含まれてしまう
                # 空白はシンタックスハイライティングによるものであるように見える
                # innerHTML から不要なタグなどを消し、空白が意図通りのテキストを得る
                inner_html = code.get_attribute('innerHTML')
                list_items = re.findall(r'<li[^>]*>.*?</li>', inner_html)
                lines = []
                for line in list_items:
                    line1 = re.sub(r'<[^>]+>', '', line)
                    line2 = re.sub(r'&nbsp;', '', line1)
                    line3 = html.unescape(line2)
                    lines.append(line3 + "\n")
                code_text = ''.join(lines)

                with open(path, 'w') as f:
                    f.write(code_text)

                if "C++" in sub["language"]:
                    subprocess.call(["clang-format", "-i", "-style=file", path])

                dt_now = datetime.datetime.now()
                self.repo.remotes.origin.pull()
                self.repo.git.add("submissions/*")
                self.repo.git.commit("submissions/*", message="add submission: " + dt_now.strftime('%Y/%m/%d %H:%M:%S'))
                self.repo.git.push("origin", "main")
                print(f"Finished process {sub['contest_id']} {problem_num} {sub['language']}, "
                      f"Message...'add submission: {dt_now.strftime('%Y/%m/%d %H:%M:%S')}'")

        self.driver.quit()
