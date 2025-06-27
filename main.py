import json
import os
import random

# --- Game Data ---
SAVE_FILE = "savegame.json"
WORLD_FILE = "world.json"

# Load game world
with open(WORLD_FILE) as f:
    rooms = json.load(f)

# Load riddles
riddles = [
    {"question": "What has keys but can't open locks?", "answer": "keyboard"},
    {"question": "What has hands but can't clap?", "answer": "clock"},
    {"question": "What can travel around the world while staying in the same corner?", "answer": "stamp"},
    {"question": "What gets wetter the more it dries?", "answer": "towel"}
]
treasure_riddle = random.choice(riddles)

# Player state
player = {
    "current_room": "forest_center",
    "inventory": ["stick", "health potion"],
    "health": 100,
    "coins": 10,
    "equipped_weapon": "stick"
}

# Weapon stats
weapon_stats = {
    "stick": 5,
    "dagger": 10,
    "sword": 15
}

# Enemies
enemies = [
    {"name": "Bagh", "location": "cave", "patrol_path": ["cave", "river", "forest_center"], "step": 0, "damage": 20, "health": 40},
    {"name": "Sarpo", "location": "river", "patrol_path": ["river", "forest_center"], "step": 0, "damage": 10, "health": 25},
    {"name": "Chituwa", "location": "forest_center", "patrol_path": ["river", "forest_center"], "step": 0, "damage": 10, "health": 25}
]

# Shop items
shop_items = {
    "health potion": 10,
    "dagger": 15,
    "sword": 25
}

# --- Utility ---
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump({"player": player, "rooms": rooms, "enemies": enemies}, f)
    print("💾 Game saved!")

def load_game():
    global player, enemies
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE) as f:
            data = json.load(f)
            player.update(data["player"])
            enemies.clear()
            enemies.extend(data["enemies"])
            for room in data["rooms"]:
                rooms[room] = data["rooms"][room]
        print("✅ Game loaded!")
    else:
        print("❌ No save file found.")

# --- Display ---
def show_room():
    room = rooms[player["current_room"]]
    print(f"\n📍 Location: {player['current_room'].replace('_', ' ').title()}")
    print("-" * 30)
    print(room.get("description", ""))
    if room.get("items"):
        print("🧰 Items here:", ", ".join(room["items"]))
    print("🚪 Exits:", ", ".join(room["exits"].keys()))

def show_status():
    print(f"\n❤️ Health: {player['health']}   🪙 Coins: {player['coins']}   🗡️ Equipped: {player['equipped_weapon'] or 'None'}")

def show_inventory():
    print("🎒 Inventory:", ", ".join(player["inventory"]) if player["inventory"] else "Empty")
    print(f"🪙 Coins: {player['coins']}")
    print(f"🗡️ Equipped: {player['equipped_weapon'] or 'None'}")

def show_larger_map():
    current = player["current_room"]
    def highlight(room):
        return f"👉 [{room.replace('_', ' ').title()}] 👈" if current == room else f"[{room.replace('_', ' ').title()}]"

    print("\n🗺️ MAP:")

    print(f"        {highlight('peak')}")
    print("           |")
    print(f"   {highlight('mountain_pass')}")
    print("           |")
    print(f"        {highlight('cliffside')}")
    print("           |")
    print(f"        {highlight('forest_center')}")
    
    # Horizontal line
    print(f"{highlight('cave')} - {highlight('forest_center')} - {highlight('river')} - {highlight('bridge')} - {highlight('locked_room')}")

    # Branches down from forest_center and river
    print("           |         |")
    print(f"     {highlight('village')}   {highlight('mill')}")
    print("           |")
    print(f"    {highlight('blacksmith')}")

def show_help():
    print("""
📘 Commands:
- go [direction]
- pick up [item]
- drop [item]
- equip [weapon]
- use [item]
- attack
- inventory
- shop
- map
- save
- load
- help
- quit
""")

# --- Actions ---
def move_player(direction):
    room = rooms[player["current_room"]]
    if direction in room["exits"]:
        next_room = room["exits"][direction]
        if next_room == "locked_room" and rooms["locked_room"].get("locked", True):
            print(f"\n🧐 Riddle: {treasure_riddle['question']}")
            answer = input("Your answer: ").strip().lower()
            if answer == treasure_riddle["answer"]:
                print("✅ Correct! The gate opens.")
                rooms["locked_room"]["locked"] = False
            else:
                print("❌ Wrong! The gate remains locked.")
                return
        player["current_room"] = next_room
        if "treasure" in rooms[next_room].get("items", []):
            if "treasure" not in player["inventory"]:
                print("🎉 You found the treasure! You win!")
                player["inventory"].append("treasure")
                rooms[next_room]["items"].remove("treasure")
    else:
        print("❌ You can't go that way.")

