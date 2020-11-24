# Docs: https://www.pygame.org/docs/ref/display.html

# AnyBeam Pico Mini Portable Pocket
# Resolution: 720p = 1280 x 720, aspect ratio: 16:9


import time,pygame
#initialize pygame library
pygame.init()
pygame.mouse.set_visible(False)

# Print a list of all available fonts
#print(pygame.font.get_fonts())

#theFont1=pygame.font.Font(None,105)

theFont1=pygame.font.Font('fonts/Malter Sans Demo2.otf',72)
font1Small=pygame.font.Font('fonts/Malter Sans Demo2.otf',24)

theFont2=pygame.font.Font('fonts/DS-DIGII2.otf',80)
theFont3=pygame.font.Font('fonts/DS-DIGIT2.otf',80)



clock = pygame.time.Clock()
screen = pygame.display.set_mode((1280, 720))
screen.fill((0,0,0))
pygame.display.flip()
pygame.display.set_caption('Pi Time')
# Clear screen

print(pygame.display.Info())


done = False
while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
            break
            #quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
            break
            #quit()
        
    epochNow = time.time()
    now = time.localtime(epochNow)
    halfSecond = (epochNow % 1) >= 0.5
    print (epochNow, halfSecond)

    if halfSecond:
        theTime=time.strftime("%H:%M", now)
    else:
        theTime=time.strftime("%H~%M", now)

    ampm=time.strftime("%p", now)

    theTime2 = "18:59"

    if theTime.startswith('0'):
        theTime = theTime.replace('0', ' ', 1)

    screen.fill((0,0,0))

    colorWhite = (255, 255, 255)
    colorGray = (163, 163, 163)
    colorRed = (209, 79, 79)
    colorBlue = (82, 116, 227)
    colorGreen = (72, 181, 94)

    timeDisplayX = 80
    timeDisplayY = 60

    # Time (HH:MM)
    #text_width, text_height = theFont1.size(str(theTime))
    timeText=theFont1.render(str(theTime), True, colorRed,(0,0,0))
    timeText_width = timeText.get_width()
    timeText_height = timeText.get_height()
    screen.blit(timeText, (timeDisplayX,timeDisplayY))

    # AM/PM 
    ampmText=font1Small.render(str(ampm), True, colorRed,(0,0,0))
    ampmText_width = ampmText.get_width()
    ampmText_height = ampmText.get_height()
    screen.blit(ampmText, (timeDisplayX+timeText_width-ampmText_width,timeDisplayY-ampmText_height+5))



    # Test
    timeText=theFont2.render(str(theTime), True,colorRed,(0,0,0))
    screen.blit(timeText, (80,160))
 

    # Test
    timeText=theFont3.render(str(theTime), True,colorRed,(0,0,0))
    screen.blit(timeText, (80,260))
 


    # Example of getting text width
    #screen.blit(text, (320 - text.get_width() // 2, 240 - text.get_height() // 2))

    #pygame.display.flip()
    pygame.display.update()
    clock.tick(2)
 
print("Existing app...")
pygame.quit()
exit()