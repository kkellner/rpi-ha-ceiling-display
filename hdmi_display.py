# Docs: https://www.pygame.org/docs/ref/display.html

# AnyBeam Pico Mini Portable Pocket
# Resolution: 720p = 1280 x 720, aspect ratio: 16:9

# Turn on/off HDMI port:
#   vcgencmd display_power 0 [display]
#   vcgencmd display_power 1 [display]
#
# Check if display is on or off (example HDMI 1):
#   vcgencmd display_power -1 7 
#
# Optional display:
#   Display	        ID
#   Main LCD        0
#   Secondary LCD	1
#   HDMI 0          2
#   Composite       3
#   HDMI 1          7
#
# If HDMI-CDC is needed, see: https://pimylifeup.com/raspberrypi-hdmi-cec/
#


import time,pygame
import os, io
import threading
import platform
import logging
from colorsys import rgb_to_hls, hls_to_rgb

logger = logging.getLogger(__name__)

# This is a value returned from an entity that is unknown (e.g., HA first starting)
UNKNOWN_VALUE = "unknown"
UNAVAILABLE_VALUE = "unavailable"

DEFAULT_DISPLAY_BRIGHTNESS = 50.0
class HdmiDisplay:

    def __init__(self, ceiling_display):
        #initialize pygame library

        self.ceiling_display = ceiling_display
        self.displayEnabled = True
        self.brightness = DEFAULT_DISPLAY_BRIGHTNESS

        self.valueColor = colorBaseRed
        self.labelColor = darken_color(self.valueColor, 0.5)
 

    def startup(self):

        pygame.init()
        pygame.mouse.set_visible(False)

        # Print a list of all available fonts
        #print(pygame.font.get_fonts())

        #theFont1=pygame.font.Font(None,105)

        self.fontTime=pygame.font.Font('fonts/Malter Sans Demo2.otf',150)

        self.fontLabel=pygame.font.Font('fonts/Malter Sans Demo2.otf',60)
        self.fontValue=pygame.font.Font('fonts/Malter Sans Demo2.otf',60)
        self.fontSmall=pygame.font.Font('fonts/Malter Sans Demo2.otf',24)

        #theFont2=pygame.font.Font('fonts/DS-DIGII2.otf',88)
        #theFont3=pygame.font.Font('fonts/DS-DIGIT2.otf',84)

        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((1280, 720))
        
        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.display.set_caption('Pi Time')
        # Clear screen

        print(pygame.display.Info())

        self.updateDisplayLoop()

        # thread1 = threading.Thread(target=(lambda: self.updateDisplayLoop() ))
        # thread1.setDaemon(False)
        # thread1.start()

    def getEventValue(self, eventId, defaultValue):
        events = self.ceiling_display.ha_events.events
        if eventId in events:
            value =  events[eventId]['new_state']['state']
            if value == UNKNOWN_VALUE or value == UNAVAILABLE_VALUE:
                value = defaultValue
        else:
            value = defaultValue
        return value

    def getEventValueFloat(self, eventId, defaultValue=float("nan")):
        return float(self.getEventValue(eventId, defaultValue))

    def getEventValueInt(self, eventId, defaultValue = -1):
        return int(self.getEventValue(eventId, defaultValue))

    def getEventValueBoolean(self, eventId, defaultValue = False):
        return str2bool(self.getEventValue(eventId, defaultValue))


    def updateDisplayLoop(self):

        done = False
        while not done:

            self.updateBrightness()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    break
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    done = True
                    break

            self.screen.fill((0,0,0))

            haEvents = self.ceiling_display.ha_events
            events = haEvents.events

            outsideTemperature = self.getEventValueFloat('sensor.outdoor_temperature')
            insideTemperature = self.getEventValueFloat('sensor.zbtemp301_bedroom_temperature')
            windSpeed = self.getEventValueFloat('sensor.wind_speed')
            windGust = self.getEventValueFloat('sensor.wind_gust')

            self.updateTime(80,60)

            self.updateInsideTemperature(80, 250, insideTemperature)

            self.updateOutsideTemperature(80, 350, outsideTemperature)
            self.updateWind(370, 350, windSpeed, windGust)

            self.updateDebug(80, 470, "Events", "{:d}".format(haEvents.eventCount))
            self.updateDebug(80, 500, "Connected", "{:s}".format(str(haEvents.connected)))
            if not haEvents.connected:
                disconnectedDuration = time.time() - haEvents.lastDisconnectTime
                self.updateDebug(80, 530, "Disconnected", "{:.1f}".format(disconnectedDuration))

            pygame.display.update()

            # Update interval (fps)
            self.clock.tick(2)

    def updateBrightness(self):
        b = self.getEventValueFloat('input_number.ceiling_display_brightness', DEFAULT_DISPLAY_BRIGHTNESS)
        if (b != self.brightness):
            self.brightness = b
            logger.info("brightness: %i", b)
            self.valueColor = adjust_color_lightness(colorBaseRed, 1-((100-b)/100))
            self.labelColor = darken_color(self.valueColor, 0.5)

        enabled = self.getEventValueBoolean('input_boolean.ceiling_display_enabled', True)
        if (enabled != self.displayEnabled):
            self.displayEnabled = enabled
            logger.info("Set Display Enabled: %s", str(enabled))
            if is_raspberrypi():
                cmd = "/usr/bin/vcgencmd display_power {}".format(int(enabled)) 
                logger.info("Running on Raspberry PI - turn on/off HDMI, cmd: %s", cmd)
                os.system(cmd)


    def updateDebug(self, displayX: int, displayY: int, label:str, debugText: str):
        # Temperature
        displayXValueOffset = 0
        
        labelText=self.fontSmall.render(label+": ", True, self.labelColor, (0,0,0))
        labelText_width = labelText.get_width()
        self.screen.blit(labelText, (displayX, displayY))

        formattedValue = debugText
        valueText=self.fontSmall.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + labelText_width+ displayXValueOffset, displayY))
    

 
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

    def updateOutsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature
        displayXValueOffset = 150
        label = "Out:"
        labelText=self.fontValue.render(label, True, self.labelColor, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))

        degreeSymbolText=self.fontSmall.render(str("°"), True, self.valueColor, (0,0,0))
        degreeSymbolText_width = degreeSymbolText.get_width()
        degreeSymbolText_height = degreeSymbolText.get_height()
        self.screen.blit(degreeSymbolText, (displayX+displayXValueOffset+valueText_width+4, displayY+10))

    def updateInsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature
        displayXValueOffset = 150
        label = "In:"
        labelText=self.fontValue.render(label, True, self.labelColor, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))

        degreeSymbolText=self.fontSmall.render(str("°"), True, self.valueColor, (0,0,0))
        degreeSymbolText_width = degreeSymbolText.get_width()
        degreeSymbolText_height = degreeSymbolText.get_height()
        self.screen.blit(degreeSymbolText, (displayX+displayXValueOffset+valueText_width+4, displayY+10))


    def updateWind(self, windDisplayX: int, windDisplayY: int, windSpeed: float, windGust: float ):
        # Wind
        windSpeedFormatted = "{:.0f}".format(windSpeed)
        windGustFormatted = "{:.0f}".format(windGust)

        if windSpeedFormatted != windGustFormatted:
            formattedWind = "{:s}-{:s}".format(windSpeedFormatted, windGustFormatted)
        else:
            formattedWind = "{:s}".format(windSpeedFormatted)

        tempText=self.fontValue.render(formattedWind, True, self.valueColor, (0,0,0))
        tempText_width = tempText.get_width()
        tempText_height = tempText.get_height()
        self.screen.blit(tempText, (windDisplayX,windDisplayY))
        mphText=self.fontSmall.render(str("mph"), True, self.valueColor, (0,0,0))
        mphText_width = mphText.get_width()
        mphText_height = mphText.get_height()
        self.screen.blit(mphText, (windDisplayX+tempText_width+4, windDisplayY+tempText_height-mphText_height-15))

    def updateField(self, windDisplayX: int, windDisplayY: int, label: str, value: float, suffix: str):
        x=0


# def brightness(color)
# {
#    return (int)Math.Sqrt(
#       c.R * c.R * .241 +     # Red
#       c.G * c.G * .691 +     # Green
#       c.B * c.B * .068);     # Blue
# }




def adjust_color_lightness(color, factor):
    h, l, s = rgb_to_hls(color[0] / 255.0, color[1] / 255.0, color[2] / 255.0)
    l = max(min(l * factor, 1.0), 0.0)
    r, g, b = hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def lighten_color(color, factor=0.1):
    return adjust_color_lightness(color, 1 + factor)


def darken_color(color, factor=0.1):
    return adjust_color_lightness(color, 1 - factor)

def str2bool(v):
    if type(v) is bool:
        return v
    return v.lower() in ("yes", "true", "on", "t", "1")

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

colorBaseWhite = (255, 255, 255)
colorBaseGray = (163, 163, 163)
colorBaseRed = (209, 79, 79)
colorBaseBlue = (82, 116, 227)
colorBaseGreen = (72, 181, 94)


def main():
    """
    The main function
    :return:
    """
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")



    display = HdmiDisplay()
    display.starup()

    print("Existing app...")
    pygame.quit()
    exit()


if __name__ == '__main__':
    main()

