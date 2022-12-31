# You can also define plugins in different files like so
# Its the same as in the first example but with two added things

import wharf

plugin = wharf.Plugin(name="MyExt")

@plugin.listen("message_edit")
async def message_edit(msg: wharf.Message):
    print(msg.content)


# These two functions are needed, both involve loading and unloading the plugins!
def load(bot):
    bot.add_plugin(plugin)

def remove(bot):
    bot.remove_plugin(plugin)