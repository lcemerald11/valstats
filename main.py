import discord
from discord.ext import commands
import config

# Import your command class
from commands.team import TeamCommand

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    # Register slash commands
    TeamCommand(client.tree)
    await client.tree.sync()
    print(f"Bot logged in as {client.user} and slash commands synced.")

# Start bot
if __name__ == "__main__":
    client.run(config.BOT_TOKEN)