def pick_up_item(item):
    room = rooms[player["current_room"]]
    if item in room.get("items", []):
        player["inventory"].append(item)
        room["items"].remove(item)
        print(f"✅ Picked up {item}")
    else:
        print("❌ Item not found.")

def drop_item(item):
    if item in player["inventory"]:
        player["inventory"].remove(item)
        if player["equipped_weapon"] == item:
            player["equipped_weapon"] = None
        rooms[player["current_room"]].setdefault("items", []).append(item)
        print(f"🗑️ Dropped {item}")
    else:
        print("❌ You don't have that.")

def equip_weapon(weapon):
    if weapon in player["inventory"] and weapon in weapon_stats:
        player["equipped_weapon"] = weapon
        print(f"🗡️ Equipped {weapon}")
    else:
        print("❌ Can't equip that.")

def use_item(item):
    if item in player["inventory"]:
        if item == "health potion":
            player["health"] = min(100, player["health"] + 30)
            player["inventory"].remove(item)
            print("🧪 Healed 30 HP.")
        else:
            print("❌ Can't use that.")
    else:
        print("❌ Not in inventory.")

def attack():
    current = player["current_room"]
    weapon = player["equipped_weapon"]
    if not weapon:
        print("❌ No weapon equipped.")
        return
    for enemy in enemies:
        if enemy["location"] == current:
            damage = weapon_stats[weapon]
            enemy["health"] -= damage
            print(f"🗡️ You hit {enemy['name']} for {damage}!")
            if enemy["health"] <= 0:
                loot = random.choice(["health potion", None])
                coins = random.randint(3, 7)
                player["coins"] += coins
                print(f"💀 {enemy['name']} defeated. Looted {coins} coins.")
                if loot:
                    player["inventory"].append(loot)
                    print(f"🎁 Found: {loot}")
                enemies.remove(enemy)
            else:
                player["health"] -= enemy["damage"]
                print(f"⚔️ {enemy['name']} hit back! -{enemy['damage']} HP")
                if player["health"] <= 0:
                    print("💀 You died. Game Over.")
                    exit()
            return
    print("😐 No enemy here.")

def move_enemies():
    for e in enemies:
        e["step"] = (e["step"] + 1) % len(e["patrol_path"])
        e["location"] = e["patrol_path"][e["step"]]

def check_enemies():
    for e in enemies:
        if e["location"] == player["current_room"]:
            print(f"⚠️ {e['name']} is here!")

def enter_shop():
    print("\n🛒 Shop:")
    for item, cost in shop_items.items():
        print(f"- {item}: {cost} coins")
    choice = input("Buy what? ").strip().lower()
    if choice in shop_items:
        if player["coins"] >= shop_items[choice]:
            player["coins"] -= shop_items[choice]
            player["inventory"].append(choice)
            print(f"✅ Bought {choice}")
        else:
            print("❌ Not enough coins.")
    else:
        print("❌ Not available.")

# --- Game Loop ---
def game_loop():
    clear_screen()
    print("🌲 Welcome to TextQuest AI 🌲")
    while True:
        show_status()
        show_room()
        check_enemies()
        command = input("\n> ").strip().lower()

        if command.startswith("go "): move_player(command[3:])
        elif command.startswith("pick up "): pick_up_item(command[8:])
        elif command.startswith("drop "): drop_item(command[5:])
        elif command.startswith("equip "): equip_weapon(command[6:])
        elif command.startswith("use "): use_item(command[4:])
        elif command == "attack": attack()
        elif command == "inventory": show_inventory()
        elif command == "shop": enter_shop()
        elif command == "map": show_larger_map()
        elif command == "save": save_game()
        elif command == "load": load_game()
        elif command == "help": show_help()
        elif command == "quit":
            print("👋 Thanks for playing!")
            break
        else:
            print("❓ Unknown command. Type 'help'.")

        move_enemies()
        input("\nPress Enter to continue...")
        clear_screen()

if __name__ == "__main__":
    game_loop()
