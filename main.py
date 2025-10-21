import discord
import os
import requests # Library to make HTTP requests to the website
from bs4 import BeautifulSoup # Library to parse the HTML from the website
from dotenv import load_dotenv # Library to load our secret token

# Load the secret token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up the bot with the necessary intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# This event runs once when the bot successfully connects to Discord
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    print('Bot is ready to go!')

# This defines a slash command that users can run
@bot.slash_command(name="events", description="Fetches events to post to Discord.")
async def events(ctx):
    # Let the user know the bot is working on the request
    await ctx.defer()

    # --- 1. WEB SCRAPING PART ---
    # The URL of the website we want to scrape
    url = "https://www.meetup.com/find/?location=us--ma--Boston&source=EVENTS&keywords=ai&dateRange=this-week"
    
    try:
        # Send a request to the website
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Parse the website's HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        # print("=======", soup)

        # --- 2. PREPARING THE INFORMATION ---
        # Find the first event container on the page. 
        # We find this by "inspecting element" in a web browser.
        events_element = soup.select('div[data-recommendationsource]')[0]
        # print("==== SOUP ====", events_element)

        if events_element:
            # Extract the items we want from the event
            title   = events_element.find('h3').get_text(strip=True)
            # print("==== TITLE ===", title)
            link    = events_element.find('a[href]')
            date    = events_element.find('time').get_text(strip=True)
            author  = events_element.select('h3 + div > div:first-child')[0].get_text(strip=True)


            # --- 3. POSTING TO DISCORD ---
            # Create a nicely formatted embed
            embed = discord.Embed(
                title = title,
                url = link,
                description = "Dummy description for event post",
                timestamp = date,
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"— {author}")

            # Send the embed back as the response
            await ctx.followup.send(embed=embed)
        else:
            await ctx.followup.send("Sorry, I couldn't find an event to share.")

    except requests.exceptions.RequestException as e:
        print(f"Error during web request: {e}")
        await ctx.followup.send("Sorry, I couldn't connect to the event website.")


# This is the last line: it runs the bot with your secret token
bot.run(TOKEN)