


import threading

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

import logging

logger = logging.getLogger(__name__)

# Docs: https://selenium-python.readthedocs.io/getting-started.html

class Browser:


    def __init__(self):
        logger.info("init")


    def openBrowserThread(self, url):
        thread1 = threading.Thread(target=(lambda: self.openBrowser(url) ))
        thread1.setDaemon(True)
        thread1.start()

    def openBrowser(self, url):
        
        caps = DesiredCapabilities().CHROME
        #caps = DesiredCapabilities().FIREFOX
        #caps["pageLoadStrategy"] = "normal"  #  complete
        #caps["pageLoadStrategy"] = "eager"  #  interactive
        caps["pageLoadStrategy"] = "none"

        # fireFoxOptions = webdriver.FirefoxOptions()
        # fireFoxOptions.add_argument("--start-maximized")
        # fireFoxOptions.add_argument("--disable-infobars")
        # fireFoxOptions.set_preference("dom.webnotifications.enabled", False)
        # driver = webdriver.Firefox(desired_capabilities=caps, firefox_options=fireFoxOptions)

        chrome_options = Options()
        chrome_options.add_argument("--kiosk")
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])

        # More Info: https://github.com/GoogleChrome/chrome-launcher/blob/master/docs/chrome-flags-for-tools.md#--enable-automation
        # "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        #     --disable-hang-monitor
        #     --disable-prompt-on-repost
        #     --dom-automation
        #     --full-memory-crash-report
        #     --no-default-browser-check
        #     --no-first-run
        #     --disable-background-networking
        #     --disable-sync
        #     --disable-translate
        #     --disable-web-resources
        #     --safebrowsing-disable-auto-update
        #     --safebrowsing-disable-download-protection
        #     --disable-client-side-phishing-detection
        #     --disable-component-update
        #     --disable-default-apps
        #     --enable-logging
        #     --log-level=1
        #     --ignore-certificate-errors
        #     --no-default-browser-check
        #     --test-type=ui
        #     --user-data-dir="C:\Users\nik\AppData\Local\Temp\scoped_dir1972_4232"
        #     --testing-channel=ChromeTestingInterface:1972.1
        #     --noerrdialogs
        #     --metrics-recording-only
        #     --enable-logging
        #     --disable-zero-browsers-open-for-tests
        #     --allow-file-access
        #     --allow-file-access-from-files about:blank


        self.driver = webdriver.Chrome(desired_capabilities=caps, chrome_options=chrome_options)
        #self.driver.minimize_window()
        # The following might work on Linux but does not work on MacOS
        self.driver.set_window_position(0,-1000)
        self.driver.get(url)

        #driver.implicitly_wait(2)
        #action = ActionChains(driver)
        #action.send_keys(Keys.ALT, Keys.TAB)
        #time.sleep(5)


        # ActionChains(driver) \
        #     .send_keys(Keys.CONTROL + Keys.COMMAND + "f") \
        #     .perform()

        # ActionChains(driver) \
        #     .key_down(Keys.COMMAND) \
        #     .click(element) \
        #     .key_up(Keys.COMMAND) \
        #     .perform()
       
        #driver.getKeyboard().pressKey(Keys.F11)

        # time.sleep(10)
        # logger.info("Close broser")
        # driver.close()
        # driver.quit()
        #driver.fullscreen_window()

    def close(self):
        self.driver.close()