# Docs: https://www.pygame.org/docs/ref/display.html

# AnyBeam Pico Mini Portable Pocket
# Resolution: 720p = 1280 x 720, aspect ratio: 16:9


import time,pygame
#initialize pygame library
pygame.init()
pygame.mouse.set_visible(False)

# Print a list of all available fonts
#print(pygame.font.get_fonts())

theFont1=pygame.font.Font(None,105)

theFont2=pygame.font.Font('fonts/Novus-Regular.otf',72)

theFont3=pygame.font.Font('fonts/Malter Sans Demo.otf',72)



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
        
    
    theTime=time.strftime("Time: %H:%M:%S ", time.localtime())
    timeText=theFont1.render(str(theTime), True,(255,255,255),(0,0,0))
    screen.blit(timeText, (80,60))

    timeText2=theFont2.render(str(theTime), True,(255,255,255),(0,0,0))
    screen.blit(timeText2, (80,160))

    timeText3=theFont3.render(str(theTime), True,(255,255,255),(0,0,0))
    screen.blit(timeText3, (80,260))


    # Example of getting text width
    #screen.blit(text, (320 - text.get_width() // 2, 240 - text.get_height() // 2))

    #pygame.display.flip()
    pygame.display.update()
    clock.tick(1)
 
print("Existing app...")
pygame.quit()
exit()