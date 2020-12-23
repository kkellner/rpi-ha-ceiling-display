#!/usr/local/bin/python3

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


from blueiris import BlueIris
from browser import Browser

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

    def startup(self):

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
                    blueiris = BlueIris()
                    blueiris.login()
                    camName = "fdoor"
                    camUrl = blueiris.getCamURL(camName)
                    logger.info("CAM URL: %s", camUrl)
                    self.browser = Browser()
                    self.browser.openBrowserThread(camUrl)
                    
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_c):
                    self.browser.close()


            self.screen.fill((0,0,0))
            self.updateTime(10,60)
            pygame.display.update()

            # Update interval (fps)
            self.clock.tick(2)

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



def main():  


    # blueiris = BlueIris()
    # blueiris.login()
    # url = blueiris.getCamURL("cam24")
    # logger.info("CAM URL: %s", url)
    
    display = HdmiDisplay()
    display.startup()

    print("Existing app...")
    pygame.quit()
    exit()


if __name__ == '__main__':
  main()

