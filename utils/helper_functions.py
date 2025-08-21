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


def build_event_embed(events, embed):
    for h_event in events[:5]:
        day = h_event.get("day", "?")
        month = h_event.get("month", "?")
        year = h_event.get("year", "?")

        try:
            year_int = int(year)
            if year_int >= 0:
                year_display = str(year_int)
            else:
                year_display = f"{abs(year_int)} BC"
        except (ValueError, TypeError):
            year_display = str(year)

        date = f"{day}/{month}/{year_display}"
        description = h_event.get("event", "No description available")
        embed.add_field(name=date, value=description, inline=False)

    return embed
