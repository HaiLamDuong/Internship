import os
import urllib.parse
from functools import reduce

import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Const
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MY_ID = os.getenv("MY_TELEGRAM_ID")
FERNET_KEY = os.getenv("FERNET_KEY")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
UPDATE_URL = f"{BASE_URL}/getUpdates"

# URL
URL = "https://internship.cse.hcmut.edu.vn/home/company/all"

# Create a cipher object
cipher = Fernet(FERNET_KEY)


def functionRunTime(func):
    def innerFunction(*args, **kargs):
        import time

        start = time.time()
        res = func(*args, **kargs)
        end = time.time()
        print(f"Run time of {func.__name__} is: {end - start}")
        return res

    return innerFunction


@functionRunTime
def getChatIDs():
    try:
        # Get ids from ids.txt file
        try:
            f = open("ids.txt", "r")
            oldChatIDs = reduce(
                lambda acc, curr: acc + [str(cipher.decrypt(curr.encode()).decode())],
                f.read().split("\n")[:-1],
                [],
            )
            f.close()
        except Exception as e:
            print("Error in reading ids.txt:", e)
            oldChatIDs = []

        # Get ids from telegram bot
        response = requests.get(UPDATE_URL)
        data = response.json().get("result", [])
        chatIDs = set(
            [
                str(item.get("message", {}).get("chat", {}).get("id", MY_ID))
                for item in data
            ]
        )
        newChatIDs = list(filter(lambda ID: ID not in oldChatIDs, chatIDs))

        if len(newChatIDs) == 0:
            return oldChatIDs

        # Append new ids to file ids.txt
        with open("ids.txt", "a") as f:
            for ID in newChatIDs:
                f.write(f"{cipher.encrypt(ID.encode()).decode()}\n")

        return newChatIDs + oldChatIDs
    except Exception as e:
        print("Error in getChatIDs:", e)
        return [MY_ID]


@functionRunTime
def sendNotification(urlParams):
    try:
        chatIDs = getChatIDs()
        for ID in chatIDs:
            requests.get(f"{BASE_URL}/sendMessage?chat_id={ID}&{urlParams}")
    except Exception as e:
        print("Error in sendNotification:", e)


@functionRunTime
def sendDonotHaveNewCompanyNotification():
    try:
        params = {"text": "❌ Chưa có công ty nào được thêm vào."}
        urlParams = urllib.parse.urlencode(params)
        requests.get(f"{BASE_URL}/sendMessage?chat_id={MY_ID}&{urlParams}")
    except Exception as e:
        print("Error in sendDonotHaveNewCompanyNotification:", e)


@functionRunTime
def getNumbersOfOldCompanys():
    # Get numbers of old companys
    try:
        f = open("numbers.txt", "r")
        numbers = int(f.read())
        f.close()
    except FileNotFoundError:
        numbers = 0
    finally:
        return numbers


@functionRunTime
def main():
    numbers = getNumbersOfOldCompanys()

    try:
        response = requests.get(URL)
        data = response.json().get("items", [])
    except Exception as e:
        print("Error in main:", e)
        data = []

    if len(data) and len(data) != numbers:
        infos = reduce(
            lambda acc, curr: acc
            + [(curr.get("_id", None), curr.get("fullname", "None"))],
            data,
            [],
        )

        # Write numbers of companys to file numbers.txt
        with open("numbers.txt", "w") as f:
            f.write(f"{len(infos)}")

        # Read names of old companys
        try:
            f = open("company.txt", "r")
            oldCompanys = reduce(
                lambda acc, curr: acc + [curr], f.read().split("\n")[:-1], []
            )
            f.close()
        except FileNotFoundError:
            oldCompanys = []

        # Filter new companys
        newCompanys = list(filter(lambda name: name not in oldCompanys, infos))
        newCompanys = list(map(lambda info: info[1], newCompanys))
        if len(newCompanys) > 0:
            params = {
                "text": "\n".join(
                    [f"📢 Có {len(newCompanys)} công ty mới được thêm vào:"]
                    + list(map(lambda item: f"✅ {item}", newCompanys))
                )
            }
            urlParams = urllib.parse.urlencode(params)

            # Append new companys to file
            with open("company.txt", "a") as f:
                for id, name in infos:
                    f.write(f"{id}\n")

            sendNotification(urlParams)
    else:
        # sendDonotHaveNewCompanyNotification()
        print("❌ Chưa có công ty nào được thêm vào.")


if __name__ == "__main__":
    main()
