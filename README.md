# wharf

An minimal discord api wrapper that allows **you** to do what you want to do
<br>
Support Server: https://discord.gg/gJdY2AQxJY



## Aint this just another discord.py or hikari clone?
I see how you can think that but no. wharf was made entirely from scratch but the libraries do share stylistic choices. wharf is meant to be as minimal as possible whilst are being beginner-friendly. basically a mix of hikari and discord.py into one brand new made from scratch library!

### What events are there/Whats their names?
You can find a list of all gateway events at [The discord docs](https://discord.com/developers/docs/topics/gateway-events)!<br>
we use the gateway event names discord gives us in the docs such as ``message_create``, ``guild_create``, or ``interaction_create``.
We support all events but some of the events use the raw json from the gateway instead of proper models **for now**.
