import os
import discord
import openai
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the bot token and OpenAI API key from environment variables
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Define intents and create the bot instance
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)


# Function to split a long message into smaller chunks (max 2000 characters)
def split_message(text, max_length=2000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


# Event: Bot is ready and sets a custom status
@bot.event
async def on_ready():
    custom_status = discord.Game(name='✏️"@myname !ask message" to use')
    await bot.change_presence(status=discord.Status.online, activity=custom_status)
    print(f'Logged in as {bot.user.name}')


# Event: Process messages and handle mentions with "!ask" command
@bot.event
async def on_message(message):
    # Ignore messages from bots
    if not message.author.bot and bot.user.mentioned_in(message):
        try:
            # Extract the user message after the mention
            user_message = message.content.split(' ', 1)[1]

            if user_message.startswith('!ask'):
                question = user_message[5:].strip()  # Remove '!ask' from the message content

                # Call OpenAI API with the question
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": question}
                    ],
                )

                # Retrieve and split the response into chunks if too long
                response_text = response['choices'][0]['message']['content']
                response_chunks = split_message(response_text)

                for chunk in response_chunks:
                    await message.channel.send(chunk)
        except Exception as e:
            # Send an error message in case of any exception
            await message.channel.send(f"An error occurred: {e}")

    # Allow other commands to process
    await bot.process_commands(message)


# Ensure compatibility with SelectorEventLoop on Windows
if __name__ == "__main__":
    if os.name == 'nt':  # If running on Windows
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    bot.run(TOKEN)
