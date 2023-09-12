import os
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from telethon import events, TelegramClient

load_dotenv()

api_id = int(os.getenv('api_id'))
api_hash = os.getenv('api_hash')
client = TelegramClient('anon', api_id, api_hash)


@client.on(events.NewMessage(pattern='^[A-Z0-9]{8}$'))
async def message_handler(event):
    text = event.message.text
    check_handle_message(text)


def show_result(data):
    print(data['code'], data['amount'], data['coin'])


def check_box(code):
    try:
        btn = WebDriverWait(driver, timeout=3).until(
            ec.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[1]/div/div/button'))
        )
        open_btn = driver.find_element(By.XPATH, value='/html/body/div[4]/div[1]/div/div/button').click()
        time.sleep(3)
        amount = driver.find_element(By.XPATH, value='/html/body/div[4]/div[1]/div/div/div[4]/div/div/div[1]').text
        coin = driver.find_element(By.XPATH, value='/html/body/div[4]/div[1]/div/div/div[4]/div/div/div[2]').text
        print(code, amount, coin)
        driver.refresh()
        driver.implicitly_wait(3)
    except:
        print('Криптобокс закончился или уже использован')
        driver.refresh()
        driver.implicitly_wait(3)


def open_box(code: str):
    all_codes.append(code)
    print(last_codes)
    if len(last_codes) == 1000:
        last_codes.clear()
    if code in last_codes:
        print(f'skip: {code}')
    else:
        input_code_lable = driver.find_element(by=By.XPATH,
                                               value='/html/body/div[1]/div[1]/div[2]/div[2]/div/div[1]/div[2]'
                                                     '/div/div[2]/input')
        paste_code = input_code_lable.send_keys(code)

        get_box_btn = (driver.find_element(by=By.XPATH,
                                           value='/html/body/div[1]/div[1]/div[2]/div[2]/div/div[1]/div[2]'
                                                 '/button').click())

        last_codes.append(code)

        check_box(code)


def check_handle_message(message: str) -> None:
    if len(message) > 8:
        message = message.replace('*', '').replace('`', '')
    open_box(message)


def start_browser(value: str):
    url = f'http://localhost:3001/v1.0/browser_profiles/{value}/start?automation=1'
    response = requests.get(url)
    print(response.status_code)
    port = response.json()['automation']['port']

    chromedriver_path = Service('chromedriver/chromedriver-windows-x64.exe')
    options = webdriver.ChromeOptions()
    options.debugger_address = f'127.0.0.1:{port}'
    # options.add_argument('--headless')

    browser = webdriver.Chrome(service=chromedriver_path, options=options)
    # driver.set_window_position(x=1099, y=0)
    return browser


async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == "__main__":
    all_codes = []
    last_codes = []
    profile_id = os.getenv('pofile_id')
    driver = start_browser(profile_id)
    with client:
        client.loop.run_until_complete(main())
