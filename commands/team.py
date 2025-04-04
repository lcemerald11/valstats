import discord
from discord import app_commands
import requests
from bs4 import BeautifulSoup
from colorthief import ColorThief
from io import BytesIO

# Define the slash command
class TeamCommand:
    def __init__(self, tree: app_commands.CommandTree):
        @tree.command(name="hello", description="Say hello!")
        @app_commands.describe(
            name="Team name",
            search= "Place in search"
        )
        async def hello(interaction: discord.Interaction, name: str, search: int):
            results = search_teams(name)
            if (results == [] or len(results)<search):
                await interaction.response.send_message(f'Team or index entered does not exist. Please enter valid data.')  
            # print(results)
            players = find_players(results[search-1][1])
            emed = createEmbed(results[search-1],players)
            await interaction.response.send_message(embed=emed)  


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
        img = team_div.find("img")["src"]
        

        if name_tag and "team" in link_tag:
            team_id = int(link_tag[6:link_tag.find("/", 6)])
            name = name_tag.text.strip()
            link = "https://www.vlr.gg" + team_div["href"]
            if ("//" in img):
                img = "https:" + img
            else:
                img = "https://www.vlr.gg" + img
            # if (low_id >= team_id):
            #     low_id = team_id
            #     teams.insert(0,[name, link, img])
            # else:
            #     teams.append([name, link, img])
            teams.append([name, link, img])
    print(teams)
    return teams

def find_players(url):
    players = []
    player_name = ""
    gamer_name = ""
    game_tag = ""
    name_tag = ""
    role = ""
    flag = ""

    headers = {
        "User-Agent": "Mozilla/5.0"  # Helps avoid being blocked
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    

    for player_div in soup.select(".team-roster-item"):
        game_tag = player_div.select_one(".team-roster-item-name-alias")  # Team name
        name_tag = player_div.select_one(".team-roster-item-name-real")  # Team name
        role = player_div.select_one(".team-roster-item-name-role")
        flag = "flag_" + player_div.find("i")["class"][1][4:]
        if game_tag:
            gamer_name = game_tag.text.strip()
        if name_tag:
            player_name = name_tag.text.strip()

        
        if not role:
            if not player_div.select_one(".fa-star"):
                role_name = "Player" 
            else:
                role_name = "IGL"
        else:
            role_name = role.text.strip()
        if flag == "flag_un":
            flag = "white_large_square"
        players.append([gamer_name,player_name,role_name,flag])
    return players

def createEmbed(team, players):
    count=0
    postPlayerCheck = True
    url = team[1]
    headers = {
        "User-Agent": "Mozilla/5.0"  # Helps avoid being blocked
    }

    responseURL = requests.get(url, headers=headers)
    soup = BeautifulSoup(responseURL.text, 'html.parser')
    #team-header-country
    team_country = soup.select_one(".team-header-country").text.strip()
    flag_emote = ":flag_" + ((soup.select_one(".team-header-country")).find("i"))["class"][1][4:] + ":"
    team_links = []
    links_dev = soup.find('div', class_='team-header-links')

    for links in links_dev.find_all("a"):
        L = links["href"]
        if (L != ""):  
            team_links.append(links["href"])
        else:
            team_links.append("-")

    
    response = requests.get(team[2]) 
    image_bytes = BytesIO(response.content)
    color_thief = ColorThief(image_bytes)

    embed = discord.Embed(
        title=f"{team[0]}",
        color=discord.Colour.from_rgb(color_thief.get_color(quality=1)[0],color_thief.get_color(quality=1)[1],color_thief.get_color(quality=1)[2]),
        url=team[1]
    )

    embed.set_author(name="Made By Val-Bot", icon_url="attachment://IMG_4298.jpg")
    embed.set_thumbnail(url=team[2])
    embed.add_field(name= flag_emote + " " + team_country, value= team_links[0], inline=False)
    for player in players:
        cond = ((player[2] not in ["Player", "Sub", "Inactive","IGL"]) and postPlayerCheck)  
        if cond:
            embed.add_field(name="**Staff: **", value = "\n\n", inline=False)
            embed.add_field(name= player[0] + " :" + player[3] + ":", value= "```" + "Name: \n" + player[1] + "\n\nRole: " + player[2].title() + "```", inline=True)
            postPlayerCheck = False
        else:
            embed.add_field(name= player[0] + " :" + player[3] + ":", value= "```" + "Name: \n" + player[1] + "\n\nRole: " + player[2].title() + "```", inline=True)
        count+=1
    
    embed.set_author(name="Bot Created by Chunkymydunky",)
    embed.set_footer(text= "Val-Stats v1.0")
    embed.timestamp = discord.utils.utcnow()

    return embed