#!/usr/bin/env python3
import pygame
import math
import random

class PlayerStats:
    """Player character stats and progression"""
    
    def __init__(self):
        # Core stats
        self.level = 1
        self.experience = 0
        self.stat_points = 0
        
        # Base attributes
        self.attack = 1      # +1kg explosive per point
        self.defense = 1     # +5% damage resistance per point
        self.evasion = 1     # +3% dodge chance per point
        self.shield = 1      # +500J capacity + 10J/s regen per point
        
        # Derived stats (calculated from attributes)
        self.explosive_bonus_kg = 0
        self.damage_resistance = 0
        self.dodge_chance = 0
        self.shield_capacity_bonus = 0
        self.shield_regen_bonus = 0
        
        self._calculate_derived_stats()
        
    def add_experience(self, exp_amount):
        """Add experience and check for level up"""
        self.experience += exp_amount
        old_level = self.level
        
        while self.experience >= self.get_exp_requirement():
            self.level_up()
        
        return self.level > old_level  # Return True if leveled up
    
    def get_exp_requirement(self):
        """Get experience required for next level"""
        return 100 + (self.level - 1) * 50  # 100, 150, 200, 250...
    
    def level_up(self):
        """Level up the player"""
        exp_required = self.get_exp_requirement()
        self.experience -= exp_required
        self.level += 1
        self.stat_points += 1
        
        print(f"LEVEL UP! Now level {self.level}")
        return True
    
    def allocate_stat_point(self, stat_name):
        """Allocate a stat point to an attribute"""
        if self.stat_points <= 0:
            return False
        
        if stat_name == "attack":
            self.attack += 1
        elif stat_name == "defense":
            self.defense += 1
        elif stat_name == "evasion":
            self.evasion += 1
        elif stat_name == "shield":
            self.shield += 1
        else:
            return False
        
        self.stat_points -= 1
        self._calculate_derived_stats()
        print(f"Allocated point to {stat_name}. Remaining points: {self.stat_points}")
        return True
    
    def _calculate_derived_stats(self):
        """Calculate derived stats from attributes"""
        self.explosive_bonus_kg = (self.attack - 1) * 1.0  # +1kg per point above 1
        self.damage_resistance = min(0.75, (self.defense - 1) * 0.05)  # +5% per point, max 75%
        self.dodge_chance = min(0.50, (self.evasion - 1) * 0.03)  # +3% per point, max 50%
        self.shield_capacity_bonus = (self.shield - 1) * 500  # +500J per point
        self.shield_regen_bonus = (self.shield - 1) * 10  # +10J/s per point
    
    def get_stat_summary(self):
        """Get formatted stat summary"""
        return {
            'level': self.level,
            'experience': self.experience,
            'exp_requirement': self.get_exp_requirement(),
            'stat_points': self.stat_points,
            'attack': self.attack,
            'defense': self.defense,
            'evasion': self.evasion,
            'shield': self.shield,
            'explosive_bonus_kg': self.explosive_bonus_kg,
            'damage_resistance': f"{self.damage_resistance*100:.1f}%",
            'dodge_chance': f"{self.dodge_chance*100:.1f}%",
            'shield_capacity_bonus': self.shield_capacity_bonus,
            'shield_regen_bonus': self.shield_regen_bonus
        }


class DropSystem:
    """Handles item drops from enemies"""
    
    def __init__(self):
        self.drop_chance = 0.3  # 30% chance
        
    def check_drop(self, enemy_level=1):
        """Check if enemy drops items"""
        if random.random() < self.drop_chance:
            # Calculate Kerr Scrap amount based on enemy level
            base_scrap = random.randint(1, 3)
            level_bonus = enemy_level - 1
            total_scrap = base_scrap + level_bonus
            
            return {
                'type': 'kerr_scrap',
                'amount': total_scrap,
                'level': enemy_level
            }
        return None


class Inventory:
    """Player inventory system"""
    
    def __init__(self):
        self.kerr_scrap = 0
        self.items = {}
        self.visible = False
        
    def add_item(self, item_type, amount=1):
        """Add item to inventory"""
        if item_type == 'kerr_scrap':
            self.kerr_scrap += amount
            print(f"Collected {amount} Kerr Scrap! Total: {self.kerr_scrap}")
            return True
        
        if item_type not in self.items:
            self.items[item_type] = 0
        self.items[item_type] += amount
        return True
    
    def remove_item(self, item_type, amount=1):
        """Remove item from inventory"""
        if item_type == 'kerr_scrap':
            if self.kerr_scrap >= amount:
                self.kerr_scrap -= amount
                return True
            return False
        
        if item_type in self.items and self.items[item_type] >= amount:
            self.items[item_type] -= amount
            if self.items[item_type] <= 0:
                del self.items[item_type]
            return True
        return False
    
    def toggle_visibility(self):
        """Toggle inventory display"""
        self.visible = not self.visible
        print(f"Inventory {'opened' if self.visible else 'closed'}")
        return self.visible
    
    def get_inventory_data(self):
        """Get inventory data for UI"""
        return {
            'kerr_scrap': self.kerr_scrap,
            'items': self.items.copy(),
            'visible': self.visible
        }


