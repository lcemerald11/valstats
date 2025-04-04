import discord
from discord import app_commands
import requests
from bs4 import BeautifulSoup


# Define the slash command
class TeamCommand:
    def __init__(self, tree: app_commands.CommandTree):
        @tree.command(name="hello", description="Say hello!")
        @app_commands.describe(
            name="Team name",
            circuit= "VCT, Game Changers.."
        )
        async def hello(interaction: discord.Interaction, name: str, circuit: str):
            results = search_teams(name)
            print(results)
            await interaction.response.send_message(f"Hello, " + results[0][0] + " " + results[0][1])  


def search_teams(team_query):
    url = f"https://www.vlr.gg/search/?q={team_query}&type=all"
    headers = {
        "User-Agent": "Mozilla/5.0"  # Helps avoid being blocked
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    teams = []

    # Search results are under divs with class 'search-item-team'
    team_id = 0
    low_id = 99999
    for team_div in soup.select(".wf-module-item.search-item"):
        name_tag = team_div.select_one(".search-item-title")  # Team name
        link_tag = team_div["href"]
        

        if name_tag and "team" in link_tag:
            team_id = int(link_tag[6:link_tag.find("/", 6)])
            name = name_tag.text.strip()
            link = "https://www.vlr.gg" + team_div["href"]
            if (low_id >= team_id):
                low_id = team_id
                teams.insert(0,(name, link))
            else:
                teams.append((name, link))

    return teams