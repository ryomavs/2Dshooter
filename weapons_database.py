#!/usr/bin/env python3

# ===============================
# Weapons Database - All weapon specifications
# ===============================

class WeaponsDatabase:
    
    # Rarity definitions
    RARITIES = ["Common", "Uncommon", "Rare", "Epic", "Legendary", "Mythic", "Relic"]
    RARITY_PROBABILITIES = [0.5, 0.3, 0.15, 0.04, 0.01, 0.001, 0.0001]
    
    # Standard bomb specifications (Level 1-13)
    STANDARD_BOMBS = {
        1: {
            "base_stats": {
                "min_damage": 1, "max_damage": 3, "mass_kg": 50, "velocity_kmh": 792,
                "diameter_mm": 75, "length_mm": 300, "shrapnel_kg": 5.0
            },
            "rarity_effects": {
                "Common": {"damage_mult": 1.0, "effect": "None"},
                "Uncommon": {"damage_mult": 1.0, "effect": "+10% explosion area"},
                "Rare": {"damage_mult": 1.33, "effect": "Piercing explosion (ignores 20% armor/cover)"},
                "Epic": {"damage_mult": 1.33, "effect": "Cooldown reduced 15%"},
                "Legendary": {"damage_mult": 1.67, "effect": "Area +25% and pierces light shields"},
                "Mythic": {"damage_mult": 1.67, "effect": "Secondary explosion (50% damage after 1s)"},
                "Relic": {"damage_mult": 2.0, "effect": "Random elemental explosion + Cooldown -25% + Area +30%"}
            }
        },
        2: {
            "base_stats": {
                "min_damage": 2, "max_damage": 6, "mass_kg": 165, "velocity_kmh": 851,
                "diameter_mm": 95, "length_mm": 380, "shrapnel_kg": 16.5
            },
            "rarity_effects": {
                "Common": {"damage_mult": 1.0, "effect": "None"},
                "Uncommon": {"damage_mult": 1.17, "effect": "+10% explosion area"},
                "Rare": {"damage_mult": 1.17, "effect": "Piercing explosion (ignores 20% armor/cover)"},
                "Epic": {"damage_mult": 1.17, "effect": "Cooldown reduced 15%"},
                "Legendary": {"damage_mult": 1.33, "effect": "Area +25% and pierces light shields"},
                "Mythic": {"damage_mult": 1.33, "effect": "Secondary explosion (50% damage after 1s)"},
                "Relic": {"damage_mult": 1.5, "effect": "Random elemental explosion + Cooldown -25% + Area +30%"}
            }
        },
        3: {
            "base_stats": {
                "min_damage": 3, "max_damage": 9, "mass_kg": 280, "velocity_kmh": 910,
                "diameter_mm": 110, "length_mm": 450, "shrapnel_kg": 28.0
            }
        },
        4: {
            "base_stats": {
                "min_damage": 5, "max_damage": 12, "mass_kg": 395, "velocity_kmh": 969,
                "diameter_mm": 125, "length_mm": 520, "shrapnel_kg": 39.5
            }
        },
        5: {
            "base_stats": {
                "min_damage": 7, "max_damage": 15, "mass_kg": 510, "velocity_kmh": 1028,
                "diameter_mm": 140, "length_mm": 590, "shrapnel_kg": 51.0
            }
        },
        6: {
            "base_stats": {
                "min_damage": 9, "max_damage": 18, "mass_kg": 625, "velocity_kmh": 1087,
                "diameter_mm": 155, "length_mm": 660, "shrapnel_kg": 62.5
            }
        },
        7: {
            "base_stats": {
                "min_damage": 11, "max_damage": 21, "mass_kg": 740, "velocity_kmh": 1146,
                "diameter_mm": 170, "length_mm": 730, "shrapnel_kg": 74.0
            }
        },
        8: {
            "base_stats": {
                "min_damage": 13, "max_damage": 24, "mass_kg": 855, "velocity_kmh": 1205,
                "diameter_mm": 185, "length_mm": 800, "shrapnel_kg": 85.5
            }
        },
        9: {
            "base_stats": {
                "min_damage": 14, "max_damage": 27, "mass_kg": 970, "velocity_kmh": 1264,
                "diameter_mm": 200, "length_mm": 870, "shrapnel_kg": 97.0
            }
        },
        10: {
            "base_stats": {
                "min_damage": 15, "max_damage": 30, "mass_kg": 1085, "velocity_kmh": 1323,
                "diameter_mm": 215, "length_mm": 940, "shrapnel_kg": 108.5
            }
        },
        11: {
            "base_stats": {
                "min_damage": 16, "max_damage": 33, "mass_kg": 1200, "velocity_kmh": 1382,
                "diameter_mm": 230, "length_mm": 1010, "shrapnel_kg": 120.0
            }
        },
        12: {
            "base_stats": {
                "min_damage": 17, "max_damage": 36, "mass_kg": 1315, "velocity_kmh": 1441,
                "diameter_mm": 245, "length_mm": 1080, "shrapnel_kg": 131.5
            }
        },
        13: {
            "base_stats": {
                "min_damage": 15, "max_damage": 30, "mass_kg": 1350, "velocity_kmh": 1441,
                "diameter_mm": 250, "length_mm": 1100, "shrapnel_kg": 135.0
            }
        }
    }
    
    # Special bombs (MOAP/FOAB) - Player level >=100
    SPECIAL_BOMBS = {
        1: {
            "name": "MOAP Mk.I", "mass_kg": 5000, "velocity_kmh": 1000,
            "diameter_mm": 400, "length_mm": 2000, "min_damage": 50000, "max_damage": 100000,
            "shrapnel_kg": 500, "rarity": "Legendary",
            "effect": "Area +100%, ignores light armor"
        },
        2: {
            "name": "MOAP Mk.II", "mass_kg": 7500, "velocity_kmh": 1200,
            "diameter_mm": 450, "length_mm": 2200, "min_damage": 80000, "max_damage": 160000,
            "shrapnel_kg": 750, "rarity": "Legendary",
            "effect": "Cooldown -25%, kinetic damage penetrates"
        },
        3: {
            "name": "FOAB Prototype", "mass_kg": 10000, "velocity_kmh": 1500,
            "diameter_mm": 500, "length_mm": 2500, "min_damage": 150000, "max_damage": 300000,
            "shrapnel_kg": 1000, "rarity": "Mythic",
            "effect": "Dual thermal explosion, ignores shields"
        },
        4: {
            "name": "Bunker Breacher", "mass_kg": 15000, "velocity_kmh": 1200,
            "diameter_mm": 600, "length_mm": 3000, "min_damage": 200000, "max_damage": 400000,
            "shrapnel_kg": 1500, "rarity": "Mythic",
            "effect": "Penetrates defenses before detonating"
        },
        5: {
            "name": "Antimatter Warhead", "mass_kg": 20000, "velocity_kmh": 2000,
            "diameter_mm": 700, "length_mm": 3500, "min_damage": 500000, "max_damage": 1000000,
            "shrapnel_kg": 2000, "rarity": "Relic",
            "effect": "Explosion annihilates shields, ignores armor"
        },
        6: {
            "name": "Oblivion Core", "mass_kg": 25000, "velocity_kmh": 2500,
            "diameter_mm": 800, "length_mm": 4000, "min_damage": 1000000, "max_damage": 2000000,
            "shrapnel_kg": 3000, "rarity": "Relic",
            "effect": "Temporal singularity: area damage + persists 5s"
        },
        13: {
            "name": "Oblivion Core++", "mass_kg": 30000, "velocity_kmh": 2600,
            "diameter_mm": 850, "length_mm": 4200, "min_damage": 1200000, "max_damage": 2400000,
            "shrapnel_kg": 3500, "rarity": "Relic",
            "effect": "Temporal singularity: area damage + persists 5s"
        }
    }
    
    # Ship fuselage specifications
    SHIP_FUSELAGES = {
        1: {"mass_kg": 47100, "shield": 5000, "hull": 5000, "shrapnel_kg": 39985, "length_m": 120, "width_m": 80, "height_m": 25},
        2: {"mass_kg": 88000, "shield": 21000, "hull": 21000, "shrapnel_kg": 74800, "length_m": 140, "width_m": 90, "height_m": 30},
        3: {"mass_kg": 128900, "shield": 37000, "hull": 37000, "shrapnel_kg": 109565, "length_m": 160, "width_m": 100, "height_m": 35},
        4: {"mass_kg": 169800, "shield": 53000, "hull": 53000, "shrapnel_kg": 144330, "length_m": 180, "width_m": 110, "height_m": 40},
        5: {"mass_kg": 210700, "shield": 69000, "hull": 69000, "shrapnel_kg": 179095, "length_m": 200, "width_m": 120, "height_m": 45},
        6: {"mass_kg": 251600, "shield": 85000, "hull": 85000, "shrapnel_kg": 213860, "length_m": 220, "width_m": 130, "height_m": 50},
        7: {"mass_kg": 292500, "shield": 101000, "hull": 101000, "shrapnel_kg": 248625, "length_m": 240, "width_m": 140, "height_m": 55},
        8: {"mass_kg": 333400, "shield": 117000, "hull": 117000, "shrapnel_kg": 283390, "length_m": 260, "width_m": 150, "height_m": 60},
        9: {"mass_kg": 374300, "shield": 133000, "hull": 133000, "shrapnel_kg": 318155, "length_m": 280, "width_m": 160, "height_m": 65},
        10: {"mass_kg": 415200, "shield": 149000, "hull": 149000, "shrapnel_kg": 352920, "length_m": 300, "width_m": 170, "height_m": 70},
        11: {"mass_kg": 456100, "shield": 165000, "hull": 165000, "shrapnel_kg": 387685, "length_m": 320, "width_m": 180, "height_m": 75},
        12: {"mass_kg": 478000, "shield": 182000, "hull": 182000, "shrapnel_kg": 406300, "length_m": 340, "width_m": 190, "height_m": 80},
        13: {"mass_kg": 500000, "shield": 200000, "hull": 200000, "shrapnel_kg": 425000, "length_m": 360, "width_m": 200, "height_m": 85}
    }
    
    # Engine specifications
    ENGINES = {
        1: {"mass_kg": 1700, "thrust_kn": 3000, "shrapnel_kg": 1122, "length_m": 8, "diameter_m": 2.5},
        2: {"mass_kg": 3050, "thrust_kn": 7400, "shrapnel_kg": 2013, "length_m": 9, "diameter_m": 3.0},
        3: {"mass_kg": 4400, "thrust_kn": 11800, "shrapnel_kg": 2904, "length_m": 10, "diameter_m": 3.5},
        4: {"mass_kg": 5750, "thrust_kn": 16200, "shrapnel_kg": 3795, "length_m": 11, "diameter_m": 4.0},
        5: {"mass_kg": 7100, "thrust_kn": 20600, "shrapnel_kg": 4686, "length_m": 12, "diameter_m": 4.5},
        6: {"mass_kg": 8450, "thrust_kn": 25000, "shrapnel_kg": 5577, "length_m": 13, "diameter_m": 5.0},
        7: {"mass_kg": 9800, "thrust_kn": 29400, "shrapnel_kg": 6468, "length_m": 14, "diameter_m": 5.5},
        8: {"mass_kg": 11150, "thrust_kn": 33800, "shrapnel_kg": 7359, "length_m": 15, "diameter_m": 6.0},
        9: {"mass_kg": 12500, "thrust_kn": 38200, "shrapnel_kg": 8250, "length_m": 16, "diameter_m": 6.5},
        10: {"mass_kg": 13850, "thrust_kn": 42600, "shrapnel_kg": 9141, "length_m": 17, "diameter_m": 7.0},
        11: {"mass_kg": 15200, "thrust_kn": 50000, "shrapnel_kg": 11000, "length_m": 18, "diameter_m": 7.5},
        12: {"mass_kg": 16550, "thrust_kn": 54400, "shrapnel_kg": 11891, "length_m": 19, "diameter_m": 8.0},
        13: {"mass_kg": 18000, "thrust_kn": 60000, "shrapnel_kg": 13000, "length_m": 20, "diameter_m": 8.5}
    }
    
    # Kinetic projectiles (for Gunships)
    KINETIC_PROJECTILES = {
        "armor_piercing": {
            "mass_kg": 0.5, "velocity_kmh": 5000, "diameter_mm": 15, "length_mm": 80, "material": "Depleted Uranium"
        },
        "high_explosive": {
            "mass_kg": 0.8, "velocity_kmh": 4500, "diameter_mm": 20, "length_mm": 60, "material": "Steel + HE Filler"
        },
        "incendiary": {
            "mass_kg": 0.3, "velocity_kmh": 4800, "diameter_mm": 12, "length_mm": 70, "material": "Magnesium Core"
        }
    }
    
    # Energy weapons (for Energy Cruisers)
    ENERGY_WEAPONS = {
        "pulse_laser": {
            "power_mw": 50, "duration_ms": 100, "beam_diameter_mm": 5, "range_km": 10, "energy_type": "Coherent Light"
        },
        "plasma_cannon": {
            "power_mw": 150, "duration_ms": 200, "beam_diameter_mm": 20, "range_km": 8, "energy_type": "Ionized Plasma"
        },
        "ion_beam": {
            "power_mw": 200, "duration_ms": 50, "beam_diameter_mm": 2, "range_km": 15, "energy_type": "Particle Beam"
        }
    }
    
    @staticmethod
    def get_standard_bomb(level, rarity):
        """Get standard bomb specifications for given level and rarity"""
        if level not in WeaponsDatabase.STANDARD_BOMBS:
            return None
        
        base_stats = WeaponsDatabase.STANDARD_BOMBS[level]["base_stats"]
        
        # Apply rarity effects if they exist for this level
        if "rarity_effects" in WeaponsDatabase.STANDARD_BOMBS[level] and rarity in WeaponsDatabase.STANDARD_BOMBS[level]["rarity_effects"]:
            rarity_data = WeaponsDatabase.STANDARD_BOMBS[level]["rarity_effects"][rarity]
            damage_mult = rarity_data["damage_mult"]
            effect = rarity_data["effect"]
        else:
            # Use generic rarity multipliers
            rarity_multipliers = {
                "Common": 1.0, "Uncommon": 1.1, "Rare": 1.2, "Epic": 1.35,
                "Legendary": 1.5, "Mythic": 1.75, "Relic": 2.0
            }
            damage_mult = rarity_multipliers.get(rarity, 1.0)
            effect = "None"
        
        return {
            "min_damage": int(base_stats["min_damage"] * damage_mult),
            "max_damage": int(base_stats["max_damage"] * damage_mult),
            "mass_kg": base_stats["mass_kg"],
            "velocity_kmh": base_stats["velocity_kmh"],
            "diameter_mm": base_stats["diameter_mm"],
            "length_mm": base_stats["length_mm"],
            "shrapnel_kg": base_stats["shrapnel_kg"],
            "effect": effect
        }
    
    @staticmethod
    def get_special_bomb(level):
        """Get special bomb specifications for given level"""
        return WeaponsDatabase.SPECIAL_BOMBS.get(level)
    
    @staticmethod
    def get_ship_fuselage(level):
        """Get ship fuselage specifications for given level"""
        return WeaponsDatabase.SHIP_FUSELAGES.get(level)
    
    @staticmethod
    def get_engine(level):
        """Get engine specifications for given level"""
        return WeaponsDatabase.ENGINES.get(level)
    
    @staticmethod
    def get_kinetic_projectile(projectile_type):
        """Get kinetic projectile specifications"""
        return WeaponsDatabase.KINETIC_PROJECTILES.get(projectile_type)
    
    @staticmethod
    def get_energy_weapon(weapon_type):
        """Get energy weapon specifications"""
        return WeaponsDatabase.ENERGY_WEAPONS.get(weapon_type)

