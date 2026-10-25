"""anniRPG: a text-based fantasy RPG that runs in the terminal.

Create a hero, fight random monsters, earn gold, buy potions and weapons
in the store, and save your progress to a file.

Run it with:  python anniRPG.py
"""

import os
import pickle
import random
import sys

SAVE_FILE = "anniRPG_save.pkl"
DEFAULT_NAME = "Ezra"
POTION_PRICE = 20
POTION_HEAL = 50
MISS_CHANCE = 0.1  # chance that any single attack misses
FLEE_CHANCE = 1 / 3  # chance that running away works

# Weapons sold in the store, with their price in gold.
WEAPON_PRICES = {
    "White Tank Top": 40,
    "Bamboo Stick": 80,
    "Belt": 100,
    "Golden Chappal": 300,
}

# Extra attack each weapon adds to the player's base attack.
WEAPON_BONUSES = {
    "Chappal": 5,
    "White Tank Top": 10,
    "Bamboo Stick": 20,
    "Belt": 25,
    "Golden Chappal": 40,
}

# Each enemy type as (name, max health, attack, gold reward).
ENEMY_TYPES = [
    ("Sneaky Goblin", 50, 5, 10),
    ("Rotting Zombie", 70, 7, 15),
    ("Wobbly Slime", 30, 2, 5),
    ("Floating Beholder", 85, 9, 20),
    ("Angry Orc", 90, 10, 30),
]


class Player:
    """The hero controlled by the person playing."""

    def __init__(self, name):
        self.name = name
        self.max_health = 100
        self.health = self.max_health
        self.base_attack = 10
        self.gold = 0
        self.potions = 0
        self.weapons = ["Chappal"]
        self.equipped_weapon = "Chappal"

    @property
    def attack(self):
        """Base attack plus the bonus from the equipped weapon."""
        return self.base_attack + WEAPON_BONUSES[self.equipped_weapon]


class Enemy:
    """A monster to fight. A fresh one is created for every fight."""

    def __init__(self, name, max_health, attack, gold_reward):
        self.name = name
        self.max_health = max_health
        self.health = max_health
        self.attack = attack
        self.gold_reward = gold_reward


player = None  # the current Player, set by create_character() or load_game()
enemy = None  # the Enemy in the current fight, set by start_fight()


def clear_screen():
    """Clear the terminal on Windows, macOS and Linux."""
    os.system("cls" if os.name == "nt" else "clear")


def find_item(typed_name, item_names):
    """Return the item whose name matches typed_name, ignoring case, or None."""
    for item_name in item_names:
        if item_name.lower() == typed_name.strip().lower():
            return item_name
    return None


def roll_damage(attack):
    """Return one attack's damage: 0 on a miss, else half to full attack."""
    if random.random() < MISS_CHANCE:
        return 0
    return random.randint(attack // 2, attack)


# Each screen function below returns the next screen to show, as a function
# name without (). run_game() at the bottom keeps showing screens in a loop,
# so menus never pile up on the call stack.


def main_menu():
    """Title screen: start a new game, load a saved one, or quit."""
    clear_screen()
    print("anniRPG")
    print("\nWelcome, adventurer!")
    print("1) Start")
    print("2) Load")
    print("3) Exit")
    choice = input("-> ")
    if choice == "1":
        return create_character
    elif choice == "2":
        return load_game
    elif choice == "3":
        sys.exit()
    else:
        return main_menu


def create_character():
    """Ask for the hero's name and create the player."""
    global player
    clear_screen()
    print("What is your hero's name?")
    name = input(f"(press Enter to use {DEFAULT_NAME}) >>> ").strip()
    player = Player(name or DEFAULT_NAME)
    clear_screen()
    print("Your name is", player.name)
    input("")
    return hub_menu


def load_game():
    """Load the player from the save file, if there is one."""
    global player
    clear_screen()
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "rb") as save_file:
            player = pickle.load(save_file)
        print("Loaded save state.")
        input("")
        return hub_menu
    else:
        print("Save file not found.")
        input("")
        return main_menu


def save_game():
    """Write the player to the save file."""
    clear_screen()
    with open(SAVE_FILE, "wb") as save_file:
        pickle.dump(player, save_file)
    print("Game saved.")
    input("")
    return hub_menu


def hub_menu():
    """Show the player's stats and the main actions."""
    clear_screen()
    print("Name:", player.name)
    print("Attack Strength:", player.attack)
    print(f"Health: {player.health}/{player.max_health}")
    print("Current Weapon:", player.equipped_weapon)
    print("Gold:", player.gold)
    print("Potions:", player.potions)
    print("1) Fight\n2) Inventory\n3) Store\n4) Save\n5) Exit")
    choice = input(">>> ")
    if choice == "1":
        return start_fight
    elif choice == "2":
        return inventory_menu
    elif choice == "3":
        return store_menu
    elif choice == "4":
        return save_game
    elif choice == "5":
        sys.exit()
    else:
        return hub_menu


def inventory_menu():
    """List what the player owns."""
    clear_screen()
    print("Your inventory:\n")
    print(f"{player.potions} Potion(s)")
    for weapon in player.weapons:
        print(weapon)
    print("\nWhat do you want to do?")
    print("1) Equip Weapon")
    print("2) Go back")
    choice = input(">>> ")
    if choice == "1":
        return equip_menu
    elif choice == "2":
        return hub_menu
    else:
        return inventory_menu


