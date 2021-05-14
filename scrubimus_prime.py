import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
import random

# Constants
prefix = '!'
dbName = 'Scrubhub'
collectionName = 'ScrubimusPrime'

# Settings
token = open("token.txt", "r").read()
mongoUrl = open("mongoConnectionString.txt", "r").read()

# Objects
bot = commands.Bot(command_prefix=prefix)
cluster = MongoClient(mongoUrl)
db = cluster[dbName]
collection = db[collectionName]


class Listeners(commands.Cog):
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user} has connected to Discord!')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        try:
            if ctx.author.name.lower() == bot.user.name.lower():
                return

            if not str(ctx.content).startswith(prefix):
                if random.randint(0, 9) == 0:
                    Economy.add_coins(ctx.author.id, 1)
                    await ctx.channel.send('Coin added!')
                return

        except Exception as ex:
            print(f'Error occurred: ' + str(ex))
            await ctx.channel.send('Error occurred: ' + str(ex))
            raise Exception(ex)


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self, ctx, arg):
        await ctx.send(arg)

    @commands.command()
    async def roll(self, ctx, dice: str):
        """Rolls a dice in NdN format."""
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send('Format has to be in NdN!')
            return

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    @commands.command(description='For when you wanna settle the score some other way')
    async def choose(self, ctx, *choices: str):
        """Chooses between multiple choices."""
        await ctx.send(random.choice(choices))


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='coin', aliases=['coins', 'c'], help='Get coins')
    async def _coin(self, ctx):
        self.add_coins(self, ctx.author.id, 1)
        await ctx.send('Coin added!')

    @commands.command(name='balance', aliases=['bal', 'b'], help='See your balance')
    async def _balance(self, ctx):
        balance = self.check_balance(ctx.author.id)
        await ctx.send('Current balance: ' + str(balance))

    def check_balance(self, userid):
        query = {"_id": userid, "coins": {'$exists': True, '$ne': False}}
        collection_count = collection.count_documents(query)
        if collection_count == 0:
            Account.create_profile(userid)

        user = collection.find(query)

        for result in user:
            balance = result["coins"]
        return int(balance)

    def add_coins(self, userid, coins):
        balance = self.check_balance(userid)
        balance += coins
        collection.update_one({"_id": userid}, {"$set": {"coins": balance}})


class Account(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='resetaccount')
    async def _resetaccount(self, ctx):
        if await General.ask_user(ctx, 'Are you sure you want to reset your account? (y/n)'):
            self.reset_profile(self, ctx.author.id)
            await ctx.send('Account is reset!')

    def check_profile(self, userid):
        query = {"_id": userid}
        if collection.count_documents(query) == 0:
            self.create_profile(self, userid)

    def create_profile(self, userid):
        self.reset_profile(userid)
        post = {"_id": userid, "coins": 0}
        collection.insert_one(post)

    def reset_profile(self, userid):
        collection.delete_many({"_id": userid})


class General(commands.Cog):
    async def ask_user(self, ctx, question):
        await ctx.channel.send(question)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        reply = await self.bot.wait_for('message', check=check, timeout=30)
        try:
            if reply.content.lower() in ('y', "yes"):
                return True
            else:
                return False
        except Exception as error:
            return False


def setup(bot1):
    bot1.add_cog(Listeners(bot1))
    bot1.add_cog(General(bot1))
    bot1.add_cog(TestCog(bot1))
    bot1.add_cog(Economy(bot1))
    bot1.add_cog(Account(bot1))


bot.run(token)
