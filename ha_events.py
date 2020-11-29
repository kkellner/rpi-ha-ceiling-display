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
import socket
import threading
import logging
import yaml
import time
import os, sys, signal


logger = logging.getLogger(__name__)

class HaEvents:

    def __init__(self, ceiling_display):
        """Simple WebSocket client for Home Assistant."""

        self.eventCount = 0
        self.events = {}
        self.shutdown = False
        self.connected = False
        self.lastDisconnectTime = time.time()

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

    def processEventsX(self):
 
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logger.info("calling processEvents")
            loop.run_until_complete(self.processEvents())
            logger.warn("processEvents has ended")
            loop.close()
        except Exception as e:
            logger.error("Error: Type: %s Msg: %s", type(e), e)
            traceback.print_exception(*sys.exc_info()) 
                    
    def allStatesToEvents(self, json_msg):
        results = json_msg["result"]
        for event in results:
            eventId = event['entity_id']
            self.events[eventId] = {"new_state": event}

        #print(self.events)

    async def processEvents(self):
        while True:
            try:
                await self.processEvents2()
            except (ConnectionError, socket.timeout, socket.herror, socket.gaierror) as e:
                logger.warn("ConnectionError: Type: %s Msg: %s", type(e), e)
            except Exception as e:
                logger.warn("Error: Type: %s Msg: %s", type(e), e)
                #traceback.print_exc() 
                traceback.print_exception(*sys.exc_info()) 
            
            self.events = {}
            if self.connected == True:
                self.connected = False
                self.lastDisconnectTime = time.time()
            await asyncio.sleep(5)

    async def processEvents2(self):


        websocket = await asyncws.connect(self.websocketUrl)

        await websocket.send(json.dumps(
            {'type': 'auth',
            'access_token': self.haAccessToken}
        ))

        self.connected = True
        logger.info("get_states called")
        await websocket.send(json.dumps(
            {"id": 1, "type": "get_states"}
        ))
    
        # Format
        # {"id": 1, "type": "result", "success": true, "result": [{"entity_id": "person.kkellner", "state": "home", "attributes": {"editable": true, "id": "5f3d180e25bd4e098dc4a5510221746f", "source": "device_tracker.kurtphone", "user_id": "4447436a5424483bb91d1d4fd28e2a3f", "friendly_name": "kkellner", "last_changed": "2020-11-23T18:12:14.287334+00:00", "last_updated": "2020-11-23T18:12:26.184702+00:00", "context": {"id": "597d90a0be7b9e6bcd51058f45607969", "parent_id": null, "user_id": null}}, {"entity_id": "person.jkellner", "state": "home", "attributes": {"editable": true, "id": "d707594627274c208bd99a265203dc0c",

        while True:
            message = await websocket.recv()
            if message is None:
                break
            #print (message)
            json_msg = json.loads(message)
            if ('id' in json_msg and json_msg['id'] == 1):
                logger.info("Got all states")
                self.allStatesToEvents(json_msg)
                break

        logger.info("get_states complete")

        await websocket.send(json.dumps(
            {'id': 2, 'type': 'subscribe_events', 'event_type': 'state_changed'}
        ))

        while True:

            message = await websocket.recv()
            if message is None:
                break
            #print (message)
            self.eventCount += 1
            json_msg = json.loads(message)
            if (json_msg['type'] == 'event' and json_msg['event']['event_type'] == 'state_changed'):
                entityId = json_msg['event']['data']['entity_id']
                newState = json_msg['event']['data']['new_state']['state']

                self.events[entityId] = json_msg['event']['data']

                print(f"\rEvents: {self.eventCount}", end='', flush=True)
 

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