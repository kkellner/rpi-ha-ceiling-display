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
try:
    import pydbus
    timedated = pydbus.SystemBus().get(".timedate1")
except ImportError:
    print("pydbus library not found")
    timedated = None

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
        self.setBrightness(DEFAULT_DISPLAY_BRIGHTNESS)

        logger.info("time synced: %s", str(self.isTimeSynced()) )


    def startup(self):

        #pygame.init()
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)

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
        #self.screen = pygame.display.set_mode((1280, 720))
        
        self.screen.fill((0,0,0))
        pygame.display.flip()
        pygame.display.set_caption('Ceiling Display Time')
    
        print(pygame.display.Info())

        self.updateDisplayLoop()
        logger.warning("#### Exiting updateDisplayLoop")
        pygame.display.quit()
        logger.warning("#### about to call pygame.quit()")
        pygame.quit()

    def isTimeSynced(self):
        """
        Return True if time is synchronized.
        """
        if timedated is not None:
            return timedated.NTPSynchronized
        else:
            return False

    def getEventAttribute(self, eventId, attributeName, defaultValue = UNAVAILABLE_VALUE):
        events = self.ceiling_display.ha_events.events
        if eventId in events:
            attributes =  events[eventId]['new_state']['attributes']
            value = UNAVAILABLE_VALUE
            if attributeName in attributes:
                value = attributes[attributeName]
            if value == UNKNOWN_VALUE or value == UNAVAILABLE_VALUE:
                value = defaultValue
        else:
            value = defaultValue
        return value

    def getEventAttributeInt(self, eventId, attributeName, defaultValue = -1):
        return int(self.getEventAttribute(eventId, attributeName, defaultValue))

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
                    
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or event.key == pygame.K_x or event.key == pygame.K_q):
                    done = True
                    break
                #logger.info("gui-event: %s", str(event))

            self.screen.fill((0,0,0))

            haEvents = self.ceiling_display.ha_events
            events = haEvents.events

            outsideTemperature = self.getEventValueFloat('sensor.outdoor_temperature')
            insideTemperature = self.getEventValueFloat('sensor.zbtemp301_bedroom_temperature')
            windSpeed = self.getEventValueFloat('sensor.wind_speed')
            windGust = self.getEventValueFloat('sensor.wind_gust')
            rainRate = self.getEventValueFloat('sensor.daily_rain_rate')

            self.updateTime(10,60)

            if haEvents.statesSynced:
          
                self.updateInsideTemperature(10, 250, insideTemperature)

                self.updateOutsideTemperature(10, 350, outsideTemperature)
                self.updateWind(300, 350, windSpeed, windGust)

                if rainRate > 0:
                    self.updateRain(530, 350, rainRate)
                
                self.updateHvac(10, 450)
                
            if haEvents.connected:
                self.updateDebug(10, 530, "Events", "{:d}".format(haEvents.eventCount))
                #self.updateDebug(10, 560, "Connected", "{:s}".format(str(haEvents.connected)))
                self.updateDebug(10, 560, "Connect Attempts", "{:s}".format(str(haEvents.connectAttemptCount)))
                self.updateDebug(10, 590, "Successsful Connects", "{:s}".format(str(haEvents.connectSuccessCount)))
            else:
                disconnectedDuration = time.time() - haEvents.lastDisconnectTime
                formattedDuration = formatDuration(disconnectedDuration)
                self.updateDebug(10, 530, "Disconnected", formattedDuration)
                self.updateDebug(10, 560, "Connect Attempts", "{:s}".format(str(haEvents.connectAttemptCount)))
                self.updateDebug(10, 590, "Successsful Connects", "{:s}".format(str(haEvents.connectSuccessCount)))

            pygame.display.update()

            # Update interval (fps)
            self.clock.tick(2)

    def setBrightness(self, brightnessPercent):
        self.brightness = brightnessPercent
        logger.info("Set brightness: %i", brightnessPercent)
        self.valueColor = adjust_color_lightness(colorBaseRed, 1-((100-brightnessPercent)/100))
        labelBrightness = (brightnessPercent / 100) ** 0.5 * .5
        self.labelColor = darken_color(self.valueColor, labelBrightness)
        WARN_COLOR=(161, 159, 47)
        warnBrightness = brightnessPercent
        self.warnColor = adjust_color_lightness(WARN_COLOR, 1-((100-warnBrightness)/100))

    def updateBrightness(self):
        b = self.getEventValueFloat('input_number.ceiling_display_brightness', self.brightness)
        if (b != self.brightness):
            self.setBrightness(b)
      
        enabled = self.getEventValueBoolean('input_boolean.ceiling_display_enabled', True)
        if (enabled != self.displayEnabled):
            self.displayEnabled = enabled
            logger.info("Set Display Enabled: %s", str(enabled))
            if is_raspberrypi():
                cmd = "/usr/bin/vcgencmd display_power {}".format(int(enabled)) 
                logger.info("Running on Raspberry PI - turn on/off HDMI, cmd: %s", cmd)
                os.system(cmd)
            elif is_linux():
                if enabled:
                   cmd = "/usr/bin/xrandr --output HDMI-1 --auto" 
                else:
                   cmd = "/usr/bin/xrandr --output HDMI-1 --off" 
                logger.info("Running on Linux - turn on/off HDMI, cmd: %s", cmd)
                os.system(cmd)
            else:
                logger.info("Running on OSX? - can't turn on/off HDMI")

             


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
    

    def updateHvac(self, displayX: int, displayY: int):
        # HVAC status
        # Example: HVAC 65 current 64: heating
        hvacAction = self.getEventAttribute("climate.thermostat", "hvac_action")
        #fanAction = self.getEventAttribute("climate.thermostat", "fan_action")
        set_temperature = self.getEventAttributeInt("climate.thermostat", "temperature")
        current_temperature = self.getEventAttributeInt("climate.thermostat", "current_temperature")

        formattedValue = "{:d}° {:s}: {:d}°".format(set_temperature, hvacAction, current_temperature)
     
        label = "HVAC:"
        labelText=self.fontLabel2.render(label, True, self.labelColor, (0,0,0))
        labelText_width = labelText.get_width()
        self.screen.blit(labelText, (displayX,displayY))

        valueText=self.fontValue2.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        self.screen.blit(valueText, (displayX + labelText_width+35, displayY))




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

        if not self.isTimeSynced():
            warnColor = self.warnColor
            pygame.draw.rect(self.screen,warnColor,(displayX,displayY+50,timeText_width,2))
            pygame.draw.rect(self.screen,warnColor,(displayX,displayY+90,timeText_width,2))
            pygame.draw.rect(self.screen,warnColor,(displayX,displayY+130,timeText_width,2))
            notSyncedText=self.fontSmall.render("Not Synced", True, warnColor, (0,0,0))
            self.screen.blit(notSyncedText, (displayX+40, displayY-ampmText_height+5))


    def updateOutsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature Outside
        displayXValueOffset = 150
        label = "Out:"
        labelText=self.fontValue.render(label, True, self.labelColor, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}°".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))

    def updateInsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature Inside
        displayXValueOffset = 150
        label = "In:"
        labelText=self.fontValue.render(label, True, self.labelColor, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}°".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))


    def updateWind(self, windDisplayX: int, windDisplayY: int, windSpeed: float, windGust: float ):
        # Wind Speed
        windSpeedFormatted = "{:.0f}".format(windSpeed)
        windGustFormatted = "{:.0f}".format(windGust)

        if windSpeedFormatted != windGustFormatted:
            formattedWind = "{:s}-{:s}".format(windSpeedFormatted, windGustFormatted)
        else:
            formattedWind = "{:s}".format(windSpeedFormatted)

        valueText=self.fontValue.render(formattedWind, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (windDisplayX,windDisplayY))
        suffixText=self.fontSmall.render(str("mph"), True, self.valueColor, (0,0,0))
        suffixText_width = suffixText.get_width()
        suffixText_height = suffixText.get_height()
        self.screen.blit(suffixText, (windDisplayX+valueText_width+4, windDisplayY+valueText_height-suffixText_height-10))

    def updateRain(self, displayX: int, displayY: int, rainRate: float):
        # Rain
        label = "Rain:"
        labelText=self.fontValue.render(label, True, self.labelColor, (0,0,0))
        labelText_width = labelText.get_width()
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.2f}".format(rainRate)
        valueText=self.fontValue.render(formattedValue, True, self.valueColor, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + labelText_width+8, displayY))

        suffixText=self.fontSmall.render("in", True, self.valueColor, (0,0,0))
        suffixText_width = suffixText.get_width()
        suffixText_height = suffixText.get_height()
        self.screen.blit(suffixText, (displayX+valueText_width+labelText_width+10, displayY+valueText_height-suffixText_height-10))


def formatDuration(duration):
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)
    durationFormatted = ""
    if hours > 0:
        durationFormatted += "{:.0f}h ".format(hours)
    if minutes > 0:
        durationFormatted += "{:.0f}m ".format(minutes)
    durationFormatted += "{:0.0f}s".format(seconds)

    return durationFormatted


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

def is_linux():
    return platform.system() == 'Linux'

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

