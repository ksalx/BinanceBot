import os
import time

import requests
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from telethon import events, TelegramClient

load_dotenv()

api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')
client = TelegramClient('anon', api_id, api_hash)

all_codes = []
last_codes = []


def simulate_browser(driver, code: str):
    all_codes.append(code)
    print('All Codes', all_codes)
    if len(last_codes) == 1000:
        last_codes.clear()
    print(last_codes)
    print(code)
    print(driver.get_window_size())
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

        time.sleep(1.8)
        try:
            open_box_btn = driver.find_element(by=By.XPATH, value='/html/body/div[8]/div[1]/div/div/button/div').text
            if open_box_btn == 'Открыть':
                open_box_btn = driver.find_element(by=By.XPATH,
                                                   value='/html/body/div[8]/div[1]/div/div/button/div').click()

                driver.implicitly_wait(3)
                open_box_btn.click()
                time.sleep(3)
                balance = driver.find_element(by=By.XPATH,
                                              value='/html/body/div[8]/div/div[3]/div[1]/div[2]/div[2]').text
                print(code, balance)
                last_codes.append(code)
                driver.implicitly_wait(3)
                driver.refresh()
                driver.implicitly_wait(3)
            else:
                print('Бокс пустой')
                last_codes.append(code)
                driver.refresh()
                driver.implicitly_wait(3)
        except Exception as E:
            print('Закончились')
            last_codes.append(code)
            driver.refresh()
            driver.implicitly_wait(3)


def check_handle_message(message: str, driver) -> None:
    if len(message) > 8:
        message = message.replace('*', '').replace('`', '')
    simulate_browser(driver, message)


@client.on(events.NewMessage(pattern='^[A-Z0-9]{8}$'))
async def message_handler(event):
    text = event.message.text
    check_handle_message(text, driver)


def start_browser(profile_id: str):
    url = f'http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1'
    response = requests.get(url)
    print(response.status_code)
    port = response.json()['automation']['port']

    chromedriver_path = Service('chromedriver/chromedriver-windows-x64.exe')
    options = webdriver.ChromeOptions()
    options.debugger_address = f'127.0.0.1:{port}'
    # options.add_argument('--headless')

    driver = webdriver.Chrome(service=chromedriver_path, options=options)
    driver.set_window_position(x=1099, y=0)
    return driver


async def main():
    await client.start()
    await client.run_until_disconnected()


if __name__ == "__main__":
    profile_id = '149638751'
    driver = start_browser(profile_id)
    with client:
        client.loop.run_until_complete(main())
