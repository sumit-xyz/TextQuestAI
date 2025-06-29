import json
import os
import random
import winsound
import time

SAVE_FILE = "savegame.json"
WORLD_FILE = "world.json"

with open(WORLD_FILE, encoding="utf-8") as f:
    rooms = json.load(f)

riddles = [
    {"question": "What has keys but can't open locks?", "answer": "keyboard"},
    {"question": "I dont need clean place, stay in dirt. I search food for all night while I hide all day. Who am I?", "answer": "mosquito"},
    {"question": "What can travel around the world while staying in the same corner?", "answer": "stamp"},
    {"question": "What gets wetter the more it dries?", "answer": "towel"}
]
treasure_riddle = random.choice(riddles)

player = {
    "current_room": "forest_center",
    "inventory": ["stick", "health potion"],
    "health": 100,
    "coins": 10,
    "equipped_weapon": "stick",
    "equipped_shield": None
}

weapon_stats = {"stick": 25, "dagger": 10, "sword": 15}
shield_stats = {"wooden_shield": 10, "iron_shield": 20}

enemies = [
    {"name": "Bagh", "location": "cave", "patrol_path": ["cave", "river", "forest_center"], "step": 0, "damage": 20, "health": 40},
    {"name": "Sarpo", "location": "river", "patrol_path": ["river", "forest_center"], "step": 0, "damage": 10, "health": 25},
    {"name": "Chituwa", "location": "forest_center", "patrol_path": ["river", "forest_center"], "step": 0, "damage": 10, "health": 25}
]

shop_items = {
    "health potion": 10,
    "dagger": 15,
    "sword": 25,
    "wooden_shield": 20,
    "iron_shield": 40
}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def save_game():
    with open(SAVE_FILE, "w") as f:
        json.dump({"player": player, "rooms": rooms, "enemies": enemies}, f, indent=4)
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

def show_welcome_message():
    banner = """
╔════════════════════════════════════╗
║  🌲 Welcome to TextQuest AI Game! 🌲  ║
╚════════════════════════════════════╝
"""
    print(banner)

def hearts_display(hp, max_hp=100):
    total_hearts = 10
    hearts_full = int(hp / max_hp * total_hearts)
    hearts_empty = total_hearts - hearts_full
    return "❤️" * hearts_full + "🖤" * hearts_empty + f" ({hp}/{max_hp})"

def show_room():
    room = rooms[player["current_room"]]
    print(f"\n📍 Location: {player['current_room'].replace('_', ' ').title()}")
    print("-" * 30)
    print(room.get("description", ""))
    if room.get("items"):
        print("🧰 Items here:", ", ".join(room["items"]))
    print("🚪 Exits:", ", ".join(room["exits"].keys()))

def show_status():
    print(f"\nHealth: {hearts_display(player['health'])}   🪙 Coins: {player['coins']}   🗡️ Weapon: {player['equipped_weapon']}   🛡️ Shield: {player.get('equipped_shield') or 'None'}")

def show_inventory():
    print("🎒 Inventory:", ", ".join(player["inventory"]))
    print(f"🗡️ Weapon: {player['equipped_weapon']}   🛡️ Shield: {player.get('equipped_shield') or 'None'}")

def show_simple_map():
    current = player["current_room"]
    treasure_rooms = [room for room, data in rooms.items() if "treasure" in data.get("items", [])]

    room_emojis = {
        "peak": "🏔️",
        "mountain_pass": "🛤️",
        "cliffside": "⛰️",
        "forest_center": "🌲",
        "cave": "🕳️",
        "river": "🌊",
        "village": "🏘️",
        "bridge": "🌉",
        "locked_room": "🔒",
        "blacksmith": "⚒️",
        "mill": "🌾"
    }

    def room_has(item, room):
        return item in rooms[room].get("items", [])

    def enemy_here(room):
        return any(e["location"] == room for e in enemies)

    def hl(room):
        name = room.replace('_', ' ').title()
        emoji = room_emojis.get(room, "")
        display = f"{emoji} {name}"

        # Add item indicators
        indicators = ""
        if room_has("treasure", room):
            indicators += "💰"
        if any(i in rooms[room].get("items", []) for i in weapon_stats):
            indicators += "🗡️"
        if any(i in rooms[room].get("items", []) for i in shield_stats):
            indicators += "🛡️"
        if "health potion" in rooms[room].get("items", []):
            indicators += "🧪"
        if enemy_here(room):
            indicators += "⚠️"

        display += f" ({indicators})" if indicators else ""

        if room == current:
            return f"👉[{display}]👈"
        elif room in treasure_rooms:
            return f"💰[{display}]💰"
        else:
            return f"✨[{display}]✨"

    print("\n🗺️ MAP:")
    print(f"           {hl('peak')}")
    print("              |")
    print(f"       {hl('mountain_pass')}")
    print("              |")
    print(f"          {hl('cliffside')}")
    print("              |")
    print(f"        {hl('forest_center')}")
    print(f"       /       |       \\")
    print(f"   {hl('cave')}   {hl('river')}   {hl('village')}")
    print(f"                |")
    print(f"            {hl('bridge')}")
    print(f"                |")
    print(f"         {hl('locked_room')}")
    print(f"                |")
    print(f"          {hl('blacksmith')}")
    print(f"                |")
    print(f"             {hl('mill')}")

    print("\nLegend: 🗡️ Weapon  🛡️ Shield  🧪 Potion  💰 Treasure  ⚠️ Enemy")

