#### ha_twitch_helix

# Intro
Custom Component to integrate with Twitch helix api

It looks like the original Twitch sensor integration uses the Twitch V5 API which is deprecated.
New Twitch apps doesn't seem to work with this deprecated API.

This component does mostly the same as the original integration found here (https://www.home-assistant.io/integrations/twitch/), but the underlying implementation is using the Twitch Helix API.


# Prerequisites
This component requires a Twitch developer app which can be setup here: https://dev.twitch.tv/console/apps 


# Installation
Configuration requires channel ids.
Channel ids can be found by visiting this website and enter the display name of the Twitch channel: https://www.streamweasels.com/support/convert-twitch-username-to-user-id/

example of setup in configurations.yaml

![](configuration.JPG)

`client_id`: client id acquired in Twitch developer app  
`client_secret`: client secret acquired in Twitch developer app  
`own_channel_id`: channel id of your twitch channel. Used to check if channels are followed and subscribed to.  
`channel_ids`: list of channel ids to create entities for  

Channel ids can be resolved here by Twitch username: https://www.streamweasels.com/support/convert-twitch-username-to-user-id/

# Examples
![](example1.JPG)
![](example2.JPG)
