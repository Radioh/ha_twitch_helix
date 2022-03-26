import logging
import voluptuous as vol
from twitchAPI.twitch import Twitch, AuthScope
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity, ENTITY_ID_FORMAT
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

ATTR_GAME = "game"
ATTR_TITLE = "title"
ATTR_SUBSCRIPTION = "subscribed"
ATTR_SUBSCRIPTION_GIFTED = "subscription_is_gifted"
ATTR_FOLLOW = "following"
ATTR_FOLLOW_SINCE = "following_since"
ATTR_FOLLOWERS_COUNT = "followers"
ATTR_VIEWS = "viewers"
ATTR_TOTAL_VIEWS = "channel_views"
ATTR_THUMBNAIL = "thumbnail_url"

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_OWN_CHANNEL = "own_channel"
CONF_CHANNELS = "channels"
CONF_THUMBNAIL_DIMENSIONS = "thumbnail_dimensions"
CONF_API_OPT_OUTS = "api_opt_outs"
CONF_ENTITY_PREFIX = "entity_prefix"

ICON = "mdi:twitch"

STATE_OFFLINE = "offline"
STATE_STREAMING = "streaming"

OPT_OUT_SUBSCRIPTION_USER = "subscription_user"
OPT_OUT_FOLLOW_USER = "follow_user"
OPT_OUT_FOLLOW_TOTAL = "follow_total"
OPT_OUT_STREAM = "stream"

SCAN_INTERVAL = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_OWN_CHANNEL): cv.string,
        vol.Required(CONF_CHANNELS): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_THUMBNAIL_DIMENSIONS) : cv.string,
        vol.Optional(CONF_API_OPT_OUTS) : vol.All(cv.ensure_list, [cv.string]),
        vol.Optional(CONF_ENTITY_PREFIX) : cv.string
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    client_id = config[CONF_CLIENT_ID]
    client_secret = config[CONF_CLIENT_SECRET]
    own_channel = config[CONF_OWN_CHANNEL]
    channels = config[CONF_CHANNELS]
    thumbnail_dimensions = config.get(CONF_THUMBNAIL_DIMENSIONS, None)
    api_opt_outs = config.get(CONF_API_OPT_OUTS, [])
    entity_prefix = config.get(CONF_ENTITY_PREFIX, "")

    user_id = None
    
    scopes = [
        AuthScope.USER_EDIT,
        AuthScope.USER_READ_EMAIL,
        AuthScope.USER_READ_SUBSCRIPTIONS
    ]

    client = Twitch(client_id, client_secret, target_app_auth_scope=scopes)

    try:
        users = client.get_users(logins=[own_channel])
        user_id = users["data"][0]["id"]
    except:
        _LOGGER.error("Error during initial twitch api check. Check config variables")
        return

    twitch_sensors = [TwitchSensor(user_id, channel, client, thumbnail_dimensions, api_opt_outs, entity_prefix) for channel in channels]
    add_entities(twitch_sensors, True)

class TwitchSensor(SensorEntity):
    def __init__(self, user_id, channel, client, thumbnail_dimensions, api_opt_outs, entity_prefix):
        self.entity_id = ENTITY_ID_FORMAT.format(entity_prefix + channel)
        self._client = client
        self._user_id = user_id
        self._channel = channel
        self._channel_id = None
        self._state = None
        self._preview = None
        self._game = None
        self._title = None
        self._subscription = None
        self._follow = None
        self._name = None
        self._viewers = None
        self._total_views = None
        self._thumbnail_url = None
        self._thumbnail_dimensions = thumbnail_dimensions
        self._api_opt_outs = api_opt_outs

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def entity_picture(self):
        """Return preview of current game."""
        return self._preview

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attr = dict()
        
        if (self._subscription):
            attr.update(self._subscription)

        if (self._follow):
            attr.update(self._follow)

        attr.update({ATTR_TOTAL_VIEWS: self._total_views})
        
        if self._state == STATE_STREAMING:
            attr.update({
                ATTR_GAME: self._game,
                ATTR_TITLE: self._title,
                ATTR_VIEWS: self._viewers,
                ATTR_THUMBNAIL: self._thumbnail_url
            })

        return attr

    @property
    def unique_id(self):
        """Return unique ID for this sensor."""
        return self._channel

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Update device state."""
        
        # Broadcast user
        broadcast_users = self._client.get_users(logins=[self._channel])
        broadcast_user = broadcast_users["data"][0]
        
        self._channel_id = broadcast_user["id"]
        self._preview = broadcast_user["profile_image_url"]
        self._name = broadcast_user["display_name"]
        self._total_views = broadcast_user["view_count"]

        # Stream
        if (OPT_OUT_STREAM not in self._api_opt_outs):
            try:
                streams = self._client.get_streams(user_id=[self._channel_id])
                stream = streams["data"][0]

                self._game = stream["game_name"]
                self._title = stream["title"]
                self._viewers = stream["viewer_count"]
                self._state = STATE_STREAMING
                self._thumbnail_url = stream["thumbnail_url"]

                if (self._thumbnail_dimensions is not None):
                    self._thumbnail_url = self._thumbnail_url.replace("{width}x{height}", self._thumbnail_dimensions)
            except:
                self._state = STATE_OFFLINE

        # Subscription
        if (OPT_OUT_SUBSCRIPTION_USER not in self._api_opt_outs):
            try:
                subscriptions = self._client.check_user_subscription(broadcaster_id=self._channel_id, user_id=self._user_id)
                subscription = subscriptions["data"][0]
                
                self._subscription = {
                    ATTR_SUBSCRIPTION: True,
                    ATTR_SUBSCRIPTION_GIFTED: subscription["is_gift"]
                }
            except:
                self._subscription = {
                    ATTR_SUBSCRIPTION: False, 
                    ATTR_SUBSCRIPTION_GIFTED: False
                }

        # Follow - User to streamer    
        if (OPT_OUT_FOLLOW_USER not in self._api_opt_outs):
            try:
                follows = self._client.get_users_follows(from_id=self._user_id, to_id=self._channel_id)
                follow = follows["data"][0]

                self._follow = {
                    ATTR_FOLLOW: True,
                    ATTR_FOLLOW_SINCE: follow["followed_at"]
                }
            except:
                self._follow = {
                    ATTR_FOLLOW: False,
                    ATTR_FOLLOW_SINCE: None
                }

        # Follow - Total follows
        if (OPT_OUT_FOLLOW_TOTAL not in self._api_opt_outs):
            try:
                total_follows = self._client.get_users_follows(to_id=self._channel_id,first=1)
                
                if (self._follow):
                    self._follow[ATTR_FOLLOWERS_COUNT] = total_follows["total"]
                else:    
                    self._follow = {
                        ATTR_FOLLOWERS_COUNT : total_follows["total"]
                    }
            except:
                if (self._follow is not None):
                    self._follow[ATTR_FOLLOWERS_COUNT] = None

