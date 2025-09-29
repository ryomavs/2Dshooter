#!/usr/bin/env python3
import pygame
import math
import random

class RPGBombSystem:
    """RPG-style bomb system with crafting effects"""
    
    def __init__(self):
        # Base bomb properties (levels 1-13)
        self.base_explosive_kg = {
            1: 0.5,   # 0.5kg TNT equivalent
            2: 0.8,
            3: 1.2,
            4: 1.8,
            5: 2.5,
            6: 3.5,
            7: 4.8,
            8: 6.5,
            9: 8.5,
            10: 11.0,
            11: 14.0,
            12: 18.0,
            13: 23.0
        }
        
        # Energy per kg of explosive (TNT equivalent)
        self.ENERGY_PER_KG = 4184000  # 4.184 MJ per kg
        
        # Base bomb properties
        self.base_cooldown = 4.0  # 4 seconds base cooldown
        self.base_flight_time = 3.2  # 3.2 seconds max flight time
        self.base_proximity_radius = 25  # 25 pixels proximity trigger
        self.normal_bomb_count = 1  # Normal single bomb
        
        # Breach_Bomb skill multiplier
        self.breach_bomb_multiplier = 5  # 5x bombs when using Breach_Bomb
        
        # Crafting effects (will be applied from inventory/perks)
        self.cooldown_reduction = 0.0  # 0-100% reduction
        self.hit_chance_bonus = 0.0   # 0-100% bonus to hit chance
        self.penetration = 0.0        # 0-100% defense penetration
        
        print("RPG Bomb System initialized with realistic TNT calculations")
    
    def get_bomb_energy(self, level):
        """Calculate bomb energy in joules"""
        explosive_kg = self.base_explosive_kg.get(level, 0.5)
        return explosive_kg * self.ENERGY_PER_KG
    
    def calculate_bomb_damage(self, level, use_breach_bomb=False, crafting_effects=None):
        """Calculate total bomb damage with all modifiers"""
        # Base energy per bomb
        energy_per_bomb = self.get_bomb_energy(level)
        
        # Number of bombs fired
        if use_breach_bomb:
            num_bombs = self.normal_bomb_count * self.breach_bomb_multiplier
        else:
            num_bombs = self.normal_bomb_count
        
        # Total damage
        total_damage = energy_per_bomb * num_bombs
        
        # Apply crafting effects if provided
        if crafting_effects:
            # Penetration affects how damage bypasses defense
            penetration = crafting_effects.get('penetration', self.penetration)
            hit_bonus = crafting_effects.get('hit_chance_bonus', self.hit_chance_bonus)
            
            return {
                'total_damage': total_damage,
                'energy_per_bomb': energy_per_bomb,
                'num_bombs': num_bombs,
                'penetration': penetration,
                'hit_chance_bonus': hit_bonus
            }
        
        return {
            'total_damage': total_damage,
            'energy_per_bomb': energy_per_bomb,
            'num_bombs': num_bombs,
            'penetration': self.penetration,
            'hit_chance_bonus': self.hit_chance_bonus
        }
    
    def get_cooldown(self, crafting_effects=None):
        """Get actual cooldown after crafting reductions"""
        cooldown_reduction = self.cooldown_reduction
        if crafting_effects and 'cooldown_reduction' in crafting_effects:
            cooldown_reduction = crafting_effects['cooldown_reduction']
        
        return self.base_cooldown * (1.0 - cooldown_reduction)
    
    def apply_damage_to_enemy(self, bomb_damage_data, enemy_defense, enemy_evasion):
        """Apply bomb damage to enemy with defense and evasion"""
        total_damage = bomb_damage_data['total_damage']
        penetration = bomb_damage_data['penetration']
        hit_bonus = bomb_damage_data['hit_chance_bonus']
        
        # Calculate hit probability
        base_hit_chance = 0.85  # 85% base hit chance
        final_hit_chance = min(0.95, base_hit_chance + hit_bonus - enemy_evasion)
        
        # Check if attack hits
        if random.random() > final_hit_chance:
            return 0, "MISSED"
        
        # Apply defense with penetration
        effective_defense = enemy_defense * (1.0 - penetration)
        final_damage = total_damage * (1.0 - effective_defense)
        
        return max(0, final_damage), "HIT"


