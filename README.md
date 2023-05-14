# Deprecation Notice
Wharf is now deprecated. I no longer will be working on this library and it might be going fully out of date soon because of the pomelo (username changes)  updates with discord.
<br>
As of 5/13/2023, this library does still work as to my knowledge but i'd say use another api wrapper such a ``Hikari`` or ``Discord.py``.
<br>
You may create a fork of this if you want just as people did with discord.py when it was deprecated back in 2021.

# Wharf

An minimal discord api wrapper that allows **you** to do what you want to do
<br>
If you need any support or want to give us suggestions, please do so by joining out [Support Server](https://discord.gg/gJdY2AQxJY)



# Aint this just another discord.py or hikari clone?
I see how you can think that but no. wharf was made entirely from scratch but the libraries do share stylistic choices. wharf is meant to be as minimal as possible whilst are being beginner-friendly. basically a mix of hikari and discord.py into one brand new made from scratch library!

# What events are there/Whats their names?
You can find a list of all gateway events at [The discord docs](https://discord.com/developers/docs/topics/gateway-events)!<br>
we use the gateway event names discord gives us in the docs such as ``message_create``, ``guild_create``, or ``interaction_create``.
We support all events but some of the events use the raw json from the gateway instead of proper models **for now**.
