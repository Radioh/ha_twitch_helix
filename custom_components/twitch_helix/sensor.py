import logging
import voluptuous as vol
from twitchAPI.twitch import Twitch, AuthScope
from datetime import timedelta

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
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

CONF_CLIENT_ID = "client_id"
CONF_CLIENT_SECRET = "client_secret"
CONF_OWN_CHANNEL = "own_channel_id"
CONF_CHANNELS = "channel_ids"

ICON = "mdi:twitch"

STATE_OFFLINE = "offline"
STATE_STREAMING = "streaming"

SCAN_INTERVAL = timedelta(seconds=120)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_OWN_CHANNEL): cv.string,
        vol.Required(CONF_CHANNELS): vol.All(cv.ensure_list, [cv.string]),
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    client_id = config[CONF_CLIENT_ID]
    client_secret = config[CONF_CLIENT_SECRET]
    own_channel_id = config[CONF_OWN_CHANNEL]
    channel_ids = config[CONF_CHANNELS]
    user_id = None
    
    scopes = [
        AuthScope.USER_EDIT,
        AuthScope.USER_READ_EMAIL,
        AuthScope.USER_READ_SUBSCRIPTIONS
    ]

    client = Twitch(client_id, client_secret, target_app_auth_scope=scopes)

    try:
        users = client.get_users(user_ids=[own_channel_id])
        user_id = users["data"][0]["id"]
    except:
        _LOGGER.error("Error during initial twitch api check. Check config variables")
        return

    add_entities([TwitchSensor(user_id, channel_id, client) for channel_id in channel_ids], True)

class TwitchSensor(SensorEntity):
    def __init__(self, user_id, channel_id, client):
        self._client = client
        self._user_id = user_id
        self._channel_id = channel_id        
        self._state = None
        self._preview = None
        self._game = None
        self._title = None
        self._subscription = None
        self._follow = None
        self._name = None
        self._viewers = None
        self._total_views = None

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
        
        attr.update(self._subscription)
        attr.update(self._follow)
        attr.update({
            ATTR_TOTAL_VIEWS: self._total_views
        })

        if self._state == STATE_STREAMING:
            attr.update({
                ATTR_GAME: self._game,
                ATTR_TITLE: self._title,
                ATTR_VIEWS: self._viewers
            })

        return attr

    @property
    def unique_id(self):
        """Return unique ID for this sensor."""
        return self._channel_id

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Update device state."""
        
        # Broadcast user
        broadcast_users = self._client.get_users(user_ids=[self._channel_id])            
        broadcast_user = broadcast_users["data"][0]        
        
        self._preview = broadcast_user["profile_image_url"]
        self._name = broadcast_user["display_name"]
        self._total_views = broadcast_user["view_count"]

        # Stream
        try:
            streams = self._client.get_streams(user_id=[self._channel_id])
            stream = streams["data"][0]

            self._game = stream["game_name"]
            self._title = stream["title"]
            self._viewers = stream["viewer_count"]
            self._state = STATE_STREAMING
        except:
            self._state = STATE_OFFLINE

        # Subscription
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
        try:
            total_follows = self._client.get_users_follows(to_id=self._channel_id,first=1)        
            self._follow[ATTR_FOLLOWERS_COUNT] = total_follows["total"]
        except:
            self._follow[ATTR_FOLLOWERS_COUNT] = None

