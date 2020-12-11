#!/usr/local/bin/python3
#!/usr/bin/python3
#
#
#
#
# REST API get single state example:
#    http://homeassistant.local:8123/api/states/light.kitchen.

import asyncio
import json
import traceback
import asyncws
#import websockets
import socket
import threading
import logging
import yaml
import time
import os, sys, signal


logger = logging.getLogger(__name__)

PINGPONG_INTERVAL_SECONDS = 15
PINGPONG_MAX_RESPONSE_TIME_SECONDS = 5
RECONNECT_DELAY_SECONDS = 5

class HaEvents:

    def __init__(self, ceiling_display):
        """Simple WebSocket client for Home Assistant."""

        self.connectAttemptCount = 0
        self.connectSuccessCount = 0
        self.eventCount = 0
        self.nextRequestId = 1
        self.events = {}
        self.shutdown = False
        self.connected = False
        self.lastDisconnectTime = time.time()
        self.lastPongId = 0
        self.loop = None

        self.ceiling_display = ceiling_display
        ymlfile = open("config.yml", 'r')
        cfg = yaml.safe_load(ymlfile)
        haConfig = cfg['homeassistant']
        self.websocketUrl = haConfig['websocket_url']
        self.haAccessToken = haConfig['access_token']


    def startup(self):

        thread1 = threading.Thread(target=(lambda: self.processEventsX() ))
        thread1.setDaemon(True)
        thread1.start()
    
    async def pingPongLoop(self, websocket):

        # Loop forever performing a ping/pong
        try:
            while True:
                #time.sleep(PINGPONG_TIME)
                await asyncio.sleep(PINGPONG_INTERVAL_SECONDS) 
                requestId = self.getNextRequestId()
                logger.info("Send PING id: %d", requestId)
                await websocket.send(json.dumps(
                    {"id": requestId, "type": "ping"}
                ))
                await asyncio.sleep(PINGPONG_MAX_RESPONSE_TIME_SECONDS)
                if (requestId != self.lastPongId):
                    logger.warn("Did not get PONG within %d seconds. Force socket closed", PINGPONG_MAX_RESPONSE_TIME_SECONDS)
                    # self.loop.stop()
                    # Force the socket closed to unblock the recv() blocking method call
                    websocket.writer.close() 
                    break
        except (ConnectionError, socket.timeout, socket.herror, socket.gaierror) as e:
            logger.warn("pingPongLoop - ConnectionError: Type: %s Msg: %s", type(e), e)
            websocket.writer.close()
        except Exception as e:
            logger.warn("pingPongLoop - Error: Type: %s Msg: %s", type(e), e)
            traceback.print_exception(*sys.exc_info())
            websocket.writer.close()


    def processEventsX(self):
 
        while True:
            try:
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
                #self.loop = asyncio.get_event_loop()
                logger.info("calling processEvents")
                self.loop.run_until_complete(self.processEvents())
                logger.warn("processEvents has ended")
                self.loop.close()
            except Exception as e:
                logger.error("processEventsX:Error: Type: %s Msg: %s", type(e), e)
                traceback.print_exception(*sys.exc_info()) 

            # Wait 5 second before we try to reconnect
            #await asyncio.sleep(5)
            logger.warn("Waiting %d seconds before reconnect to Home Assistant attempt", RECONNECT_DELAY_SECONDS)
            time.sleep(RECONNECT_DELAY_SECONDS)
                    
    def allStatesToEvents(self, json_msg):
        results = json_msg["result"]
        for event in results:
            eventId = event['entity_id']
            self.events[eventId] = {"new_state": event}

        #print(self.events)

    async def processEvents(self):
    
        try:
            await self.processEvents2()
        except (ConnectionError, socket.timeout, socket.herror, socket.gaierror) as e:
            logger.warn("processEvents:ConnectionError: Type: %s Msg: %s", type(e), e)
        except Exception as e:
            logger.warn("processEvents:Error: Type: %s Msg: %s", type(e), e)
            #traceback.print_exc() 
            traceback.print_exception(*sys.exc_info()) 
        
        self.events = {}
        if self.connected == True:
            self.connected = False
            self.lastDisconnectTime = time.time()
        


    async def processEvents2(self):
    # HA websocket docs:
    # https://developers.home-assistant.io/docs/api/websocket/

        #async with websockets.connect(self.websocketUrl) as websocket:

        self.connectAttemptCount += 1
        logger.info("HA connectAttemptCount: %d", self.connectAttemptCount)
        websocket = await asyncws.connect(self.websocketUrl)
        
        await websocket.send(json.dumps(
            {'type': 'auth',
            'access_token': self.haAccessToken}
        ))

        startupRequestId = self.getNextRequestId()
    
        self.connected = True
        self.connectSuccessCount += 1
        logger.info("HA connectSuccessCount: %d", self.connectSuccessCount)
        await websocket.send(json.dumps(
            {"id": startupRequestId, "type": "get_states"}
        ))
        
        # Format
        # {"id": 1, "type": "result", "success": true, "result": [{"entity_id": "person.kkellner", "state": "home", "attributes": {"editable": true, "id": "5f3d180e25bd4e098dc4a5510221746f", "source": "device_tracker.kurtphone", "user_id": "4447436a5424483bb91d1d4fd28e2a3f", "friendly_name": "kkellner", "last_changed": "2020-11-23T18:12:14.287334+00:00", "last_updated": "2020-11-23T18:12:26.184702+00:00", "context": {"id": "597d90a0be7b9e6bcd51058f45607969", "parent_id": null, "user_id": null}}, {"entity_id": "person.jkellner", "state": "home", "attributes": {"editable": true, "id": "d707594627274c208bd99a265203dc0c",

        # TODO: Ping/Pong:  https://developers.home-assistant.io/docs/api/websocket/#pings-and-pongs
        loop = asyncio.get_event_loop()
        asyncio.run_coroutine_threadsafe(self.pingPongLoop(websocket), loop)

        # Loop forever processing states/events from HA
        while True:

            message = await websocket.recv()
            if message is None:
                logger.info("Stream was closed")
                break
            #print (message)
            self.eventCount += 1
            try:
                json_msg = json.loads(message)
                if ('id' in json_msg and json_msg['id'] == startupRequestId):
                    # Startup response to get-all-states request 
                    logger.info("Got all states")
                    self.allStatesToEvents(json_msg)
                    logger.info("allStatesToEvents complete")
                    # Subscribe to all events
                    await websocket.send(json.dumps(
                    {'id': self.getNextRequestId(), 'type': 'subscribe_events', 'event_type': 'state_changed'}
                    ))
                elif (json_msg['type'] == 'event' and json_msg['event']['event_type'] == 'state_changed'):
                    entityId = json_msg['event']['data']['entity_id']
                    #newState = json_msg['event']['data']['new_state']
                    self.events[entityId] = json_msg['event']['data']
                    print(f"\rEvents: {self.eventCount}", end='', flush=True)
                elif (json_msg['type'] == 'pong'):
                    self.lastPongId = json_msg['id']
                    logger.info("Got a PONG id: %d", self.lastPongId)
                else:
                    logger.info("Unknown event: %s", str(json_msg))

            except Exception as e:
                logger.warn("processEvents2: Error extracting data from json_msg. Error: %s Msg: %s, json: %s", type(e), e, message)


    def getNextRequestId(self):
        requestId = self.nextRequestId
        self.nextRequestId += 1
        return requestId

