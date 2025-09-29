#!/usr/bin/env python3
import pygame
import math
import random
from ship_base import ShipBase
from weapons_database import WeaponsDatabase

class BreacherShip(ShipBase):
    """Explosive specialist ship with stat-based progression"""
    
    def __init__(self, screen_width, screen_height):
        super().__init__(screen_width, screen_height)
        
        # Ship identification
        self.ship_type = "Breacher"
        
        # Enhanced physics with reasonable drag for space
        self.max_thrust = 150000.0 * (self.base_size / 13)
        self.mass = 800.0 * (self.base_size / 13)
        self.max_velocity = 400 * (self.base_size / 13)
        self.drag_coefficient = 0.3  # Light drag for better control
        
        # Base stats (before player stat modifications)
        self.base_hp = 80
        self.base_shield = 120
        self.base_explosive_damage = 1.0
        
        # Current stat modifiers (applied by progression system)
        self.stat_modifiers = {
            'explosive_bonus_kg': 0,
            'damage_resistance': 0,
            'dodge_chance': 0,
            'shield_capacity_bonus': 0,
            'shield_regen_bonus': 0,
            'explosive_damage_mult': 1.0,
            'cooldown_mult': 1.0,
            'shield_capacity_mult': 1.0
        }
        
        # Weapon systems this ship can use
        self.weapon_systems = ["bombs", "cannons"]
        
        # Equipment compatibility
        self.compatible_equipment = ["cannons", "bombs", "fuselages", "engines"]
        
        # Special abilities unique to Breacher
        self.special_abilities = ["breach_bomb", "cluster_strike", "overcharge_warheads"]
        
        # Breacher-specific equipment (now stat-based)
        self.equipped_bomb = {"level": 1, "rarity": "Common"}
        
        # Special ability tracking
        self.breach_bomb_uses = 0
        self.overcharge_active = False
        self.overcharge_timer = 0
        
        # Shield regeneration
        self.shield_regen_timer = 0
        self.shield_regen_delay = 3.0  # 3 seconds before regen starts
        
        # Recalculate stats with ship-specific modifiers
        self._recalculate_stats()
        
        print(f"Breacher: T={self.max_thrust:.0f}N, M={self.mass:.0f}kg, T/W={self.max_thrust/self.mass:.1f}")
    
    def apply_stat_modifiers(self, modifiers):
        """Apply stat modifiers from progression system"""
        self.stat_modifiers.update(modifiers)
        self._recalculate_stats()
    
    def _recalculate_stats(self):
        """Recalculate all stats based on modifiers"""
        # Apply shield bonuses
        shield_bonus = self.stat_modifiers.get('shield_capacity_bonus', 0)
        shield_mult = self.stat_modifiers.get('shield_capacity_mult', 1.0)
        self.max_shield = int((self.base_shield + shield_bonus) * shield_mult)
        
        # Ensure current values don't exceed new maximums
        self.current_shield = min(self.current_shield, self.max_shield)
        self.current_hp = min(self.current_hp, self.max_hp)
    
    def update(self, delta_time, keys_pressed):
        """Update Breacher ship with stat-based systems"""
        # Call parent update for physics
        super().update(delta_time, keys_pressed)
        
        # Update overcharge timer
        if self.overcharge_active:
            self.overcharge_timer -= delta_time
            if self.overcharge_timer <= 0:
                self.overcharge_active = False
                self.overcharge_timer = 0
        
        # Handle shield regeneration
        self._update_shield_regen(delta_time)
    
    def _update_shield_regen(self, delta_time):
        """Update shield regeneration based on stats"""
        if self.current_shield < self.max_shield:
            self.shield_regen_timer += delta_time
            
            if self.shield_regen_timer >= self.shield_regen_delay:
                base_regen = 5.0  # 5 J/s base regen
                stat_regen = self.stat_modifiers.get('shield_regen_bonus', 0)
                total_regen = (base_regen + stat_regen) * delta_time
                
                self.current_shield = min(self.max_shield, self.current_shield + total_regen)
    
    def take_damage(self, damage_joules, damage_type="generic"):
        """Apply damage with evasion and damage resistance"""
        # Check for evasion
        dodge_chance = self.stat_modifiers.get('dodge_chance', 0)
        if random.random() < dodge_chance:
            print(f"Evaded {damage_joules:.0f}J damage!")
            return False  # Damage evaded
        
        # Apply damage resistance
        resistance = self.stat_modifiers.get('damage_resistance', 0)
        actual_damage = damage_joules * (1.0 - resistance)
        
        # Reset shield regen timer when taking damage
        self.shield_regen_timer = 0
        
        # Call parent damage method with modified damage
        return super().take_damage(actual_damage, damage_type)
    
    def fire_special_weapon(self, ability_name, projectile_manager):
        """Fire Breacher-specific special weapons with stat bonuses"""
        if ability_name == "breach_bomb":
            return self._fire_breach_bomb(projectile_manager)
        elif ability_name == "cluster_strike":
            return self._fire_cluster_strike(projectile_manager)
        elif ability_name == "overcharge_warheads":
            return self._activate_overcharge()
        
        return False
    
    def _fire_breach_bomb(self, projectile_manager):
        """Fire breach bomb with stat-based explosive bonuses"""
        if "breach_bomb" in self.cooldowns:
            return False
        
        # Get base bomb specifications
        bomb_stats = WeaponsDatabase.get_standard_bomb(
            level=self.equipped_bomb["level"],
            rarity=self.equipped_bomb["rarity"]
        )
        
        if not bomb_stats:
            return False
        
        # Apply stat-based modifications
        enhanced_bomb_stats = self._apply_stat_bonuses_to_bomb(bomb_stats)
        
        # 5-bomb spread pattern
        angles = [
            -math.pi / 2,
            -math.pi / 2 - math.pi / 12,
            -math.pi / 2 - math.pi / 24,
            -math.pi / 2 + math.pi / 24,
            -math.pi / 2 + math.pi / 12
        ]
        
        velocity_ms = enhanced_bomb_stats["velocity_kmh"] * 1000 / 3600
        group_id = self._generate_group_id()
        
        for angle in angles:
            vx = math.cos(angle) * velocity_ms
            vy = math.sin(angle) * velocity_ms
            
            projectile_manager.add_bomb(
                self.x, self.y - 25,
                vx, vy,
                enhanced_bomb_stats,
                group_id
            )
        
        # Track usage and set cooldown with stat modifier
        self.breach_bomb_uses += 1
        base_cooldown = 4.0  # From constants
        cooldown_mult = self.stat_modifiers.get('cooldown_mult', 1.0)
        final_cooldown = base_cooldown * cooldown_mult
        self.cooldowns["breach_bomb"] = final_cooldown
        
        return True
    
    def _fire_cluster_strike(self, projectile_manager):
        """Fire cluster bombs with stat bonuses"""
        if "cluster_strike" in self.cooldowns:
            return False
        
        bomb_stats = WeaponsDatabase.get_standard_bomb(
            level=self.equipped_bomb["level"],
            rarity=self.equipped_bomb["rarity"]
        )
        
        if not bomb_stats:
            return False
        
        # Apply stat bonuses to cluster bombs
        cluster_stats = self._apply_stat_bonuses_to_bomb(bomb_stats)
        cluster_stats["min_damage"] = int(cluster_stats["min_damage"] * 0.75)
        cluster_stats["max_damage"] = int(cluster_stats["max_damage"] * 0.75)
        cluster_stats["velocity_kmh"] = int(cluster_stats["velocity_kmh"] * 1.2)
        
        velocity_ms = cluster_stats["velocity_kmh"] * 1000 / 3600
        group_id = self._generate_group_id()
        
        # 7 bombs in line formation
        for i in range(-3, 4):
            offset_x = i * 40
            vx = 0
            vy = -velocity_ms * 1.2
            
            projectile_manager.add_bomb(
                self.x + offset_x, self.y - 25,
                vx, vy,
                cluster_stats,
                group_id
            )
        
        # Apply cooldown modifier
        base_cooldown = 3.0
        cooldown_mult = self.stat_modifiers.get('cooldown_mult', 1.0)
        self.cooldowns["cluster_strike"] = base_cooldown * cooldown_mult
        
        return True
    
    def _apply_stat_bonuses_to_bomb(self, base_bomb_stats):
        """Apply player stat bonuses to bomb stats"""
        enhanced_stats = base_bomb_stats.copy()
        
        # Apply explosive bonus from attack stat
        explosive_bonus = self.stat_modifiers.get('explosive_bonus_kg', 0)
        if explosive_bonus > 0:
            # Increase shrapnel mass (represents more explosive payload)
            enhanced_stats["shrapnel_kg"] += explosive_bonus
            
            # Scale damage based on increased payload
            damage_increase = 1.0 + (explosive_bonus / enhanced_stats["shrapnel_kg"])
            enhanced_stats["min_damage"] = int(enhanced_stats["min_damage"] * damage_increase)
            enhanced_stats["max_damage"] = int(enhanced_stats["max_damage"] * damage_increase)
        
        # Apply explosive damage multiplier from perks
        explosive_mult = self.stat_modifiers.get('explosive_damage_mult', 1.0)
        enhanced_stats["min_damage"] = int(enhanced_stats["min_damage"] * explosive_mult)
        enhanced_stats["max_damage"] = int(enhanced_stats["max_damage"] * explosive_mult)
        
        # Apply overcharge if active
        if self.overcharge_active:
            enhanced_stats["min_damage"] = int(enhanced_stats["min_damage"] * 1.5)
            enhanced_stats["max_damage"] = int(enhanced_stats["max_damage"] * 1.5)
        
        return enhanced_stats
    
    def _activate_overcharge(self):
        """Activate overcharged warheads"""
        if "overcharge_warheads" in self.cooldowns or self.overcharge_active:
            return False
        
        self.overcharge_active = True
        self.overcharge_timer = 5.0
        
        # Apply cooldown modifier
        base_cooldown = 15.0
        cooldown_mult = self.stat_modifiers.get('cooldown_mult', 1.0)
        self.cooldowns["overcharge_warheads"] = base_cooldown * cooldown_mult
        
        return True
    
    def get_weapon_systems(self):
        """Return weapon systems available to Breacher"""
        return self.weapon_systems.copy()
    
    def get_special_abilities(self):
        """Return special abilities unique to Breacher"""
        return self.special_abilities.copy()
    
    def _get_ship_color(self):
        """Breacher ships are orange/red to represent explosives"""
        if self.overcharge_active:
            # Pulsing bright orange when overcharged
            pulse = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
            return (255, pulse, 0)
        else:
            return (255, 165, 0)
    
    def _draw_ship_specifics(self, screen):
        """Draw Breacher-specific visual elements"""
        # Draw explosive charge indicators
        for i in range(6):
            angle = (i / 6) * 2 * math.pi
            charge_x = self.x + math.cos(angle) * 15
            charge_y = self.y + math.sin(angle) * 15
            
            # Color based on charge state
            if self.overcharge_active:
                charge_color = (255, 255, 0)
            else:
                charge_color = (255, 100, 100)
            
            pygame.draw.circle(screen, charge_color, (int(charge_x), int(charge_y)), 3)
        
        # Draw overcharge effect
        if self.overcharge_active:
            ring_radius = int(30 + 10 * math.sin(pygame.time.get_ticks() * 0.02))
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), ring_radius, 2)
        
        # Draw stat bonus indicators
        self._draw_stat_indicators(screen)
    
    def _draw_stat_indicators(self, screen):
        """Draw visual indicators for active stat bonuses"""
        y_offset = -35
        
        # Attack bonus indicator
        if self.stat_modifiers.get('explosive_bonus_kg', 0) > 0:
            font = pygame.font.Font(None, 16)
            text = f"+{self.stat_modifiers['explosive_bonus_kg']:.1f}kg"
            surface = font.render(text, True, (255, 100, 100))
            screen.blit(surface, (self.x - 20, self.y + y_offset))
            y_offset -= 15
        
        # Defense bonus indicator
        if self.stat_modifiers.get('damage_resistance', 0) > 0:
            font = pygame.font.Font(None, 16)
            resistance_pct = self.stat_modifiers['damage_resistance'] * 100
            text = f"{resistance_pct:.0f}% DEF"
            surface = font.render(text, True, (100, 100, 255))
            screen.blit(surface, (self.x - 25, self.y + y_offset))
    
    def _generate_group_id(self):
        """Generate unique ID for projectile groups"""
        return f"breacher_{random.randint(1000, 9999)}"
    
    def get_stat_summary(self):
        """Get current stat summary for UI"""
        return {
            'hp': f"{self.current_hp:.0f}/{self.max_hp:.0f}",
            'shield': f"{self.current_shield:.0f}/{self.max_shield:.0f}",
            'explosive_bonus': f"+{self.stat_modifiers.get('explosive_bonus_kg', 0):.1f}kg",
            'damage_resistance': f"{self.stat_modifiers.get('damage_resistance', 0)*100:.1f}%",
            'dodge_chance': f"{self.stat_modifiers.get('dodge_chance', 0)*100:.1f}%",
            'shield_regen': f"{self.stat_modifiers.get('shield_regen_bonus', 0):.0f} J/s",
            'overcharge_active': self.overcharge_active,
            'overcharge_timer': self.overcharge_timer
        }