from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import requests
import urllib.parse
import time
import os
from dotenv import load_dotenv
from functools import reduce

# Load environment variables
load_dotenv()

# Const
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MY_ID = os.getenv("MY_TELEGRAM_ID")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
UPDATE_URL = f"{BASE_URL}/getUpdates"

# URL
URL = "https://internship.cse.hcmut.edu.vn"

# Set up webdriver
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Helper function    
def getCompanyName(logo):
    try:
        logo.click()
        time.sleep(3)
        info = driver.find_elements(By.CSS_SELECTOR, ".modal.fade")[1]
        name = info.find_element(By.CSS_SELECTOR, "h4").text
        info.find_element(By.CSS_SELECTOR, "button.close").click()
        return name
    except Exception as e:
        pass

def getChatIDs():
    try:
        response = requests.get(UPDATE_URL)
        data = response.json().get("result", [])
        CHAT_ID = set([str(item.get("message", {}).get("chat", {}).get("id", MY_ID)) for item in data])
        return CHAT_ID
    except Exception as e:
        pass

def sendNotification(urlParams):
    try:
        CHAT_ID = getChatIDs()
        for ID in CHAT_ID:
            requests.get(f"{BASE_URL}/sendMessage?chat_id={ID}&{urlParams}")
    except Exception as e:
        pass

def sendDonotHaveNewCompanyNotification():
    try:
        params = {
            "text": "❌ Chưa có công ty nào được thêm vào."
        }
        urlParams = urllib.parse.urlencode(params)
        requests.get(f"{BASE_URL}/sendMessage?chat_id={MY_ID}&{urlParams}")
    except Exception as e:
        pass

# Get numbers of old companys
try:
    f = open("numbers.txt", "r")
    numbers = int(f.read())
    f.close()
except FileNotFoundError:
    numbers = 0

# Open website
try:
    driver.get(URL)
    time.sleep(2)
    logos = driver.find_elements(By.CSS_SELECTOR, "div > div.logo-box")
    if len(logos) != numbers:
        names = list(map(getCompanyName, logos))
        print(f"Hiện tại đang có {len(names)} công ty", names)
    else:
        names = []
except Exception as e:
    names = []

if len(logos) != numbers:
    # Write numbers of companys to file numbers.txt
    with open("numbers.txt", "w") as f:
        f.write(f"{len(names)}")

    # Read names of old companys
    try:
        f = open("company.txt", "r")
        oldCompanys = reduce(lambda acc, curr: acc + [curr], f.read().split("\n"), [])
        f.close()
    except FileNotFoundError:
        oldCompanys = []

    # Filter new companys
    newCompanys = list(filter(lambda name: name not in oldCompanys, names))
    if len(newCompanys) > 0:
        params = {
            "text": "\n".join([f"📢 Có {len(newCompanys)} công ty mới được thêm vào:"] + list(map(lambda item: f"✅ {item}",newCompanys)))
        }
        urlParams = urllib.parse.urlencode(params)

        # Append new companys to file
        with open("company.txt", "a") as f:
            for name in newCompanys:
                f.write(f"{name}\n")

        sendNotification(urlParams)
else:
    sendDonotHaveNewCompanyNotification()

driver.quit()