class InventorySystem:
    """Complete inventory system with crafting materials"""
    
    def __init__(self):
        # Resources
        self.kerr_scrap = 0
        self.rare_metals = 0
        self.energy_cores = 0
        
        # Crafting components  
        self.explosive_compounds = 0
        self.targeting_modules = 0
        self.armor_piercing_tips = 0
        self.coolant_systems = 0
        
        # Crafted upgrades
        self.bomb_upgrades = {
            'cooldown_reduction': 0.0,    # 0-75% reduction
            'hit_chance_bonus': 0.0,      # 0-50% bonus
            'penetration': 0.0,           # 0-60% defense penetration
        }
        
        # UI state
        self.visible = False
        self.selected_tab = "inventory"  # "inventory", "crafting", "upgrades"
        
        # Drop rates
        self.drop_rates = {
            'kerr_scrap': 0.6,           # 60% chance
            'rare_metals': 0.15,         # 15% chance
            'energy_cores': 0.08,        # 8% chance
            'explosive_compounds': 0.12, # 12% chance
            'targeting_modules': 0.10,   # 10% chance
            'armor_piercing_tips': 0.08, # 8% chance
            'coolant_systems': 0.06      # 6% chance
        }
    
    def add_item(self, item_type, amount=1):
        """Add item to inventory"""
        if hasattr(self, item_type):
            current = getattr(self, item_type)
            setattr(self, item_type, current + amount)
            print(f"Collected {amount} {item_type.replace('_', ' ').title()}! Total: {current + amount}")
            return True
        return False
    
    def remove_item(self, item_type, amount=1):
        """Remove item from inventory"""
        if hasattr(self, item_type):
            current = getattr(self, item_type)
            if current >= amount:
                setattr(self, item_type, current - amount)
                return True
        return False
    
    def can_craft_upgrade(self, upgrade_type):
        """Check if upgrade can be crafted"""
        recipes = {
            'cooldown_reduction': {
                'kerr_scrap': 25,
                'coolant_systems': 3,
                'energy_cores': 1
            },
            'hit_chance_bonus': {
                'kerr_scrap': 30,
                'targeting_modules': 4,
                'rare_metals': 2
            },
            'penetration': {
                'kerr_scrap': 35,
                'armor_piercing_tips': 5,
                'explosive_compounds': 3
            }
        }
        
        recipe = recipes.get(upgrade_type)
        if not recipe:
            return False
        
        for item, required in recipe.items():
            if getattr(self, item, 0) < required:
                return False
        
        return True
    
    def craft_upgrade(self, upgrade_type):
        """Craft an upgrade"""
        if not self.can_craft_upgrade(upgrade_type):
            return False
        
        recipes = {
            'cooldown_reduction': {
                'kerr_scrap': 25,
                'coolant_systems': 3,
                'energy_cores': 1,
                'effect': 0.15  # +15% cooldown reduction
            },
            'hit_chance_bonus': {
                'kerr_scrap': 30,
                'targeting_modules': 4,
                'rare_metals': 2,
                'effect': 0.10  # +10% hit chance
            },
            'penetration': {
                'kerr_scrap': 35,
                'armor_piercing_tips': 5,
                'explosive_compounds': 3,
                'effect': 0.12  # +12% penetration
            }
        }
        
        recipe = recipes[upgrade_type]
        effect_amount = recipe['effect']
        
        # Consume materials
        for item, required in recipe.items():
            if item != 'effect':
                current = getattr(self, item)
                setattr(self, item, current - required)
        
        # Apply upgrade (with caps)
        current_upgrade = self.bomb_upgrades[upgrade_type]
        max_upgrades = {'cooldown_reduction': 0.75, 'hit_chance_bonus': 0.50, 'penetration': 0.60}
        
        new_value = min(max_upgrades[upgrade_type], current_upgrade + effect_amount)
        self.bomb_upgrades[upgrade_type] = new_value
        
        print(f"Crafted {upgrade_type.replace('_', ' ').title()}: {new_value*100:.1f}%")
        return True
    
    def toggle_visibility(self):
        """Toggle inventory display"""
        self.visible = not self.visible
        print(f"Inventory {'opened' if self.visible else 'closed'}")
        return self.visible
    
    def get_inventory_data(self):
        """Get complete inventory data for UI"""
        return {
            'visible': self.visible,
            'selected_tab': self.selected_tab,
            'resources': {
                'kerr_scrap': self.kerr_scrap,
                'rare_metals': self.rare_metals,
                'energy_cores': self.energy_cores
            },
            'components': {
                'explosive_compounds': self.explosive_compounds,
                'targeting_modules': self.targeting_modules,
                'armor_piercing_tips': self.armor_piercing_tips,
                'coolant_systems': self.coolant_systems
            },
            'upgrades': self.bomb_upgrades.copy()
        }


