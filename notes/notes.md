

# Intro

The following are my notes to date regarding the AnyBeam projector using a Raspberry Pi 4b. 

UPDATE as of 12/17/2020, AnyBeam verified that there is an issue with the HDMI output on the Raspberry Pi 4 where it produces jittering/flickering. This is not an AnyBeam projector issue but flakey HDMI output from the RPi4b.  Hopefully a future update to the RPi4b will fix the HDMI output.

# Background

The plan was to use a raspberry Pi 4b to generate a display that will be output via HDMI and then displayed via a projector on the ceiling of the bedroom.

I was worried about having it powered on 8-12 hours per night but I wasked AnyBeam who said that it would be fine.

I puchased the AnyBeam Pico Mini Portable Pocket Projector on 11/23/2020.


# Issues

I have encountered the following issues while using the AnyBeam projector connected to Raspberry Pi 4b


## Display freezes

As often as 3 times per night (12 hour period), the display will freeze.  What I mean is the projected image that contains the time, is no longer updated and shows a frozen-in-time display.  Two ways to fix the issue:
1. Power cycling the AnyBeam projector (remove / restore the USB power).
2. Pull the HDMI cable and re-attach

I verified that the image is still updated from the Raspberry Pi by viewing its raw framebuffer via a ssh.  I also attached the HDMI cable from Raspberry Pi to an LCD dislay and everything was updating.  

This issue is a show stopper as you can't have a time display that randomly freezes which results in showing a time that is no longer accurate.  Any AnyBeam firmware update fixe this??  I'm hoping so.

## White horizonal line

A white horizontal line (about 5-10 pixels high) shows on top of content.  These white lines flicker so its not solid.  This has happened twice over 4 days.  Power cycling AnyBeam fixed.  I forgot to take a picture of the issue.


## Black horizonal line

A black horizontal line (about 5-10 pixels high) shows on top of content.  This has happened 3 times over 4 days.  Power cycling AnyBeam fixed.

Picture of issue (ignore the bad photo quality)
![black lines issue](2020_12_03_horizontal_line_issue.jpg)

Picture after power cycle of AnyBeamn (ignore the bad photo quality)
![black lines reboot fixed](2020_12_03_horizontal_line_after_reboot_fix.jpg)

## Occasional flash

Occasional flash for less then a second of something white (bright) - Notice it maybe once per night. Maybe its losing HDMI signal for a faction of a second?

## Lost HDMI signal for a few seconds

Lost signal in middle of night and showed the connect Anybeam screen for 4 seconds or so.  It auto-reconnected.  This has occured once (that I noticed) in the last 4 days.  The problem is this screen is VERY bright when you are sleeping in a completely dark room.

Here is the screen you see for a few seconds:
![disconnect screen](disconnected_screen.jpg)


## Very faint bottom line

There is a very faint white (gray?) line at the bottom of the display -- seems to be after the 720th row of the display.  After adjusting many setting in software with no fix, I just put some black electrical tape on the very bottom of the lens.  This masked off the line.  No a big deal and it was an easy workaround.

# Attempted fixes

The following changes were made in an attempt to fix the issue(s)

1. Replaced the USB power supply and cable to the AnyBeam projector.
1. Replaced the Raspberry Pi (hardware)
1. Changed to pygame fps from 2 to 30.
1. Replaced the micro-HDMI cable.

None of the above changes have had any effect on these issues.



