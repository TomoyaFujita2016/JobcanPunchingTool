import json
import time
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from os.path import join, dirname
import os
from dotenv import load_dotenv
import requests


dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")
TOKEN_LINE_API = os.environ.get("TOKEN_LINE_API")
LINEID = os.environ.get("LINEID")


def line_notification(msg):
    REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/push"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN_LINE_API}",
    }
    payload = {
        "to": LINEID,
        "messages": [{"type": "text", "text": msg}],
    }
    requests.post(REPLY_ENDPOINT, headers=header, data=json.dumps(payload))


class Jobcan:
    URL_LOGIN = "https://id.jobcan.jp/users/sign_in?app_key=atd"
    URL_PUNCHING = "https://ssl.jobcan.jp/employee"

    def __init__(self, email, password, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=self.options
        )
        self.login(email, password)

    def __del__(self):
        self.driver.quit()

    def login(self, email, password):
        self.driver.get(Jobcan.URL_LOGIN)
        self.driver.find_element_by_name("user[email]").send_keys(EMAIL)
        self.driver.find_element_by_name("user[password]").send_keys(PASSWORD)
        self.driver.find_element_by_name("commit").click()
        time.sleep(1)

    def punching(self):
        self.driver.get(Jobcan.URL_PUNCHING)
        status_before = self.driver.find_element_by_id("working_status").text
        self.driver.find_element_by_name("adit_item").click()
        time.sleep(1)
        status_after = self.driver.find_element_by_id("working_status").text
        msg = f"Status: {status_before} → {status_after}"
        line_notification(msg)


def main():
    try:
        jobcan = Jobcan(EMAIL, PASSWORD, headless=True)
        jobcan.punching()
    except Exception:
        line_notification(str(traceback.format_exc()))


if __name__ == "__main__":
    main()
