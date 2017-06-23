import os
import discord
import asyncio
from discord.ext import commands
from cogs.utils.dataIO import dataIO


class Away:
    """Le away cog"""
    def __init__(self, bot):
        self.bot = bot
        self.data = dataIO.load_json('data/away/away.json')

    async def listener(self, message):
        tmp = {}
        for mention in message.mentions:
            tmp[mention] = True
        if message.author.id != self.bot.user.id:
            for author in tmp:
                if author.id in self.data:
                    try:
                        avatar = author.avatar_url if author.avatar else author.default_avatar_url
                        if self.data[author.id]['MESSAGE']:
                            em = discord.Embed(description=self.data[author.id]['MESSAGE'], color=discord.Color.blue())
                            em.set_author(name='{} is currently away'.format(author.display_name), icon_url=avatar)
                        else:
                            em = discord.Embed(color=discord.Color.blue())
                            em.set_author(name='{} is currently away'.format(author.display_name), icon_url=avatar)
                        await self.bot.send_message(message.channel, embed=em)
                    except:
                        if self.data[author.id]['MESSAGE']:
                            msg = '{} is currently away and has set the following message: `{}`'.format(author.display_name, self.data[author.id]['MESSAGE'])
                        else:
                            msg = '{} is currently away'.format(author.display_name)
                        await self.bot.send_message(message.channel, msg)

    @commands.command(pass_context=True, name="away")
    async def _away(self, context, *message: str):
        """Tell the bot you're away or back."""
        author = context.message.author
        to_delete = []
        channel = context.message.channel
        server = context.message.server
        author = context.message.author
        is_bot = self.bot.user.bot
        has_permissions = channel.permissions_for(server.me).manage_messages
        to_delete.append(context.message)
        if author.id not in self.data: #author *is not* afk
            self.data[context.message.author.id] = {}
            if len(str(message)) < 256:
                self.data[context.message.author.id]['MESSAGE'] = ' '.join(context.message.clean_content.split()[1:])
            else:
                self.data[context.message.author.id]['MESSAGE'] = True
            botmsg = 'You\'re now set as away.'
            print('afk on')
        else: #author **is** afk
            del self.data[author.id]
            botmsg = 'You\'re now back.'
            to_delete.append(msg)
            print('afk off')
        await self.bot.say(botmsg)
        await asyncio.sleep(5)

        async for botmsg in self.bot.logs_from(channel, limit=2):
            to_delete.append(botmsg)

        # if not has_permissions:
        #     await self.bot.say('I am not allowed to delete messages. Please advise your server administrator.')
        #     return

        try:
            await self.slow_deletion(to_delete)
            print('messages deleted')
        except:
            print('messages not deleted')
        dataIO.save_json('data/away/away.json', self.data)

        # try:
        #     await  client.purge_from(channel, limit=1, check=is_me)
        # except:
        #     #added manage messages permission
        #     await self.bot.say('Could not tidy up messages.')

    async def slow_deletion(self, messages):
        for message in messages:
            try:
                await self.bot.delete_message(message)
            except:
                pass

def check_folder():
    if not os.path.exists('data/away'):
        print('Creating data/away folder...')
        os.makedirs('data/away')


def check_file():
    f = 'data/away/away.json'
    if not dataIO.is_valid_json(f):
        dataIO.save_json(f, {})
        print('Creating default away.json...')


def setup(bot):
    check_folder()
    check_file()
    n = Away(bot)
    bot.add_listener(n.listener, 'on_message')
    bot.add_cog(n)
