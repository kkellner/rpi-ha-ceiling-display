#!/usr/local/bin/python3
# Main class to drive a ceiling display of information
# from Home Assistant 
#
# Author: Kurt Kellner
#
import asyncio
#import json
import asyncws
import logging
import yaml
import os, sys, signal

from ha_events import HaEvents
from hdmi_display import HdmiDisplay

logger = logging.getLogger(__name__)

class CeilingDisplay:

    def __init__(self):
        """Setup all needed instances"""
        self.ha_events = None
        self.hdmi_display = None

        FORMAT = '%(asctime)-15s %(threadName)-10s %(levelname)6s %(message)s'
        logging.basicConfig(level=logging.NOTSET, format=FORMAT)

        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)



    def startup(self):
        logger.info('Startup...')
        self.ha_events = HaEvents(self)
        self.hdmi_display = HdmiDisplay(self)


        #loop = asyncio.get_event_loop()
        #loop.run(self.ha_events.startup())
        #loop.run_until_complete(self.hdmi_display.startup())
        

        #asyncio.create_task(self.ha_events.startup())
        #logger.info("after ha_events startup")
      
        self.ha_events.startup()
        self.hdmi_display.startup()
        
        #loop.close()
        logger.warn("about to exit")
        sys.exit(0) 


    def signal_handler(self, signal, frame):
        logger.info('Shutdown...')
        # if self.server is not None:
        #     self.server.shutdown()
        # if self.light is not None:
        #     self.light.shutdown()
        # if self.pubsub is not None:
        #     self.pubsub.shutdown()
        #sys.tracebacklimit = 0
        sys.exit(0)

def main():
    """
    The main function
    :return:
    """
    #if os.geteuid() != 0:
    #    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

  
    ceilingDisplay = CeilingDisplay()
    
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(ceilingDisplay.startup())
    # loop.close()
    ceilingDisplay.startup()

if __name__ == '__main__':
    main()
