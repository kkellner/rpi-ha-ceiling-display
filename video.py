#!/usr/local/bin/python3

import pyblueiris
from aiohttp import ClientSession
import asyncio
import yaml
import logging

import time,pygame
import os, io
import threading
import platform
import socket
from colorsys import rgb_to_hls, hls_to_rgb
#from moviepy.editor import VideoFileClip

#import webbrowser

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


PROTOCOL = 'http'


FORMAT = '%(asctime)-15s %(threadName)-10s %(levelname)6s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

logger = logging.getLogger(__name__)

colorBaseWhite = (255, 255, 255)
colorBaseGray = (163, 163, 163)
colorBaseRed = (209, 79, 79)
colorBaseBlue = (82, 116, 227)
colorBaseGreen = (72, 181, 94)

class HdmiDisplay:


    def __init__(self):
        #initialize pygame library
        self.displayEnabled = True
        self.valueColor = colorBaseRed

    def startup(self, camUrl):

        self.camUrl =camUrl
        #webbrowser.open('http://example.com')  # Go to example.com

        # Docs: https://selenium-python.readthedocs.io/getting-started.html



        # driver = webdriver.Firefox()

        # # This came from a Java example
        # # FirefoxProfile profile = new FirefoxProfile();
        # #profile.setPreference("browser.fullscreen.autohide",true)
        # #profile.setPreference("browser.fullscreen.animateUp",0)
        # #WebDriver driver = new FirefoxDriver(profile);

        # #driver.maximize_window()
        # #driver.get("http://www.python.org")
        # driver.get(camUrl)
        # #driver.manage().window().fullscreen()
        # driver.fullscreen_window()


        # Note this needs to be the correct keystroke for the OS
        #((FirefoxDriver)driver).getKeyboard().pressKey(Keys.F11);

        # assert "Python" in driver.title
        # elem = driver.find_element_by_name("q")
        # elem.clear()
        # elem.send_keys("pycon")
        # elem.send_keys(Keys.RETURN)

        # time.sleep(5)

        # assert "No results found." not in driver.page_source
        # driver.close()
        # driver.quit()

        # time.sleep(10)

        #pygame.init()
        pygame.display.init()
        pygame.font.init()
        #pygame.mouse.set_visible(True)

        # Print a list of all available fonts
        #print(pygame.font.get_fonts())

        #theFont1=pygame.font.Font(None,105)

        self.fontTime=pygame.font.Font('fonts/Malter Sans Demo2.otf',150)

        self.fontLabel=pygame.font.Font('fonts/Malter Sans Demo2.otf',60)
        self.fontValue=pygame.font.Font('fonts/Malter Sans Demo2.otf',60)
        self.fontSmall=pygame.font.Font('fonts/Malter Sans Demo2.otf',24)

        self.fontLabel2=pygame.font.Font('fonts/Malter Sans Demo2.otf',40)
        self.fontValue2=pygame.font.Font('fonts/Malter Sans Demo2.otf',40)

        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        #self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE|pygame.HWSURFACE|pygame.DOUBLEBUF)

        #self.screen = pygame.display.set_mode((1280, 720))
        
        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.display.set_caption('Display Time')

        print(pygame.display.Info())

        # movie = pygame.movie.Movie('/Users/kkellner/Downloads/sample_640x360.mpeg')
        # self.movie_screen = pygame.Surface(movie.get_size()).convert()
        # movie.set_display(self.movie_screen)
        # movie.play()

        # Docs:  https://zulko.github.io/moviepy/
        #clip = VideoFileClip('/Users/kkellner/Downloads/sample_640x360.mpeg')
        #clip = VideoFileClip('http://172.20.0.160/mjpg/cam24/video.mjpg?session=0dc6090a7b1602cf07064ef91f6809cc')
        #clip.preview()


        self.updateDisplayLoop()
        logger.warning("#### Exiting updateDisplayLoop")
        pygame.display.quit()
        logger.warning("#### about to call pygame.quit()")
        pygame.quit()

    def updateDisplayLoop(self):

        done = False
        while not done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    break
                    
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_x or event.key == pygame.K_q):
                    done = True
                    break
                #logger.info("gui-event: %s", str(event))

                if event.type == pygame.KEYDOWN and (event.key == pygame.K_o):
                    self.openBrowserThread()
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_c):
                    self.driver.close()


            self.screen.fill((0,0,0))

            self.updateTime(10,60)


            # screen.blit(self.movie_screen,(0,0))

            pygame.display.update()

            # Update interval (fps)
            self.clock.tick(2)

    def openBrowserThread(self):
        thread1 = threading.Thread(target=(lambda: self.openBrowser() ))
        thread1.setDaemon(True)
        thread1.start()

    def openBrowser(self):
        
        caps = DesiredCapabilities().FIREFOX
        #caps["pageLoadStrategy"] = "normal"  #  complete
        #caps["pageLoadStrategy"] = "eager"  #  interactive
        caps["pageLoadStrategy"] = "none"

        fireFoxOptions = webdriver.FirefoxOptions()
        fireFoxOptions.add_argument("--start-maximized")
        fireFoxOptions.add_argument("--disable-infobars")
        fireFoxOptions.set_preference("dom.webnotifications.enabled", False)

        driver = webdriver.Firefox(desired_capabilities=caps, firefox_options=fireFoxOptions)
        
        #driver = webdriver.Firefox()
        self.driver = driver
        driver.get(self.camUrl)
        driver.implicitly_wait(2)
        #action = ActionChains(driver)
        #action.send_keys(Keys.ALT, Keys.TAB)
        time.sleep(5)
        ActionChains(driver) \
            .send_keys(Keys.COMMAND + "f") \
            .perform()

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


    def updateTime(self, displayX: int, displayY: int):

        epochNow = time.time()
        now = time.localtime(epochNow)
        halfSecond = (epochNow % 1) >= 0.5
        #print (epochNow, halfSecond)

        if halfSecond:
            theTime=time.strftime("%I:%M", now)
        else:
            theTime=time.strftime("%I~%M", now)

        ampm=time.strftime("%p", now)

        if theTime.startswith('0'):
            theTime = theTime.replace('0', ' ', 1)

        # Time (HH:MM)
        #text_width, text_height = theFont1.size(str(theTime))
        timeText=self.fontTime.render(str(theTime), True, self.valueColor, (0,0,0))
        timeText_width = timeText.get_width()
        timeText_height = timeText.get_height()
        self.screen.blit(timeText, (displayX,displayY))

        # AM/PM 
        ampmText=self.fontSmall.render(str(ampm), True, self.valueColor, (0,0,0))
        ampmText_width = ampmText.get_width()
        ampmText_height = ampmText.get_height()
        self.screen.blit(ampmText, (displayX+timeText_width-ampmText_width, displayY-ampmText_height+5))



