# In this example, i will show a basic plugin
import wharf

# First define the plugin
myplugin = wharf.Plugin(
    name="hi", description="hi!!"
)  # You can name it whatever you want


@myplugin.listen(
    "message_create"
)  # You can define listeners using the listen decorator
async def message_create(message: wharf.Message):
    if message.content == "ping":
        await message.send("Pong!")


bot = wharf.Bot(token="SomeToken", intents=wharf.Intents.MESSAGE_CONTENT)

bot.add_plugin(myplugin)  # You add plugins using the add_plugin function in your bot

bot.load_extension(
    "basic_ext"
)  # You can also load extensions, which are also just plugins inside other files! go to basic_ext.py to see

bot.run()
