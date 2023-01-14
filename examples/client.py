import wharf

client = wharf.Bot(token="SomeToken", intents=wharf.Intents.all())


@client.listen("ready")
async def ready():
    print("Im ready :D")


@client.listen("message_create")
async def message_create(message):
    if message.content == ".hi":
        await message.send("hi!!! :)")


client.run()
