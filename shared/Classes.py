"""
Classes.py — The 7 playable classes and their special abilities.

Each class dict exposes:
  id            int   — unique index 0-6
  name          str
  description   str   — shown on class-select screen
  ability_name  str
  ability_desc  str
  mana_cost     int   — mana consumed per ability use
  ability_cd    float — cooldown in seconds after use

Server-side ability *effects* are resolved in GameState.apply_ability().
"""

CLASSES = [
    {
        "id": 0,
        "name": "Stella",
        "description": "Crown Princess Stella is the Fairy of the Sun and Moon",
        "ability_name": "Eclipse Storm",
        "ability_desc": "Fire 8 bullets in all directions instantly.",
        "mana_cost": 30,
        "ability_cd": 4.0,
        "ability_effect": "radial_burst",
        "ability_params": {"count": 8, "speed": 520, "damage_mult": 0.8},
    },
    {
        "id": 1,
        "name": "Musa",
        "description": "Musa is the Fairy of Music.",
        "ability_name": "Music Shield",
        "ability_desc": "Become invulnerable for 2 seconds.",
        "mana_cost": 40,
        "ability_cd": 8.0,
        "ability_effect": "invulnerable",
        "ability_params": {"duration": 2.0},
    },
    {
        "id": 2,
        "name": "Bloom",
        "description": "Princess Bloom is the Fairy of the Dragon Flame.",
        "ability_name": "Nova Blast",
        "ability_desc": "Explode all bullets near you and deal area damage.",
        "mana_cost": 45,
        "ability_cd": 6.0,
        "ability_effect": "nova",
        "ability_params": {"radius": 200, "damage": 40},
    },
    {
        "id": 3,
        "name": "Tecna",
        "description": "Tecna is the Fairy of Technology.",
        "ability_name": "Digital Step",
        "ability_desc": "Teleport to your cursor position.",
        "mana_cost": 35,
        "ability_cd": 5.0,
        "ability_effect": "teleport",
        "ability_params": {"max_range": 350},
    },
    {
        "id": 4,
        "name": "Flora",
        "description": "Flora is the Fairy of Nature.",
        "ability_name": "Healing Pulse",
        "ability_desc": "Restore 30 HP to yourself and nearby allies.",
        "mana_cost": 40,
        "ability_cd": 7.0,
        "ability_effect": "heal_aura",
        "ability_params": {"radius": 250, "heal": 30},
    },
    {
        "id": 5,
        "name": "Aisha",
        "description": "Crown Princess Aisha is the Fairy of Waves.",
        "ability_name": "Wave Blast",
        "ability_desc": "Slow all enemies by 60% for 3 seconds.",
        "mana_cost": 35,
        "ability_cd": 7.0,
        "ability_effect": "slow_enemies",
        "ability_params": {"slow_factor": 0.4, "duration": 3.0},
    },
    {
        "id": 6,
        "name": "Roxy",
        "description": "Crown Princess Roxy is the Fairy of Animals.",
        "ability_name": "Beastly Charge",
        "ability_desc": "Dash forward dealing 50 damage to any enemy hit.",
        "mana_cost": 30,
        "ability_cd": 5.0,
        "ability_effect": "charge",
        "ability_params": {"speed": 900, "duration": 0.3, "damage": 50},
    },
]

CLASS_MAP = {c["id"]: c for c in CLASSES}


def get_class(class_id: int) -> dict:
    """Return class definition dict or raise KeyError."""
    return CLASS_MAP[class_id]