class DropSystem:
    """Enhanced drop system with multiple item types"""
    
    def __init__(self, inventory_system):
        self.inventory = inventory_system
        
        # Drop weights by enemy type
        self.enemy_drop_weights = {
            'fighter': {
                'kerr_scrap': 50,
                'rare_metals': 10,
                'targeting_modules': 15
            },
            'bomber': {
                'kerr_scrap': 40,
                'explosive_compounds': 25,
                'energy_cores': 15,
                'coolant_systems': 8
            },
            'scout': {
                'kerr_scrap': 60,
                'rare_metals': 20,
                'armor_piercing_tips': 12
            }
        }
    
    def calculate_drops(self, enemy_type, enemy_level):
        """Calculate what drops from an enemy"""
        drops = []
        drop_weights = self.enemy_drop_weights.get(enemy_type, {'kerr_scrap': 100})
        
        # Base drop chance increases with enemy level
        base_chance = 0.3 + (enemy_level - 1) * 0.05  # 30% + 5% per level
        
        if random.random() < base_chance:
            # Determine what drops
            total_weight = sum(drop_weights.values())
            rand_val = random.randint(1, total_weight)
            
            cumulative = 0
            for item_type, weight in drop_weights.items():
                cumulative += weight
                if rand_val <= cumulative:
                    # Determine amount based on enemy level
                    base_amount = 1 + (enemy_level - 1) // 2
                    amount = random.randint(base_amount, base_amount + 2)
                    
                    drops.append({
                        'type': item_type,
                        'amount': amount,
                        'level': enemy_level
                    })
                    break
        
        # Rare chance for bonus drop
        if enemy_level >= 5 and random.random() < 0.1:
            bonus_items = ['energy_cores', 'rare_metals', 'explosive_compounds']
            bonus_item = random.choice(bonus_items)
            drops.append({
                'type': bonus_item,
                'amount': 1,
                'level': enemy_level
            })
        
        return drops
    
    def award_drops(self, enemy_type, enemy_level):
        """Award drops to inventory"""
        drops = self.calculate_drops(enemy_type, enemy_level)
        
        for drop in drops:
            self.inventory.add_item(drop['type'], drop['amount'])
        
        return drops


