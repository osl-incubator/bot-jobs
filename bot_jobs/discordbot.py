import datetime
import os

import discord
import requests
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

client = discord.Client()

API_ROOT = "https://api.github.com"
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
# GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


class MyCog(commands.Cog):
    def __init__(self):
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5.0)
    async def printer(self):
        print(self.index)
        self.index += 1


@tasks.loop(seconds=86400)
async def slow_count():
    # import pdb; pdb.set_trace()

    # for guild in client.guilds:
    #    discord.utils.get(guild.channels, name='channel', category=category)

    channel = [
        ob for ob in client.guilds[0].channels if ob.name == 'dev_tests'
    ][0]

    result = "**Results:**\n"
    result += "\n".join(
        [f"- {k}" for k in get_pull_requests("pytorch", "pytorch")]
    )
    await channel.send(result)
    print(f"Task done at {datetime.datetime.now()}")


@slow_count.after_loop
async def after_slow_count():
    print('task done!')


def get_pull_requests(owner: str, repo: str):
    yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
    yesterday_text = yesterday.strftime("%Y-%m-%d")

    endpoint = f"{API_ROOT}/repos/{owner}/{repo}/pulls"
    params = f"q=created:>={yesterday_text}"
    url = f"{endpoint}?{params}"

    response = requests.get(
        url,
        headers={
            # "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
    )

    result = response.json()
    titles = [r["title"] for r in result]

    # return just for tests for now
    return titles


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    slow_count.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$get-prs"):
        prs = get_pull_requests("pytorch", "pytorch")
        result = "\n".join(prs)
        await message.channel.send(result)


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
