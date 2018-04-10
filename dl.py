# -*- coding: utf-8 -*-
import sys
import argparse
import os
import getpass
import time
from pathlib import Path
from pprint import pprint
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def abs_path(directory, filename):
    if directory[-1] != "/":
        directory += "/"
    return directory + filename

def should_skip(directory, filename):
    target = Path(abs_path(directory, filename))
    return target.is_file()

def wait_dl(directory, filename):
    while True:
        if Path(abs_path(directory, filename)).is_file():
            break
        time.sleep(0.05)
    while int(os.path.getsize(abs_path(directory, filename))) == 0:
        time.sleep(0.5)
        if not Path(abs_path(directory, filename) + ".part").is_file():
            break;
    time.sleep(5)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-d", nargs="?", help="download directory, default: ${PWD}")
    p.add_argument("-s", nargs="?", help="selenium driver host, default: http://127.0.0.1:4444/wd/hub")
    p.add_argument("url", nargs="*")
    args = p.parse_args()


    if not args.d:
        args.d = os.getcwd()
    if not args.url:
        assert False, "[ERROR] Give me a link"
    if not args.s:
        args.s = "http://127.0.0.1:4444/wd/hub"
    profile = webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "zh_TW.UTF-8")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", args.d)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain;text/html;text/css;text/javascript;image/gif;image/png;image/jpeg;image/bmp;image/webp;video/webm;video/ogg;audio/midi;audio/mpeg;audio/webm;audio/ogg;audio/wav;video/mp4;application/octet-stream;application/mp4")

    driver = webdriver.Remote (
        command_executor=args.s,
        desired_capabilities=DesiredCapabilities.FIREFOX,
        browser_profile=profile
    )

    for url in args.url:
        driver.get(url)
        dl_list = driver.find_elements(By.XPATH, "//*[@data-target='download']")
        for ii in dl_list:
            ActionChains(driver).click(ii.find_element(By.XPATH, "..")).perform()
            ActionChains(driver).move_by_offset(10, 10).perform()

            filename_element = driver.find_element(By.CSS_SELECTOR, ".a-b-K-T")
            ActionChains(driver).click(filename_element).perform()
            filename = filename_element.text
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

            if not should_skip(args.d, filename):
                # download part
                ActionChains(driver).click(ii).perform()
                try:
                    element_present = EC.presence_of_element_located((By.XPATH, "//button[@name='ok' and @tabindex='0']"))
                    WebDriverWait(driver, 5).until(element_present)
                    
                    driver.find_element(By.XPATH, "//button[@name='ok' and @tabindex='0']").click()
                except ElementNotInteractableException:
                    print("[WARNING] no ok button")
                except TimeoutException:
                    print("[WARNING] waiting expired")

                wait_dl(args.d, filename)
                print(filename)
            else:
                print("[ERROR] skip download of " + filename)

    driver.quit()
