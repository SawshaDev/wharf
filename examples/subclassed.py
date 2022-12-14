# Here in this example will show you how to make a custom subclassed client with custom attributes

import wharf

# Now you can actually start subclassing
class SubclassedClient(wharf.Client):
    def __init__(self, token: str, intents: wharf.Intents): # Gotta make sure to include an __init__!
        super().__init__(token=token, intents=intents)

        # Now we can actually define an attribute
        self.someattribute = "hi there!"

# Now we can make a class instance
client = SubclassedClient(token="SomeToken", intents=wharf.Intents.ALL) # Using all intents just so everything works <3!

@client.listen("ready")
async def ready():
    print(client.someattribute) # Here we print it out, which should say "hi there!"

client.run() 