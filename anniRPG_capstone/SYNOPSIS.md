# anniRPG: project synopsis

## Title

anniRPG, a text-based role-playing game written in Python.

## Objective

To build a complete, menu-driven console game that uses classes and objects, lists and dictionaries, random numbers, input validation and binary file handling.

## Overview

anniRPG is a single-player fantasy game played in the terminal. The player names a hero, fights randomly chosen monsters, earns gold, spends it on potions and weapons in a shop, and saves their progress to a file to continue later. Everything is controlled through numbered menus and typed item names.

## How to run

    python anniRPG.py

The game needs Python 3.6 or newer and no extra libraries. It was tested with Python 3.14 on Windows 11. Progress is saved to `anniRPG_save.pkl` in the folder the game is started from.

## Gameplay

1. Start a new game and type a name, or press Enter to play as Ezra.
2. The hub screen shows the hero's stats and offers Fight, Inventory, Store, Save and Exit.
3. Each fight is against a random enemy type, and a new enemy is created every time. On each turn the player can attack, drink a potion or try to run.
4. Attacks deal between half and full attack power, and every attack, the player's or the enemy's, has a 10% chance to miss. Running away works one time in three. If it fails, the enemy gets a free hit.
5. Winning a fight gives gold. Losing restores the player's health and returns them to the hub, so there is no permanent death.
6. The shop, Niraad's Garage, sells potions (20 gold each, heal 50 health) and four weapons that raise attack.

Enemies:

| Enemy | Health | Attack | Gold reward |
|---|---|---|---|
| Wobbly Slime | 30 | 2 | 5 |
| Sneaky Goblin | 50 | 5 | 10 |
| Rotting Zombie | 70 | 7 | 15 |
| Floating Beholder | 85 | 9 | 20 |
| Angry Orc | 90 | 10 | 30 |

Weapons (the hero's base attack is 10):

| Weapon | Price in gold | Attack bonus |
|---|---|---|
| Chappal (starting weapon) | free | +5 |
| White Tank Top | 40 | +10 |
| Bamboo Stick | 80 | +20 |
| Belt | 100 | +25 |
| Golden Chappal | 300 | +40 |

## Program structure

### Constants

Game settings are named constants at the top of the file (`SAVE_FILE`, `DEFAULT_NAME`, `POTION_PRICE`, `POTION_HEAL`, `MISS_CHANCE`, `FLEE_CHANCE`), so changing the game's balance takes one edit. Weapon prices and attack bonuses are kept in two dictionaries, and the enemy types are a list of tuples.

### Classes

- `Player` stores the hero's name, health, base attack, gold, potions, owned weapons and equipped weapon. Its `attack` property adds the equipped weapon's bonus to the base attack, so the value is always current.
- `Enemy` stores a monster's name, health, attack and gold reward.

### Functions

| Function | Purpose |
|---|---|
| `clear_screen()` | Clears the terminal on Windows, macOS and Linux |
| `find_item()` | Matches a typed item name, ignoring upper and lower case |
| `roll_damage()` | Works out one attack's damage, including the miss chance |
| `main_menu()` | Title screen: start, load or exit |
| `create_character()` | Asks for the hero's name and creates the `Player` |
| `load_game()`, `save_game()` | Read and write the save file with `pickle` |
| `hub_menu()` | Shows the hero's stats and the main actions |
| `inventory_menu()`, `equip_menu()` | List owned items and change the equipped weapon |
| `start_fight()` | Creates a random `Enemy` |
| `fight_menu()` | Shows both fighters' health and the battle options |
| `attack_turn()`, `enemy_turn()` | The player's attack and the enemy's reply |
| `drink_potion()`, `run_away()` | The other two battle options |
| `win_battle()`, `lose_battle()` | Give gold for a win, or restore health after a defeat |
| `store_menu()`, `buy_potions()`, `buy_weapon()` | The shop and its purchase checks |
| `run_game()` | The main game loop |

### How the screens connect

Each screen function returns the next screen to show, written as the function's name without brackets (for example `return hub_menu`). `run_game()` keeps calling whichever screen was returned last. Because no screen calls the next one directly, the menus never pile up on Python's call stack, and a game can go on for as long as the player wants.

```
main_menu -> create_character or load_game -> hub_menu
hub_menu  -> start_fight -> fight_menu -> attack_turn -> enemy_turn -> fight_menu ...
             ... -> win_battle or lose_battle -> hub_menu
hub_menu  -> inventory_menu -> equip_menu
hub_menu  -> store_menu (buy_potions, buy_weapon) -> store_menu
hub_menu  -> save_game -> hub_menu
```

## Python concepts used

- Classes, objects, `__init__` and the `@property` decorator
- Lists, dictionaries and tuples, including unpacking a tuple into arguments with `*`
- Functions used as values: one function returns another, and the game loop calls it later
- Global variables for the shared game state (`player` and `enemy`)
- The `random` module: `random()`, `randint()` and `choice()`
- Exception handling with `try` and `except ValueError`
- Binary file handling with `pickle`, `with open(...)` and `os.path.exists()`
- String methods (`strip()`, `lower()`, `join()`) and f-strings
- The `os` and `sys` modules, and an `if __name__ == "__main__":` entry point

## Input validation

- Menus ask again when the input isn't one of the listed options.
- Item names work in any letter case, so `belt` and `BELT` both find the Belt.
- Potion amounts must be whole numbers above 0. Text, zero and negative numbers get a message instead of crashing the game.
- The store refuses purchases the player can't afford and weapons the player already owns.
- Choosing Load when there is no save file returns to the main menu.

## Sample test cases

| Input | Expected result |
|---|---|
| Press Enter at the name prompt | The hero is named Ezra and Attack Strength shows 15 |
| Store: `potion`, then `abc` | "Please type a whole number above 0." and the store opens again |
| Store: `potion`, then `-5` | The same message; gold and potions don't change |
| Store, with at least 100 gold: `belt`, then `belt` again | "You already own the Belt!" |
| After buying the Belt, Inventory, then Equip: `belt` | The Belt is equipped and Attack Strength shows 35 |
| Lose a fight | Health is back to 100/100 on the hub screen |
| Save, exit, start the game again, then Load | The hero comes back with the same name, gold and potions |

## Limitations and future scope

- Saves use `pickle`, which can run code hidden in a tampered file, so only load save files the game created. Saving as JSON would remove that risk.
- There is one save slot, and the save file is written to the folder the game is run from.
- Enemies don't get stronger as the player does, and there are no levels or experience points.
- Possible additions: experience and levels, more enemies and items, several save slots, and a graphical version using pygame.
