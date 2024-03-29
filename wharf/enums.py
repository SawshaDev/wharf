from enum import Enum


class Status(Enum):
    online = "online"
    offline = "offline"
    dnd = "dnd"
    idle = "idle"


class InteractionOptionType(Enum):
    string = 3
    integer = 4
    boolean = 5
    user = 6
    channel = 7
    role = 8
    mentionable = 9
    float = 10
    attachment = 11


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
    GROUP_DM = 3

    def __int__(self) -> int:
        return self.value