def main():
    """
    The main function
    :return:
    """
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")

  
    events = HaEvents()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(events.startup())
    loop.close()


if __name__ == '__main__':
    main()



# All states example reponse:
# {
#   "id": 1,
#   "type": "result",
#   "success": true,
#   "result": [
#     {
#       "entity_id": "person.kkellner",
#       "state": "home",
#       "attributes": {
#         "editable": true,
#         "id": "5f3d180e25bd4e098dc4a5510221746f",
#         "source": "device_tracker.kurtphone",
#         "user_id": "4447436a5424483bb91d1d4fd28e2a3f",
#         "friendly_name": "kkellner",
#         "entity_picture": "/api/image/serve/de56b41ad6ecad574b2bcd032f70feea/512x512"
#       },
#       "last_changed": "2020-11-23T18:12:14.287334+00:00",
#       "last_updated": "2020-11-23T18:12:26.184702+00:00",
#       "context": {
#         "id": "597d90a0be7b9e6bcd51058f45607969",
#         "parent_id": null,
#         "user_id": null
#       }
#     },

#
# Subscribe example event:
# {
#   "id": 1,
#   "type": "event",
#   "event": {
#     "event_type": "state_changed",
#     "data": {
#       "entity_id": "sensor.zwmimo_garage_door_large_general",
#       "old_state": {
#         "entity_id": "sensor.zwmimo_garage_door_large_general",
#         "state": "2.0",
#         "attributes": {
#           "node_id": 32,
#           "value_index": 2,
#           "value_instance": 1,
#           "value_id": "72057594579796002",
#           "unit_of_measurement": "",
#           "friendly_name": "zwmimo_garage_door_large General"
#         },
#         "last_changed": "2020-11-23T05:36:11.073388+00:00",
#         "last_updated": "2020-11-23T05:36:11.073388+00:00",
#         "context": {
#           "id": "12e6491bebc6c33a3147d6be801ee030",
#           "parent_id": null,
#           "user_id": null
#         }
#       },
#       "new_state": {
#         "entity_id": "sensor.zwmimo_garage_door_large_general",
#         "state": "2.0",
#         "attributes": {
#           "node_id": 32,
#           "value_index": 2,
#           "value_instance": 1,
#           "value_id": "72057594579796002",
#           "unit_of_measurement": "",
#           "friendly_name": "zwmimo_garage_door_large General"
#         },
#         "last_changed": "2020-11-23T05:36:41.373671+00:00",
#         "last_updated": "2020-11-23T05:36:41.373671+00:00",
#         "context": {
#           "id": "de8ca765ea8fa3e3d9115875142e22a1",
#           "parent_id": null,
#           "user_id": null
#         }
#       }
#     },
#     "origin": "LOCAL",
#     "time_fired": "2020-11-23T05:36:41.373671+00:00",
#     "context": {
#       "id": "de8ca765ea8fa3e3d9115875142e22a1",
#       "parent_id": null,
#       "user_id": null
#     }
#   }
# }