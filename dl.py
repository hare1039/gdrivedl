# -*- coding: utf-8 -*-
import atexit
import sys
import argparse
import os
import getpass
import time
import signal
import subprocess
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
    abp = abs_path(directory, filename)
    return Path(abp).is_file()

def stop_waiting(signum, frame):
    raise Exception("End of time")

def wait_dl(directory, filename):
    if ".txt" in filename:
        signal.alarm(10)

    # wait 10 sec for empty file creation
    created = False
    for timecount in range(int(10 / 0.05)):
        if Path(abs_path(directory, filename)).is_file():
            created = True
            break
        time.sleep(0.05)
    if not created:
        raise Exception("Download file creation end of time")

    while int(os.path.getsize(abs_path(directory, filename))) == 0:
        time.sleep(0.5)
        if not Path(abs_path(directory, filename) + ".part").is_file():
            break;
    time.sleep(5)

def check_error(cmd):
    if cmd == "":
        return
    return_code = subprocess.call(args.t, shell=True)
    if return_code != 0:
        print("[ERROR] terminator return non 0; exit;")
        sys.exit(return_code)

def cleanup(driver):
    driver.quit()

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-d", nargs="?", help="download directory, default: ${PWD}")
    p.add_argument("-s", nargs="?", help="selenium driver host, default: http://127.0.0.1:4444/wd/hub")
    p.add_argument("-t", nargs="?", help="terminate if this command return non zero, default: ''")
    p.add_argument("url", nargs="*")
    args = p.parse_args()

    if not args.d:
        args.d = os.getcwd()
    if not args.url:
        assert False, "[ERROR] Give me a link"
    if not args.s:
        args.s = "http://127.0.0.1:4444/wd/hub"

    check_error(args.t)

    profile = webdriver.FirefoxProfile()
    profile.set_preference("intl.accept_languages", "zh_TW.UTF-8")
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", args.d)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/plain;text/html;text/css;text/javascript;image/gif;image/png;image/jpeg;image/bmp;image/webp;video/webm;video/ogg;audio/midi;audio/mpeg;audio/webm;audio/ogg;audio/wav;video/mp4;application/octet-stream;application/mp4;video/x-webm;video/x-sgi-movie;video/x-mpeg;video/mpg;video/quicktime;video/mpeg4;video/x-matroska")

    driver = webdriver.Remote (
        command_executor=args.s,
        desired_capabilities=DesiredCapabilities.FIREFOX,
        browser_profile=profile
    )
    atexit.register(cleanup, driver)
    signal.signal(signal.SIGALRM, stop_waiting)

    for url in args.url:
        driver.get(url)
        dl_list = driver.find_elements(By.XPATH, "//*[@data-target='download']")
        for ii in dl_list:
            check_error(args.t)
            # press escape 3 times so the page will on select page
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

            ActionChains(driver).click(ii.find_element(By.XPATH, "..")).perform()
            ActionChains(driver).move_by_offset(10, 10).perform()

            filename_element = driver.find_element(By.CSS_SELECTOR, ".a-b-K-T")
            ActionChains(driver).click(filename_element).perform()
            filename = filename_element.text
            ActionChains(driver).send_keys(Keys.ESCAPE).perform()

            if not should_skip(args.d, filename):
                # download part
                tries = 0
                while tries < 3:
                    check_error(args.t)
                    ActionChains(driver).click(ii).perform()
                    try:
                        element_present = EC.presence_of_element_located((By.XPATH, "//button[@name='ok' and @tabindex='0']"))
                        WebDriverWait(driver, 5).until(element_present)
                        
                        driver.find_element(By.XPATH, "//button[@name='ok' and @tabindex='0']").click()
                    except TimeoutException:
                        print("[WARNING] no ok button")
                        
                    try:
                        wait_dl(args.d, filename)
                    except Exception as e:
                        print("[ERROR] download expired. Why: " + repr(e) + ". Tries #" + str(tries))
                        ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        tries += 1
                        if tries < 3:
                            continue
                        else:
                            print("[ERROR] giving up on tries #" + str(tries))
                            break
                    if filename != "": 
                        print(filename)
                    break
            else:
                print("[ERROR] skipping download on " + filename)