def equip_menu():
    """Let the player choose which weapon to hold."""
    clear_screen()
    print("What weapon do you want to equip?")
    print("You own:", ", ".join(player.weapons))
    print("Type b to go back")
    choice = input(">>> ")
    weapon = find_item(choice, player.weapons)
    if choice.strip().lower() == "b":
        return inventory_menu
    elif weapon is None:
        clear_screen()
        print("That isn't in your inventory. Check the spelling and try again.")
        input("")
        return equip_menu
    elif weapon == player.equipped_weapon:
        clear_screen()
        print(weapon, "is already in your hands!")
        input("")
        return equip_menu
    else:
        clear_screen()
        player.equipped_weapon = weapon
        print("You have equipped", weapon)
        input("")
        return inventory_menu


def start_fight():
    """Pick a random enemy type and create a fresh enemy to fight."""
    global enemy
    enemy = Enemy(*random.choice(ENEMY_TYPES))
    return fight_menu


def fight_menu():
    """Show both fighters' health and the battle options."""
    clear_screen()
    print(f"{player.name}            VERSUS            {enemy.name}")
    print(f"{player.name}'s Health: {player.health}/{player.max_health}          "
          f"{enemy.name}'s Health: {enemy.health}/{enemy.max_health}")
    print("Potions:", player.potions)
    print("1) Attack\n2) Drink Potion\n3) Run")
    choice = input(">>> ")
    if choice == "1":
        return attack_turn
    elif choice == "2":
        return drink_potion
    elif choice == "3":
        return run_away
    else:
        return fight_menu


def attack_turn():
    """The player attacks. If the enemy survives, it hits back."""
    clear_screen()
    damage = roll_damage(player.attack)
    if damage == 0:
        print("You missed!")
    else:
        enemy.health -= damage
        print(f"You dealt {damage} damage")
    input("")
    if enemy.health <= 0:
        return win_battle
    else:
        return enemy_turn


def enemy_turn():
    """The enemy attacks the player."""
    clear_screen()
    damage = roll_damage(enemy.attack)
    if damage == 0:
        print(f"{enemy.name} missed! You dodged the attack.")
    else:
        player.health -= damage
        print(f"{enemy.name} dealt {damage} emotional damage :(")
    input("")
    if player.health <= 0:
        return lose_battle
    else:
        return fight_menu


def drink_potion():
    """Drink one potion to heal, without going over max health."""
    clear_screen()
    if player.potions == 0:
        print("You don't have any potions left!")
    else:
        player.potions -= 1
        player.health = min(player.health + POTION_HEAL, player.max_health)
        print(f"You drank a potion. Health: {player.health}/{player.max_health}")
    input("")
    return fight_menu


def run_away():
    """Try to escape. If it fails, the enemy gets a free hit."""
    clear_screen()
    if random.random() < FLEE_CHANCE:
        print("You got away safely.")
        input("")
        return hub_menu
    else:
        print("You failed to run away!")
        input("")
        return enemy_turn


def win_battle():
    """Give the player the defeated enemy's gold."""
    clear_screen()
    player.gold += enemy.gold_reward
    print(f"YOU DID IT! YOU WON! You literally annihilated the {enemy.name}!")
    print(f"You earned {enemy.gold_reward} gold.")
    input("")
    return hub_menu


def lose_battle():
    """The player was defeated: restore their health and return to the hub."""
    clear_screen()
    player.health = player.max_health
    print("You were defeated... You wake up back at camp with full health.")
    input("")
    return hub_menu


def store_menu():
    """Sell potions and weapons for gold."""
    clear_screen()
    print("Welcome to Niraad's Garage, I'm his assistant, D. "
          "What would you like to buy?")
    print(f"You have {player.gold} gold.\n")
    print("Items:")
    print(f"- Potion : {POTION_PRICE} Gold each\n")
    print("Weapons:")
    for weapon, price in WEAPON_PRICES.items():
        print(f"- {weapon} : {price} Gold")
    print("\nType an item's name to buy it, or b to go back\n")
    choice = input(">>> ")
    item = find_item(choice, ["Potion"] + list(WEAPON_PRICES))
    if choice.strip().lower() == "b":
        return hub_menu
    elif item == "Potion":
        buy_potions()
    elif item is not None:
        buy_weapon(item)
    else:
        clear_screen()
        print("Bro, choose from the options above, "
              "or is your imaginary cat smashing your keyboard again?")
        input("")
    return store_menu


def buy_potions():
    """Ask how many potions to buy and charge for them."""
    clear_screen()
    print("How many potions?")
    try:
        amount = int(input(">>> "))
    except ValueError:
        amount = 0
    cost = amount * POTION_PRICE
    clear_screen()
    if amount <= 0:
        print("Please type a whole number above 0.")
    elif player.gold < cost:
        print(f"Gold where?! {amount} potion(s) cost {cost} gold.")
    else:
        player.gold -= cost
        player.potions += amount
        print(f"You bought {amount} potion(s)!")
    input("")


def buy_weapon(weapon):
    """Buy a weapon if the player can afford it and doesn't own it yet."""
    clear_screen()
    price = WEAPON_PRICES[weapon]
    if weapon in player.weapons:
        print(f"You already own the {weapon}!")
    elif player.gold < price:
        print(f"Gold where?! The {weapon} costs {price} gold.")
    else:
        player.gold -= price
        player.weapons.append(weapon)
        print(f"Ah, a very marvellous choice! {weapon} is yours!")
    input("")


def run_game():
    """Show screens one after another until the player picks Exit."""
    screen = main_menu
    while True:
        screen = screen()


if __name__ == "__main__":
    run_game()