class ProgressionIntegrator:
    """Integrates RPG bomb system with existing progression"""
    
    def __init__(self):
        self.rpg_bombs = RPGBombSystem()
        self.inventory = InventorySystem()
        self.drop_system = DropSystem(self.inventory)
        
        # Player stats
        self.player_level = 1
        self.experience = 0
        self.stat_points = 0
        
        # Ship stats
        self.attack = 1      # Affects bomb level
        self.defense = 1     # Damage resistance
        self.evasion = 1     # Dodge chance
        self.shield = 1      # Shield capacity
        
        # UI state
        self.show_level_up = False
        self.level_up_timer = 0
        self.show_stat_allocation = False
    
    def get_bomb_level(self):
        """Get current bomb level based on attack stat"""
        return min(13, self.attack)  # Attack stat determines bomb level (max 13)
    
    def fire_breach_bomb(self, projectile_manager, ship_pos):
        """Fire breach bomb with RPG mechanics"""
        bomb_level = self.get_bomb_level()
        crafting_effects = self.inventory.bomb_upgrades
        
        # Calculate bomb properties
        bomb_data = self.rpg_bombs.calculate_bomb_damage(
            bomb_level, 
            use_breach_bomb=True, 
            crafting_effects=crafting_effects
        )
        
        # Create multiple bombs for Breach_Bomb skill
        num_bombs = bomb_data['num_bombs']  # 5 bombs
        energy_per_bomb = bomb_data['energy_per_bomb']
        
        # Calculate spread pattern for multiple bombs
        angles = []
        if num_bombs == 5:
            # 5-bomb spread pattern
            center_angle = -math.pi / 2  # Straight up
            spread = math.pi / 8  # 22.5 degrees spread
            
            angles = [
                center_angle,
                center_angle - spread/2,
                center_angle + spread/2,
                center_angle - spread,
                center_angle + spread
            ]
        else:
            angles = [-math.pi / 2]  # Single bomb straight up
        
        # Launch bombs
        for angle in angles:
            # Convert energy back to bomb stats for projectile manager
            explosive_kg = energy_per_bomb / self.rpg_bombs.ENERGY_PER_KG
            
            bomb_stats = {
                "min_damage": int(energy_per_bomb * 0.8),
                "max_damage": int(energy_per_bomb * 1.2),
                "mass_kg": max(1.0, explosive_kg * 3),  # Total mass including casing
                "velocity_kmh": 800,
                "diameter_mm": 75 + bomb_level * 5,
                "length_mm": 300 + bomb_level * 20,
                "shrapnel_kg": explosive_kg * 2,  # 2x explosive weight in shrapnel
                "penetration": crafting_effects.get('penetration', 0),
                "hit_bonus": crafting_effects.get('hit_chance_bonus', 0)
            }
            
            # Calculate velocity
            velocity_ms = bomb_stats["velocity_kmh"] * 1000 / 3600
            vx = math.cos(angle) * velocity_ms
            vy = math.sin(angle) * velocity_ms
            
            # Add to projectile manager
            projectile_manager.add_bomb(
                ship_pos[0], ship_pos[1] - 25,
                vx, vy,
                bomb_stats,
                f"breach_bomb_{random.randint(1000, 9999)}"
            )
        
        # Return cooldown
        return self.rpg_bombs.get_cooldown(crafting_effects)
    
    def on_enemy_killed(self, enemy_type, enemy_level):
        """Handle enemy death with drops and experience"""
        # Award experience
        base_exp = 10 + enemy_level * 3
        self.experience += base_exp
        
        # Check for level up
        exp_needed = 100 + (self.player_level - 1) * 50
        leveled_up = False
        
        if self.experience >= exp_needed:
            self.experience -= exp_needed
            self.player_level += 1
            self.stat_points += 1
            leveled_up = True
            self.show_level_up = True
            self.level_up_timer = 3.0
            print(f"LEVEL UP! Now level {self.player_level}")
        
        # Award drops
        drops = self.drop_system.award_drops(enemy_type, enemy_level)
        
        return {
            'exp_gained': base_exp,
            'leveled_up': leveled_up,
            'drops': drops
        }
    
    def allocate_stat_point(self, stat_name):
        """Allocate stat point"""
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
        print(f"Allocated point to {stat_name}. New bomb level: {self.get_bomb_level()}")
        return True
    
    def handle_input(self, key):
        """Handle progression input"""
        if key == pygame.K_i:
            return self.inventory.toggle_visibility()
        
        if key == pygame.K_c and self.stat_points > 0:
            self.show_stat_allocation = not self.show_stat_allocation
            return True
        
        # Stat allocation
        if self.show_stat_allocation:
            if key == pygame.K_1:
                return self.allocate_stat_point("attack")
            elif key == pygame.K_2:
                return self.allocate_stat_point("defense")
            elif key == pygame.K_3:
                return self.allocate_stat_point("evasion")
            elif key == pygame.K_4:
                return self.allocate_stat_point("shield")
        
        # Crafting keys (when inventory is open)
        if self.inventory.visible:
            if key == pygame.K_q:
                return self.inventory.craft_upgrade('cooldown_reduction')
            elif key == pygame.K_w:
                return self.inventory.craft_upgrade('hit_chance_bonus')
            elif key == pygame.K_e:
                return self.inventory.craft_upgrade('penetration')
        
        return False
    
    def update(self, delta_time):
        """Update progression systems"""
        if self.level_up_timer > 0:
            self.level_up_timer -= delta_time
            if self.level_up_timer <= 0:
                self.show_level_up = False
                if self.stat_points > 0:
                    self.show_stat_allocation = True
    
    def get_ui_data(self):
        """Get all UI data"""
        return {
            'player': {
                'level': self.player_level,
                'experience': self.experience,
                'exp_needed': 100 + (self.player_level - 1) * 50,
                'stat_points': self.stat_points,
                'attack': self.attack,
                'defense': self.defense,
                'evasion': self.evasion,
                'shield': self.shield,
                'bomb_level': self.get_bomb_level()
            },
            'inventory': self.inventory.get_inventory_data(),
            'show_level_up': self.show_level_up,
            'show_stat_allocation': self.show_stat_allocation
        }
    
    def get_weapon_modifiers(self):
        """Get weapon modifiers for ship integration"""
        return {
            'bomb_level': self.get_bomb_level(),
            'cooldown_reduction': self.inventory.bomb_upgrades['cooldown_reduction'],
            'hit_chance_bonus': self.inventory.bomb_upgrades['hit_chance_bonus'],
            'penetration': self.inventory.bomb_upgrades['penetration'],
            'damage_resistance': (self.defense - 1) * 0.05,  # 5% per defense point
            'dodge_chance': (self.evasion - 1) * 0.03,       # 3% per evasion point
            'shield_capacity_bonus': (self.shield - 1) * 500, # 500J per shield point
            'shield_regen_bonus': (self.shield - 1) * 10      # 10J/s per shield point
        }


