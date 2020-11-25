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
import os
from colorsys import rgb_to_hls, hls_to_rgb

class HdmiDisplay:

    def __init__(self):
        #initialize pygame library
        pygame.init()
        pygame.mouse.set_visible(False)

        # Print a list of all available fonts
        #print(pygame.font.get_fonts())

        #theFont1=pygame.font.Font(None,105)

        self.fontLabel=pygame.font.Font('fonts/Malter Sans Demo2.otf',72)
        self.fontValue=pygame.font.Font('fonts/Malter Sans Demo2.otf',72)
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


    def updateDisplayLoop(self):

        done = False
        while not done:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    break
                    
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    done = True
                    break

            self.screen.fill((0,0,0))

            outsideTemperature = 32.0
            insideTemperature = 68.0
            windSpeed = 0.0
            windGust = 2.0

            self.updateTime(80,60)

            self.updateInsideTemperature(80, 200, insideTemperature)

            self.updateOutsideTemperature(80, 300, outsideTemperature)
            self.updateWind(370, 300, windSpeed, windGust)

            pygame.display.update()

            # Update interval (fps)
            self.clock.tick(2)

 
    def updateTime(self, timeDisplayX: int, timeDisplayY: int):


        epochNow = time.time()
        now = time.localtime(epochNow)
        halfSecond = (epochNow % 1) >= 0.5
        #print (epochNow, halfSecond)

        if halfSecond:
            theTime=time.strftime("%H:%M", now)
        else:
            theTime=time.strftime("%H~%M", now)

        ampm=time.strftime("%p", now)

        theTime2 = "18:59"

        if theTime.startswith('0'):
            theTime = theTime.replace('0', ' ', 1)



        # Time (HH:MM)
        #text_width, text_height = theFont1.size(str(theTime))
        timeText=self.fontValue.render(str(theTime), True, colorRed, (0,0,0))
        timeText_width = timeText.get_width()
        timeText_height = timeText.get_height()
        self.screen.blit(timeText, (timeDisplayX,timeDisplayY))

        # AM/PM 
        ampmText=self.fontSmall.render(str(ampm), True, colorRed, (0,0,0))
        ampmText_width = ampmText.get_width()
        ampmText_height = ampmText.get_height()
        self.screen.blit(ampmText, (timeDisplayX+timeText_width-ampmText_width, timeDisplayY-ampmText_height+5))

    def updateOutsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature
        displayXValueOffset = 150
        label = "Out:"
        labelText=self.fontValue.render(label, True, colorRedLabel, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, colorRed, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))

        degreeSymbolText=self.fontSmall.render(str("°"), True, colorRed, (0,0,0))
        degreeSymbolText_width = degreeSymbolText.get_width()
        degreeSymbolText_height = degreeSymbolText.get_height()
        self.screen.blit(degreeSymbolText, (displayX+displayXValueOffset+valueText_width+4, displayY+10))

    def updateInsideTemperature(self, displayX: int, displayY: int, temperature: float):
        # Temperature
        displayXValueOffset = 150
        label = "In:"
        labelText=self.fontValue.render(label, True, colorRedLabel, (0,0,0))
        self.screen.blit(labelText, (displayX,displayY))

        formattedValue = "{:.0f}".format(temperature)
        valueText=self.fontValue.render(formattedValue, True, colorRed, (0,0,0))
        valueText_width = valueText.get_width()
        valueText_height = valueText.get_height()
        self.screen.blit(valueText, (displayX + displayXValueOffset, displayY))

        degreeSymbolText=self.fontSmall.render(str("°"), True, colorRed, (0,0,0))
        degreeSymbolText_width = degreeSymbolText.get_width()
        degreeSymbolText_height = degreeSymbolText.get_height()
        self.screen.blit(degreeSymbolText, (displayX+displayXValueOffset+valueText_width+4, displayY+10))


    def updateWind(self, windDisplayX: int, windDisplayY: int, windSpeed: float, windGust: float ):
        # Wind
        formattedWind = "{:.0f}-{:.0f}".format(windSpeed, windGust)
        tempText=self.fontValue.render(formattedWind, True, colorRed, (0,0,0))
        tempText_width = tempText.get_width()
        tempText_height = tempText.get_height()
        self.screen.blit(tempText, (windDisplayX,windDisplayY))
        mphText=self.fontSmall.render(str("mph"), True, colorRed, (0,0,0))
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


colorWhite = (255, 255, 255)
colorGray = (163, 163, 163)
colorRed = (209, 79, 79)
colorBlue = (82, 116, 227)
colorGreen = (72, 181, 94)

colorRedLabel = darken_color(colorRed, 0.5)


def main():
    """
    The main function
    :return:
    """
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")



    display = HdmiDisplay()
    display.updateDisplayLoop()

    print("Existing app...")
    pygame.quit()
    exit()


if __name__ == '__main__':
    main()

