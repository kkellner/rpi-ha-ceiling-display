
import pyblueiris
from aiohttp import ClientSession
import asyncio
import yaml
import logging

PROTOCOL = 'http'


FORMAT = '%(asctime)-15s %(threadName)-10s %(levelname)6s %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT)

logger = logging.getLogger(__name__)

def main():  
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(callBlueIris(), loop=loop)
    try:
        loop.run_until_complete(future)
    except KeyboardInterrupt:
        future.cancel()
        loop.run_until_complete(future)
        loop.close()


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

        # http://172.20.0.160/mjpg/cam24/video.mjpg?session=37c828f9108a17ad5df97c213f2a6d1a

if __name__ == '__main__':
  main()

