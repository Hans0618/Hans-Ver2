import discord
from discord.ext import commands
import json
import os
import ssl
from tabulate import tabulate
import pandas as pd
import matplotlib.pyplot as plt
import io
import matplotlib
import json
ssl._create_default_https_context = ssl._create_unverified_context

# Set up bot with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store user scores
# Structure: {user_id: [{song_name: str, constant: float, score: float}, ...]}
user_scores = {}

# Load existing data if available
def load_scores():
    if os.path.exists('scores.json'):
        with open('scores.json', 'r') as f:
            return json.load(f)
    return {}

# Save scores to file
def save_scores():
    with open('scores.json', 'w') as f:
        json.dump(user_scores, f)

@bot.event
async def on_ready():
    global user_scores
    print(f'{bot.user} has connected to Discord!')
    user_scores = load_scores()

def calculate_rating(constant, score):
    """Calculate song rating based on score and constant"""
    if not (1000000 <= score <= 1010000):
        return None, None  # Invalid score range
    
    # SSS+ rank (1009000+)
    if score >= 1009000:
        return "SSS+", constant + 2.15
    
    # SSS rank (1007500-1008999)
    elif score >= 1007500:
        extra = ((score - 1007500) // 100) * 0.01
        return "SSS", constant + 2.0 + extra
    
    # SS+ rank (1005000-1007499)
    elif score >= 1005000:
        extra = ((score - 1005000) // 50) * 0.01
        return "SS+", constant + 1.5 + extra
    
    # SS rank (1000000-1004999)
    elif score >= 1000000:
        extra = ((score - 1000000) // 100) * 0.01
        return "SS", constant + 1.0 + extra

@bot.command(name='addsong')
async def add_song(ctx):
    """Command to add a new song score"""
    user_id = str(ctx.author.id)
    
    # Initialize user's score list if it doesn't exist
    if user_id not in user_scores:
        user_scores[user_id] = []

    # Ask for song details
    await ctx.send("Please enter the song name:")
    
    try:
        # Wait for user response
        song_name_msg = await bot.wait_for('message', 
                                           timeout=30.0, 
                                           check=lambda m: m.author == ctx.author)
        
        song_name = song_name_msg.content
        
        # Check for duplicate song name
        if any(song['song_name'].lower() == song_name.lower() for song in user_scores[user_id]):
            await ctx.send("This song has already been added!")
            return
        
        await ctx.send("Please enter the song's rating constant:")
        constant_msg = await bot.wait_for('message', 
                                          timeout=30.0, 
                                          check=lambda m: m.author == ctx.author)
        
        await ctx.send("Please enter your score (between 1000000 and 1010000):")
        score_msg = await bot.wait_for('message', 
                                       timeout=30.0, 
                                       check=lambda m: m.author == ctx.author)
        
        # Convert inputs to appropriate types
        try:
            constant = float(constant_msg.content)
            score = float(score_msg.content)
            
            # Validate score range
            if not (1000000 <= score <= 1010000):
                await ctx.send("Score must be between 1000000 and 1010000!")
                return
            
            # Calculate rank and rating
            rank, rating = calculate_rating(constant, score)
            
            # Add the song to user's records
            song_data = {
                "song_name": song_name,
                "constant": constant,
                "score": score,
                "rank": rank,
                "rating": rating
            }
            
            user_scores[user_id].append(song_data)
            save_scores()
            
            # Send detailed response
            await ctx.send(f"Song score recorded successfully!\n"
                           f"Rank: {rank}\n"
                           f"Rating: {rating:.2f}")
            
        except ValueError:
            await ctx.send("Please enter valid numbers for constant and score!")
            
    except TimeoutError:
        await ctx.send("Time's up! Please try again.")


@bot.command(name='rmsong')
async def remove_song(ctx):
    """Command to remove a song from user's records"""
    user_id = str(ctx.author.id)
    
    # Check if user has any songs recorded
    if user_id not in user_scores or not user_scores[user_id]:
        await ctx.send("You don't have any songs recorded!")
        return
    
    await ctx.send("Please enter the song name you want to remove:")
    
    try:
        # Wait for user response
        song_name_msg = await bot.wait_for('message', 
                                         timeout=30.0, 
                                         check=lambda m: m.author == ctx.author)
        
        song_name = song_name_msg.content
        
        # Find and remove the song
        for song in user_scores[user_id][:]:  # Create a copy of the list to iterate
            if song["song_name"].lower() == song_name.lower():
                user_scores[user_id].remove(song)
                save_scores()
                await ctx.send(f"Successfully removed '{song_name}' from your records!")
                return
        
        await ctx.send(f"Couldn't find song '{song_name}' in your records!")
        
    except TimeoutError:
        await ctx.send("Time's up! Please try again.")

@bot.command(name='b30')
async def show_best_30(ctx):
    """Display user's best 30 songs by rating"""
    user_id = str(ctx.author.id)
    
    # Check if user has any songs recorded
    if user_id not in user_scores or not user_scores[user_id]:
        await ctx.send("You don't have any songs recorded!")
        return
    
    # Sort songs by rating in descending order
    sorted_songs = sorted(user_scores[user_id], key=lambda x: x['rating'], reverse=True)
    
    # Take top 30 (or all if less than 30)
    top_30 = sorted_songs[:30]
    
    # Calculate average of displayed songs
    avg_rating = sum(song['rating'] for song in top_30) / len(top_30)
    
    # Prepare data for the table
    table_data = []
    for i, song in enumerate(top_30, 1):
        song_name = song['song_name'][:20]  # Truncate to 20 characters
        table_data.append([
            i,
            song_name,
            f"{song['constant']:.1f}",
            int(song['score']),
            song['rank'],
            f"{song['rating']:.2f}"
        ])
    
    # Create DataFrame
    df = pd.DataFrame(table_data, columns=["Rank", "Song Name", "Constant", "Score", "Rank", "Rating"])
    
    # Set font properties globally
    matplotlib.rcParams['font.family'] = 'Arial Unicode MS'
    matplotlib.rcParams['font.size'] = 12
    
    # Plot the table
    fig, ax = plt.subplots(figsize=(14, len(df) * 0.4))  # Adjusted size
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    
    # Add average rating text
    plt.figtext(0.5, 0.02, f"Best 30 Average Rating: {avg_rating:.2f}", ha="center", fontsize=12)
    
    # Save the table as an image
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0.1)  # Adjusted to fit content
    buf.seek(0)
    
    # Send the image
    await ctx.send(file=discord.File(buf, 'b30_table.png'))



# Run the bot
with open('config.json') as config_file:
       config = json.load(config_file)

bot_token = config['DISCORD_BOT_TOKEN']
bot.run(bot_token)