def show_help():
    print("""
📘 Commands:
- go [direction]
- pick up [item]
- drop [item]
- equip [item]
- use [item]
- attack
- escape
- inventory
- shop
- map
- save
- load
- help
- quit
""")

def show_available_commands():
    commands = [
        "go [direction]",
        "pick up [item]",
        "drop [item]",
        "equip [item]",
        "use [item]",
        "attack",
        "escape",
        "inventory",
        "shop",
        "map",
        "save",
        "load",
        "help",
        "quit"
    ]
    print("\n📘 Available commands:")
    print(" - " + "\n - ".join(commands))

def check_enemies():
    for e in enemies:
        if e["location"] == player["current_room"]:
            print(f"⚠️ {e['name']} is here! (HP: {e['health']})")
            sound_file = os.path.join("data", f"{e['name'].lower()}.wav")
            if os.path.exists(sound_file):
                winsound.PlaySound(sound_file, winsound.SND_FILENAME)
            print(f"💢 {e['name']} attacks you for {e['damage']} damage!")
            player["health"] -= e["damage"]
            if player["health"] <= 0:
                print("💀 You died. Game Over.")
                exit()

def move_player(direction):
    current = player["current_room"]
    if direction in rooms[current]["exits"]:
        next_room = rooms[current]["exits"][direction]
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
        check_enemies()
        if "treasure" in rooms[next_room].get("items", []) and "treasure" not in player["inventory"]:
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
        rooms[player["current_room"]].setdefault("items", []).append(item)
        print(f"🗑️ Dropped {item}")
    else:
        print("❌ You don't have that.")

def equip_item(item):
    if item in player["inventory"]:
        if item in weapon_stats:
            player["equipped_weapon"] = item
            print(f"🗡️ Equipped {item}")
        elif item in shield_stats:
            player["equipped_shield"] = item
            print(f"🛡️ Equipped {item}")
        else:
            print("❌ Can't equip that.")
    else:
        print("❌ Not in inventory.")

def use_item(item):
    if item == "health potion" and item in player["inventory"]:
        player["health"] = min(100, player["health"] + 30)
        player["inventory"].remove(item)
        print("🧪 Healed 30 HP.")
    else:
        print("❌ Can't use that.")

def attack():
    current = player["current_room"]
    for enemy in enemies:
        if enemy["location"] == current:
            dmg = weapon_stats.get(player["equipped_weapon"], 5)
            enemy["health"] -= dmg
            print(f"🗡️ You hit {enemy['name']} for {dmg}!")
            if enemy["health"] <= 0:
                print(f"💀 {enemy['name']} defeated!")
                player["coins"] += random.randint(2, 6)
                enemies.remove(enemy)
            else:
                player["health"] -= enemy["damage"]
                print(f"⚔️ {enemy['name']} strikes back for {enemy['damage']}!")
                if player["health"] <= 0:
                    print("💀 You died. Game Over.")
                    exit()
            return
    print("😐 No enemy to attack.")

def escape():
    current = player["current_room"]
    for enemy in enemies:
        if enemy["location"] == current:
            print(f"😰 You try to escape from {enemy['name']}...")
            success = random.random() < 0.5
            if success:
                exits = list(rooms[current]["exits"].values())
                safe_rooms = [room for room in exits if all(e["location"] != room for e in enemies)]
                if safe_rooms:
                    new_room = random.choice(safe_rooms)
                    print(f"🏃 You successfully escaped to {new_room.replace('_', ' ').title()}!")
                    player["current_room"] = new_room
                    return
                else:
                    print("🚪 No safe room to escape to!")
            else:
                print(f"❌ Failed to escape! {enemy['name']} attacks!")
                player["health"] -= enemy["damage"]
                print(f"💢 You took {enemy['damage']} damage!")
                if player["health"] <= 0:
                    print("💀 You died. Game Over.")
                    exit()
            return
    print("🤔 No enemy here to escape from.")

def move_enemies():
    for e in enemies:
        e["step"] = (e["step"] + 1) % len(e["patrol_path"])
        e["location"] = e["patrol_path"][e["step"]]

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
        print("❌ Item not sold.")

def game_loop():
    clear_screen()
    show_welcome_message()
    while True:
        clear_screen()
        show_simple_map()
        show_room()
        check_enemies()
        show_status()
        show_available_commands()  # Shows the commands list
        command = input("\n> ").strip().lower()

        if command.startswith("go "):
            move_player(command[3:])
        elif command.startswith("pick up "):
            pick_up_item(command[8:])
        elif command.startswith("drop "):
            drop_item(command[5:])
        elif command.startswith("equip "):
            equip_item(command[6:])
        elif command.startswith("use "):
            use_item(command[4:])
        elif command == "attack":
            attack()
        elif command == "escape":
            escape()
        elif command == "inventory":
            show_inventory()
        elif command == "map":
            show_simple_map()
        elif command == "shop":
            enter_shop()
        elif command == "save":
            save_game()
        elif command == "load":
            load_game()
        elif command == "help":
            show_help()
        elif command == "quit":
            print("👋 Thanks for playing!")
            break
        else:
            print("❓ Unknown command.")

        move_enemies()
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    game_loop()
