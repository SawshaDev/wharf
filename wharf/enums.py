from enum import Enum


class Status(Enum):
    online = "online"
    offline = "offline"
    dnd = "dnd"
    idle = "idle"


class ActivityType(Enum):
    unknown = -1
    playing = 0
    streaming = 1
    listening = 2
    watching = 3
    custom = 4
    competing = 5

    def __int__(self) -> int:
        return self.value


class MessageFlags(Enum):
    CROSSPOSTED = 1 << 0
    IS_CROSSPOST = 1 << 1
    SUPRESS_EMBEDS = 1 << 2
    EPHEMERAL = 1 << 6


class ChannelTypes(Enum):
    # For now these are the most IMPORTANT types, others can be implemented on their own time.

    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2

    def __int__(self) -> int:
        return self.value