class InventoryUI:
    """UI renderer for the inventory system"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Font setup
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Colors
        self.colors = {
            'background': (20, 20, 40, 200),
            'panel': (40, 40, 80),
            'border': (100, 100, 200),
            'text': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'text_highlight': (255, 255, 100),
            'button': (60, 60, 120),
            'button_hover': (80, 80, 140),
            'resource': (100, 255, 100),
            'component': (255, 100, 255),
            'upgrade': (255, 255, 100)
        }
    
    def draw_inventory(self, screen, inventory_data, player_data):
        """Draw complete inventory interface"""
        if not inventory_data['visible']:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = min(800, self.screen_width - 100)
        panel_height = min(600, self.screen_height - 100)
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['background'])
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, panel_width, panel_height), 3)
        
        # Title
        title = self.font_large.render("INVENTORY & CRAFTING", True, self.colors['text_highlight'])
        title_rect = title.get_rect(center=(panel_width//2, 30))
        panel_surface.blit(title, title_rect)
        
        # Player info
        player_info_y = 60
        player_texts = [
            f"Level {player_data['level']} (Bomb Level {player_data['bomb_level']})",
            f"Attack: {player_data['attack']} | Defense: {player_data['defense']} | Evasion: {player_data['evasion']} | Shield: {player_data['shield']}",
            f"Stat Points Available: {player_data['stat_points']}"
        ]
        
        for i, text in enumerate(player_texts):
            color = self.colors['text_highlight'] if player_data['stat_points'] > 0 and i == 2 else self.colors['text']
            text_surface = self.font_medium.render(text, True, color)
            panel_surface.blit(text_surface, (20, player_info_y + i * 25))
        
        # Resources section
        resources_y = 150
        self._draw_section_title(panel_surface, "RESOURCES", resources_y)
        
        resources = inventory_data['resources']
        resource_items = [
            f"Kerr Scrap: {resources['kerr_scrap']}",
            f"Rare Metals: {resources['rare_metals']}",
            f"Energy Cores: {resources['energy_cores']}"
        ]
        
        for i, item in enumerate(resource_items):
            text_surface = self.font_small.render(item, True, self.colors['resource'])
            panel_surface.blit(text_surface, (40, resources_y + 30 + i * 20))
        
        # Components section
        components_y = 270
        self._draw_section_title(panel_surface, "COMPONENTS", components_y)
        
        components = inventory_data['components']
        component_items = [
            f"Explosive Compounds: {components['explosive_compounds']}",
            f"Targeting Modules: {components['targeting_modules']}",
            f"Armor Piercing Tips: {components['armor_piercing_tips']}",
            f"Coolant Systems: {components['coolant_systems']}"
        ]
        
        for i, item in enumerate(component_items):
            text_surface = self.font_small.render(item, True, self.colors['component'])
            panel_surface.blit(text_surface, (40, components_y + 30 + i * 20))
        
        # Upgrades section
        upgrades_y = 390
        self._draw_section_title(panel_surface, "BOMB UPGRADES", upgrades_y)
        
        upgrades = inventory_data['upgrades']
        upgrade_items = [
            f"Cooldown Reduction: {upgrades['cooldown_reduction']*100:.1f}% [Q to craft]",
            f"Hit Chance Bonus: {upgrades['hit_chance_bonus']*100:.1f}% [W to craft]",
            f"Defense Penetration: {upgrades['penetration']*100:.1f}% [E to craft]"
        ]
        
        for i, item in enumerate(upgrade_items):
            text_surface = self.font_small.render(item, True, self.colors['upgrade'])
            panel_surface.blit(text_surface, (40, upgrades_y + 30 + i * 20))
        
        # Controls
        controls_y = panel_height - 80
        controls = [
            "Controls: I - Close | C - Stat Allocation | Q/W/E - Craft Upgrades | 1-4 - Allocate Stats",
            "Bomb System: Attack stat determines bomb level (1-13) | Breach_Bomb fires 5 bombs instead of 1"
        ]
        
        for i, control in enumerate(controls):
            text_surface = self.font_small.render(control, True, self.colors['text_secondary'])
            panel_surface.blit(text_surface, (20, controls_y + i * 20))
        
        screen.blit(panel_surface, (panel_x, panel_y))
    
    def _draw_section_title(self, surface, title, y):
        """Draw section title with underline"""
        title_surface = self.font_medium.render(title, True, self.colors['text_highlight'])
        surface.blit(title_surface, (20, y))
        
        # Underline
        pygame.draw.line(surface, self.colors['border'], 
                        (20, y + 25), (200, y + 25), 2)
    
    def draw_stat_allocation(self, screen, player_data):
        """Draw stat allocation screen"""
        if not player_data.get('show_stat_allocation', False):
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Panel
        panel_width = 600
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['background'])
        pygame.draw.rect(panel_surface, self.colors['text_highlight'], 
                        (0, 0, panel_width, panel_height), 3)
        
        # Title
        title = f"ALLOCATE STAT POINTS ({player_data['stat_points']} available)"
        title_surface = self.font_large.render(title, True, self.colors['text_highlight'])
        title_rect = title_surface.get_rect(center=(panel_width//2, 40))
        panel_surface.blit(title_surface, title_rect)
        
        # Stat options
        stats = [
            ("1", "ATTACK", player_data['attack'], f"Bomb Level: {player_data['bomb_level']} → {min(13, player_data['attack'] + 1)}"),
            ("2", "DEFENSE", player_data['defense'], f"Damage Resist: {(player_data['defense']-1)*5:.0f}% → {player_data['defense']*5:.0f}%"),
            ("3", "EVASION", player_data['evasion'], f"Dodge Chance: {(player_data['evasion']-1)*3:.0f}% → {player_data['evasion']*3:.0f}%"),
            ("4", "SHIELD", player_data['shield'], f"Capacity: +{(player_data['shield']-1)*500:.0f}J → +{player_data['shield']*500:.0f}J")
        ]
        
        y_offset = 100
        for key, name, current, effect in stats:
            # Key and name
            key_text = f"[{key}] {name}: {current}"
            key_surface = self.font_medium.render(key_text, True, self.colors['text'])
            panel_surface.blit(key_surface, (50, y_offset))
            
            # Effect
            effect_surface = self.font_small.render(effect, True, self.colors['text_secondary'])
            panel_surface.blit(effect_surface, (70, y_offset + 25))
            
            y_offset += 60
        
        # Controls
        control_text = "Press 1-4 to allocate points | C to close"
        control_surface = self.font_small.render(control_text, True, self.colors['text_secondary'])
        panel_surface.blit(control_surface, (50, panel_height - 40))
        
        screen.blit(panel_surface, (panel_x, panel_y))
    
    def draw_level_up_notification(self, screen, player_data):
        """Draw level up notification"""
        if not player_data.get('show_level_up', False):
            return
        
        # Center notification
        panel_width = 500
        panel_height = 150
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        # Pulsing background
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        alpha = int(180 + 60 * pulse)
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['text_highlight'][:3], alpha))
        pygame.draw.rect(panel_surface, self.colors['text'], 
                        (0, 0, panel_width, panel_height), 4)
        
        # Text
        level_text = f"LEVEL UP! Now Level {player_data['level']}"
        level_surface = self.font_large.render(level_text, True, (0, 0, 0))
        level_rect = level_surface.get_rect(center=(panel_width//2, 60))
        panel_surface.blit(level_surface, level_rect)
        
        if player_data['stat_points'] > 0:
            points_text = f"You have {player_data['stat_points']} stat points! Press C to allocate"
            points_surface = self.font_medium.render(points_text, True, (0, 0, 0))
            points_rect = points_surface.get_rect(center=(panel_width//2, 100))
            panel_surface.blit(points_surface, points_rect)
        
        screen.blit(panel_surface, (panel_x, panel_y))
    
    def draw_mini_hud(self, screen, player_data, inventory_data):
        """Draw mini progression info in corner"""
        x = self.screen_width - 250
        y = 10
        
        info_lines = [
            f"Level {player_data['level']} (Bomb Lv.{player_data['bomb_level']})",
            f"Kerr Scrap: {inventory_data['resources']['kerr_scrap']}",
            f"Stat Points: {player_data['stat_points']}" if player_data['stat_points'] > 0 else ""
        ]
        
        for i, line in enumerate(info_lines):
            if line:
                color = self.colors['text_highlight'] if 'Stat Points' in line else self.colors['text']
                text_surface = self.font_small.render(line, True, color)
                screen.blit(text_surface, (x, y + i * 20))