class PerkSystem:
    """Perk system using Kerr Scrap"""
    
    def __init__(self, inventory):
        self.inventory = inventory
        self.active_perks = set()
        
        # Perk definitions
        self.perks = {
            'explosive_master': {
                'name': 'Explosive Master',
                'description': '+25% explosive damage',
                'cost': 50,
                'effect': 'explosive_damage_mult',
                'value': 1.25
            },
            'shield_boost': {
                'name': 'Shield Booster',
                'description': '+50% shield capacity',
                'cost': 40,
                'effect': 'shield_capacity_mult',
                'value': 1.5
            },
            'rapid_reload': {
                'name': 'Rapid Reload',
                'description': '-25% weapon cooldowns',
                'cost': 60,
                'effect': 'cooldown_mult',
                'value': 0.75
            },
            'lucky_drops': {
                'name': 'Lucky Drops',
                'description': '+50% drop chance',
                'cost': 30,
                'effect': 'drop_chance_mult',
                'value': 1.5
            }
        }
    
    def can_purchase(self, perk_id):
        """Check if perk can be purchased"""
        if perk_id not in self.perks:
            return False
        if perk_id in self.active_perks:
            return False
        
        perk = self.perks[perk_id]
        return self.inventory.kerr_scrap >= perk['cost']
    
    def purchase_perk(self, perk_id):
        """Purchase a perk"""
        if not self.can_purchase(perk_id):
            return False
        
        perk = self.perks[perk_id]
        if self.inventory.remove_item('kerr_scrap', perk['cost']):
            self.active_perks.add(perk_id)
            print(f"Purchased perk: {perk['name']}")
            return True
        return False
    
    def get_active_effects(self):
        """Get all active perk effects"""
        effects = {}
        for perk_id in self.active_perks:
            perk = self.perks[perk_id]
            effect_name = perk['effect']
            if effect_name not in effects:
                effects[effect_name] = 1.0
            
            # Apply multiplicative effects
            if 'mult' in effect_name:
                effects[effect_name] *= perk['value']
            else:
                effects[effect_name] += perk['value']
        
        return effects


class ProgressionManager:
    """Main progression system manager"""
    
    def __init__(self):
        self.player_stats = PlayerStats()
        self.drop_system = DropSystem()
        self.inventory = Inventory()
        self.perk_system = PerkSystem(self.inventory)
        
        # UI state
        self.show_level_up = False
        self.level_up_timer = 0
        self.show_stat_allocation = False
        
    def on_enemy_killed(self, enemy_level=1, enemy_type="fighter"):
        """Handle enemy death - award exp and check drops"""
        # Award experience
        base_exp = 10
        level_bonus = enemy_level * 2
        type_bonus = {'fighter': 0, 'bomber': 5, 'scout': 3}.get(enemy_type, 0)
        
        total_exp = base_exp + level_bonus + type_bonus
        leveled_up = self.player_stats.add_experience(total_exp)
        
        if leveled_up:
            self.show_level_up = True
            self.level_up_timer = 3.0
        
        # Check for drops
        drop = self.drop_system.check_drop(enemy_level)
        if drop:
            self.inventory.add_item(drop['type'], drop['amount'])
        
        return {
            'exp_gained': total_exp,
            'leveled_up': leveled_up,
            'drop': drop
        }
    
    def update(self, delta_time):
        """Update progression systems"""
        # Update level up notification
        if self.level_up_timer > 0:
            self.level_up_timer -= delta_time
            if self.level_up_timer <= 0:
                self.show_level_up = False
                # Auto-open stat allocation if player has points
                if self.player_stats.stat_points > 0:
                    self.show_stat_allocation = True
    
    def handle_input(self, key):
        """Handle progression-related input"""
        if key == pygame.K_i:
            self.inventory.toggle_visibility()
            return True
        
        if key == pygame.K_c and self.player_stats.stat_points > 0:
            self.show_stat_allocation = not self.show_stat_allocation
            return True
        
        # Stat allocation keys
        if self.show_stat_allocation:
            if key == pygame.K_1:
                return self.player_stats.allocate_stat_point("attack")
            elif key == pygame.K_2:
                return self.player_stats.allocate_stat_point("defense")
            elif key == pygame.K_3:
                return self.player_stats.allocate_stat_point("evasion")
            elif key == pygame.K_4:
                return self.player_stats.allocate_stat_point("shield")
        
        return False
    
    def get_weapon_modifiers(self):
        """Get weapon modifiers based on stats"""
        modifiers = {
            'explosive_bonus_kg': self.player_stats.explosive_bonus_kg,
            'damage_resistance': self.player_stats.damage_resistance,
            'dodge_chance': self.player_stats.dodge_chance,
            'shield_capacity_bonus': self.player_stats.shield_capacity_bonus,
            'shield_regen_bonus': self.player_stats.shield_regen_bonus
        }
        
        # Apply perk effects
        perk_effects = self.perk_system.get_active_effects()
        for effect, value in perk_effects.items():
            if effect == 'explosive_damage_mult':
                modifiers['explosive_damage_mult'] = value
            elif effect == 'cooldown_mult':
                modifiers['cooldown_mult'] = value
            elif effect == 'shield_capacity_mult':
                modifiers['shield_capacity_mult'] = value
            elif effect == 'drop_chance_mult':
                self.drop_system.drop_chance *= value
        
        return modifiers
    
    def get_ui_data(self):
        """Get data for UI rendering"""
        return {
            'stats': self.player_stats.get_stat_summary(),
            'inventory': self.inventory.get_inventory_data(),
            'show_level_up': self.show_level_up,
            'show_stat_allocation': self.show_stat_allocation,
            'available_perks': self.perk_system.perks,
            'active_perks': self.perk_system.active_perks
        }