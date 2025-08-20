import discord


def build_historical_figure_embed(data, wiki_data):
    description = wiki_data["extract"][:4096]

    name = data["name"]
    title = data["title"]

    information = data["info"]

    born = information.get("born", "Unknown")
    died = information.get("died", "Unknown")
    house = information.get("house", "Unknown")
    reign = information.get("reign", "Unknown")
    dynasty = information.get("dynasty", "Unknown")
    religion = information.get("religion", "Unknown")
    successor = information.get("successor", "Unknown")
    coronation = information.get("coronation", "Unknown")

    embed = discord.Embed(
        title=name, description=description, color=discord.Color.blue()
    )

    embed.add_field(name="Title:", value=title, inline=False)
    embed.add_field(name="Born:", value=born, inline=False)
    embed.add_field(name="Died:", value=died, inline=False)
    embed.add_field(name="House:", value=house, inline=False)
    embed.add_field(name="Reign:", value=reign, inline=False)
    embed.add_field(name="Dynasty:", value=dynasty, inline=False)
    embed.add_field(name="Religion:", value=religion, inline=False)
    embed.add_field(name="Successor:", value=successor, inline=False)
    embed.add_field(name="Coronation:", value=coronation, inline=False)

    return embed
