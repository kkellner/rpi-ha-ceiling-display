
import pyblueiris
from aiohttp import ClientSession
import asyncio
import yaml
import logging

logger = logging.getLogger(__name__)
class BlueIris:


    def __init__(self):

        logger.info("init")
        ymlfile = open("config.yml", 'r')
        cfg = yaml.safe_load(ymlfile)
        config = cfg['blueiris']
        self.protocol = 'http'
        self.host = config['host']
        self.username = config['username']
        self.password = config['password']
        
        self.bi = None

    def startup(self):
        logger.info("startup")

    def login(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_login())

    async def async_login(self):

        async with ClientSession(raise_for_status=True) as sess:

            self.bi = pyblueiris.BlueIris(sess, self.username, self.password, self.protocol, self.host, "", True)

            loginResult = await self.bi.setup_session()
            if loginResult == False:
                logger.error("Unable to login to Blue Iris")
                return

            #await blue.update_all_information()
            #print(blue.attributes)
            await self.bi.update_camlist()
            #print(blue.attributes)

    def getCamURL(self, camName):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_getCamURL(camName))

    async def async_getCamURL(self, camName):
            #camAttr = await blueiris.get_camera_details('cam24')
            cam = pyblueiris.camera.BlueIrisCamera(self.bi, camName)
            await cam.update_camconfig()

            #print(bi.client.blueiris_session)
            # http://172.20.0.160/mjpg/cam24/video.mjpg?session=37c828f9108a17ad5df97c213f2a6d1a
            
            fullUrl = "{}?session={}".format(cam.mjpeg_url, self.bi.client.blueiris_session)
            logger.info("camera: %s url: %s", camName, fullUrl)

            return fullUrl

