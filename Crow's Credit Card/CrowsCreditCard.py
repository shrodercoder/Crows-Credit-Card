import discord
from discord.ext import commands
import os 
import json
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DTOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Enable privileged intent
intents.members = True  # Enable members intent for member-related features

bot = commands.Bot(command_prefix="$", intents=intents)

# Load data from file if it exists
DATA_FILE = "DATA_FILE.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        data = json.load(f)
        inventory = data.get("inventory", {})
        currency = data.get("currency", {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0})
else:
    inventory = {}
    currency = {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}

# Function to save data
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump({"inventory": inventory, "currency": currency}, f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="h")
async def custom_help(ctx):
    help_text = (
        "$h - This will give you this list of commands.\n"
        "$add # [item] - Add items to the Guild's bag.\n"
        "$remove # [item] - Remove items from the Guild's bag.\n"
        "$list [page] - Display 25 unique items per page.\n"
        "$currency - Display current Guild currency amounts.\n"
        "$ca/sa/ea/ga/pa # - Add currency (Copper, Silver, Electrum, Gold, Platinum).\n"
        "$cr/sr/er/gr/pr # - Remove currency.\n"
        "$wishlist - Display the current wish list.\n"
        "$addwish [item] - Add an item to the wish list.\n"
        "$removewish [item] - Remove an item from the wish list.\n"
    )
    await ctx.send(f'```{help_text}```')

@bot.command()
async def add(ctx, count: int, *, item: str):
    inventory[item] = inventory.get(item, 0) + count
    save_data()
    await ctx.send(f"Added {count}x {item} to the Guild's bag.")

@bot.command()
async def remove(ctx, count: int, *, item: str):
    if item in inventory and inventory[item] >= count:
        inventory[item] -= count
        if inventory[item] == 0:
            del inventory[item]
        await ctx.send(f"Removed {count}x {item} from the Guild's bag.")
    else:
        await ctx.send(f'Not enough {item} in the bag.')

@bot.command(name="list")
async def list_items(ctx, page: int = 1):
    print("Starting list command execution")
    print(f"Inventory type: {type(inventory)}")
    
    # Ensure we're working with a regular dictionary items view, not a coroutine
    try:
        items_view = inventory.items()
        print(f"Items view type: {type(items_view)}")
        # Convert to a list directly without storing in a variable that might be shadowing something
        inventory_items = [(item, qty) for item, qty in items_view]
        items_count = len(inventory_items)
        print(f"List command called. Items count: {items_count}")
    except Exception as e:
        print(f"Error processing inventory: {e}")
        import traceback
        traceback.print_exc()
        await ctx.send("An error occurred while processing the inventory.")
        return
    
    if not inventory_items:
        # Send a clearer empty inventory message
        try:
            await ctx.send("```=== Guild Bag - Empty ===\nThe bag contains no items.```")
            print("Empty message sent")
        except Exception as e:
            print(f"Error sending empty message: {e}")
        return
    
    items_per_page = 25
    total_pages = (len(inventory_items) + items_per_page - 1) // items_per_page
    
    if page < 1 or (page > total_pages and total_pages > 0):
        await ctx.send(f"Invalid page number. Please use a page between 1 and {total_pages}.")
        return
    
    start = (page - 1) * items_per_page
    end = min(start + items_per_page, len(inventory_items))
    
    display = "\n".join(f'{item}: {qty}' for item, qty in inventory_items[start:end])
    page_info = f"Page {page}/{total_pages}" if total_pages > 0 else "Page 1/1"
    
    try:
        await ctx.send(f'```Guild Bag - {page_info}\n{display}```')
    except Exception as e:
        print(f"Error sending list message: {e}")
@bot.command(name="wishlist")
async def show_wishlist(ctx):
    wishlist = inventory.get("wishlist", [])
    if not wishlist:
        await ctx.send("The wish list is empty.")
    else:
        wishlist_display = "\n".join(wishlist)
        await ctx.send(f"```Wish List\n{wishlist_display}```")
@bot.command(name="addwish")
async def add_to_wishlist(ctx, *, item: str):
    wishlist = inventory.setdefault("wishlist", [])
    if item not in wishlist:
        wishlist.append(item)
        save_data()
        await ctx.send(f"Added '{item}' to the wish list.")
    else:
        await ctx.send(f"'{item}' is already in the wish list.")
@bot.command(name="removewish")
async def remove_from_wishlist(ctx, *, item: str):
    wishlist = inventory.get("wishlist", [])
    if item in wishlist:
        wishlist.remove(item)
        save_data()
        await ctx.send(f"Removed '{item}' from the wish list.")
    else:
        await ctx.send(f"'{item}' is not in the wish list.")
@bot.command(name="currency")
async def show_currency(ctx):
    currency_display = (
        f"Copper: {currency['cp']}\n"
        f"Silver: {currency['sp']}\n"
        f"Electrum: {currency['ep']}\n"
        f"Gold: {currency['gp']}\n"
        f"Platinum: {currency['pp']}"
    )
    await ctx.send(f"```Guild Currency\n{currency_display}```")

@bot.command()
async def ca(ctx, amount: int):
    currency["cp"] += amount
    save_data()
    await ctx.send(f"Added {amount} Copper to the Guild's bag.")

@bot.command()
async def sa(ctx, amount: int):
    currency["sp"] += amount
    save_data()
    await ctx.send(f"Added {amount} Silver to the Guild's bag.")

@bot.command()
async def ea(ctx, amount: int):
    currency["ep"] += amount
    save_data()
    await ctx.send(f"Added {amount} Electrum to the Guild's bag.")

@bot.command()
async def ga(ctx, amount: int):
    currency["gp"] += amount
    save_data()
    await ctx.send(f"Added {amount} Gold to the Guild's bag.")

@bot.command()
async def pa(ctx, amount: int):
    currency["pp"] += amount
    save_data()
    await ctx.send(f"Added {amount} Platinum to the Guild's bag.")

@bot.command()
async def cr(ctx, amount: int):
    currency["cp"] = max(0, currency["cp"] - amount)
    save_data()
    await ctx.send(f"Removed {amount} Copper from the Guild's bag.")

@bot.command()
async def sr(ctx, amount: int):
    currency["sp"] = max(0, currency["sp"] - amount)
    save_data()
    await ctx.send(f"Removed {amount} Silver from the Guild's bag.")

@bot.command()
async def er(ctx, amount: int):
    currency["ep"] = max(0, currency["ep"] - amount)
    save_data()
    await ctx.send(f"Removed {amount} Electrum from the Guild's bag.")

@bot.command()
async def gr(ctx, amount: int):
    currency["gp"] = max(0, currency["gp"] - amount)
    save_data()
    await ctx.send(f"Removed {amount} Gold from the Guild's bag.")

@bot.command()
async def pr(ctx, amount: int):
    currency["pp"] = max(0, currency["pp"] - amount)
    save_data()
    await ctx.send(f"Removed {amount} Platinum from the Guild's bag.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.BadArgument):
        await ctx.send("Invalid arguments. Please check your command format.")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Command not found. Use $h to see available commands.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Missing required arguments. Use $h to see command formats.")
    else:
        print(f"An error occurred: {error}")
        # Print more details about the error
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)

bot.run(TOKEN)