async def callBlueIris():

    ymlfile = open("config.yml", 'r')
    cfg = yaml.safe_load(ymlfile)
    config = cfg['blueiris']
    host = config['host']
    username = config['username']
    password = config['password']

    async with ClientSession(raise_for_status=True) as sess:
        blue = pyblueiris.BlueIris(sess, username, password, PROTOCOL, host, "", True)
        #await blue.update_all_information()
        #print(blue.attributes)
        x = await blue.setup_session()
        #print (x)
        #await blue.update_all_information()
        #print(blue.attributes)
        await blue.update_camlist()
        #print(blue.attributes)
        camAttr = await blue.get_camera_details('cam24')
        print ("#####")
        #print (camAttr)
        cam = pyblueiris.camera.BlueIrisCamera(blue, "cam24")
        await cam.update_camconfig()
        print (cam.mjpeg_url)


        print(blue.client.blueiris_session)
        return "{}?session={}".format(cam.mjpeg_url, blue.client.blueiris_session)

        # http://172.20.0.160/mjpg/cam24/video.mjpg?session=37c828f9108a17ad5df97c213f2a6d1a


def main():  


    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(callBlueIris(), loop=loop)
    try:
        url = loop.run_until_complete(future)
    except KeyboardInterrupt:
        future.cancel()
        loop.run_until_complete(future)
        loop.close()

    logger.info("URL: %s", url)
    
    display = HdmiDisplay()
    display.startup(url)

    print("Existing app...")
    pygame.quit()
    exit()





if __name__ == '__main__':
  main()

