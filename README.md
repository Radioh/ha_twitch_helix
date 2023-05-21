# ha_twitch_helix

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Intro

Custom Component to integrate with Twitch helix api.

## Prerequisites

This component requires a Twitch developer app which can be setup here: https://dev.twitch.tv/console/apps
Only APP authentication is required for the used API endpoints. Hence, you only need to provvide the client_id and client_secret from the app you create in the Twitch Console.

## Installation

### Using HACS

You can install this custom component using the Home Assistant Community Store (HACS). Click the top right corner in HACS and add this repository to the "Custom repositories" - https://github.com/Radioh/ha_twitch_helix/. After adding the repository you You should be able to search for "Twitch Helix" and install it.
If you don't have HACS installed and want to know more you can read about it at <https://hacs.xyz/>

### Installing manually

Download the latest release files and copy the "twitch_helix" folder into your "config/custom_components" folder.

### Configuration

This component requires setup in the configuration.yaml file.

example of setup in configurations.yaml

```
sensor:
  - platform: twitch_helix
    client_id: !secret twitch_client_id
    client_secret: !secret twitch_client_secret
    own_channel: my_channel
    thumbnail_dimensions: 320x180
    entity_prefix: Twitch_
    channels:
      - "LIRIK"
      - "Robbaz"
      - "Giantwaffle"
      - "AvoidingThePuddle"
    api_opt_outs:
      # - subscription_user
      # - stream
```

`client_id`: client id acquired in Twitch developer app.\
`client_secret`: client secret acquired in Twitch developer app.\
`own_channel`: channel username of your twitch channel. Used to check if channels are subscribed to.\
`thumbnail_dimensions`: optional parameter. Format is {width}x{height} for thumbnail_url dimensions. Default value is "{width}x{height}" where you need to replace values yourself in the url.\
`entity_prefix`: optional parameter. Prefix to the entity id.\
`channels`: list of channel usernames to create entities for.\
`api_opt_outs`: optional parameter. List of apis calls, which can be opted out of. Consider using this if you have a lot of streamers and is hitting the Twitch API rate limit.\

## Examples

![](example1.JPG)
![](example2.JPG)
