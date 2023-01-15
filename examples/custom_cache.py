# Here in this example, ill show how you can make a custom cache object by just subclassing wharf.impl.Cache!

import wharf  # First you import wharf obviously


class MyCache(wharf.impl.Cache):  # Then now you can create your subclass of ``wharf.impl.Cache``
    def __init__(
        self, http: wharf.HTTPClient
    ):  # This is needed but dw about having to access your bot classes http, this gets auto filled in internally!
        # The http arg in the init should ALWAYS be positional and not a kwarg
        super().__init__(http)  # Gotta do a super init so the class can actually function

    def get_user(self, user: int):
        print(self.users.get(user))  # Now you can overwrite any function and do anything you want!


# Now you can actually start defining your bot!
bot = wharf.Bot(
    token="SomeToken", intents=wharf.Intents.all(), cache=MyCache
)  # You dont have to initalize the cache here as this is already done internally!


@bot.listen(
    "ready"
)  # Now you can do anything as usual, you can even subclass wharf.Bot, anything, it doesn't matter after you insert your cache into wharf.Bot!
async def ready():
    print("Im Ready!")


bot.run()
