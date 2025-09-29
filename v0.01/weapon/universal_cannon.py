#!/usr/bin/env python3
import pygame
import math
import random
from weapons_database import WeaponsDatabase

class CannonProjectile:
    """Individual cannon shot projectile"""
    
    def __init__(self, x, y, vx, vy, projectile_data, is_player_shot=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.projectile_data = projectile_data
        self.is_player_shot = is_player_shot
        self.active = True
        self.lifetime = 3.0  # 3 second lifetime
        
        # Visual properties
        self.trail_points = [(x, y)]
        self.max_trail_length = 8
        
        # Calculate damage once
        from damage_calculator import DamageCalculator
        self.damage = DamageCalculator.calculate_projectile_damage(projectile_data)
    
    def update(self, delta_time):
        """Update projectile position and lifetime"""
        if not self.active:
            return False
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Add to trail
        self.trail_points.append((self.x, self.y))
        if len(self.trail_points) > self.max_trail_length:
            self.trail_points.pop(0)
        
        # Update lifetime
        self.lifetime -= delta_time
        if self.lifetime <= 0:
            self.active = False
            return False
        
        return True
    
    def draw(self, screen):
        """Draw projectile with trail"""
        if not self.active or len(self.trail_points) < 2:
            return
        
        # Draw trail
        color = (0, 255, 255) if self.is_player_shot else (255, 100, 100)
        
        for i in range(1, len(self.trail_points)):
            alpha = int(255 * (i / len(self.trail_points)) * 0.6)
            trail_color = (*color, alpha)
            
            # Create surface for alpha trail segment
            trail_surface = pygame.Surface((abs(self.trail_points[i][0] - self.trail_points[i-1][0]) + 4, 
                                          abs(self.trail_points[i][1] - self.trail_points[i-1][1]) + 4), 
                                        pygame.SRCALPHA)
            
            pygame.draw.line(trail_surface, trail_color, 
                           (2, 2), 
                           (self.trail_points[i][0] - self.trail_points[i-1][0] + 2, 
                            self.trail_points[i][1] - self.trail_points[i-1][1] + 2), 2)
            
            screen.blit(trail_surface, (min(self.trail_points[i][0], self.trail_points[i-1][0]) - 2, 
                                      min(self.trail_points[i][1], self.trail_points[i-1][1]) - 2))
        
        # Draw main projectile
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 3)


class UniversalCannon:
    """Universal cannon system available to all ship types"""
    
    def __init__(self, ship):
        self.ship = ship
        
        # Cannon specifications - these could be upgraded
        self.cannon_level = 1
        self.cannon_rarity = "Common"
        
        # Base cannon stats (rapid fire, low damage per shot)
        self.base_damage = 15  # Low per-shot damage
        self.fire_rate = 8.0   # 8 shots per second
        self.projectile_speed = 800  # Fast projectiles
        self.spread_angle = math.pi / 48  # Small spread (3.75 degrees)
        
        # Cooldown management
        self.last_shot_time = 0
        self.shot_interval = 1.0 / self.fire_rate
        
        # Barrel configuration
        self.barrel_count = 2  # Dual cannon setup
        self.barrel_spacing = 15  # Distance between barrels
        
        # Visual effects
        self.muzzle_flash_timer = 0
        self.heat_buildup = 0  # For overheating mechanics
        self.max_heat = 100
        
    def can_fire(self, current_time):
        """Check if cannon can fire"""
        return (current_time - self.last_shot_time) >= self.shot_interval
    
    def fire(self, projectile_manager, current_time, target_angle=None):
        """Fire the universal cannon"""
        if not self.can_fire(current_time):
            return False
        
        # Calculate firing angle
        if target_angle is None:
            # Default: fire straight up
            base_angle = -math.pi / 2
        else:
            base_angle = target_angle
        
        # Create projectile data
        projectile_data = self._get_projectile_specs()
        
        # Calculate projectile velocity
        speed = self.projectile_speed
        
        # Fire from each barrel with slight spread
        shots_fired = 0
        for barrel_index in range(self.barrel_count):
            # Calculate barrel position offset
            barrel_offset_angle = math.pi / 2  # Perpendicular to firing direction
            barrel_offset_x = math.cos(barrel_offset_angle + base_angle) * (barrel_index - 0.5) * self.barrel_spacing
            barrel_offset_y = math.sin(barrel_offset_angle + base_angle) * (barrel_index - 0.5) * self.barrel_spacing
            
            # Starting position (from barrel)
            start_x = self.ship.x + barrel_offset_x
            start_y = self.ship.y + barrel_offset_y - 20  # Slightly forward of ship center
            
            # Add spread to firing angle
            spread = random.uniform(-self.spread_angle, self.spread_angle)
            shot_angle = base_angle + spread
            
            # Calculate velocity
            vx = math.cos(shot_angle) * speed
            vy = math.sin(shot_angle) * speed
            
            # Create projectile
            projectile_manager.add_kinetic_shot(
                start_x, start_y, vx, vy, 
                projectile_data, is_player_shot=True
            )
            
            shots_fired += 1
        
        # Update firing state
        self.last_shot_time = current_time
        self.muzzle_flash_timer = 0.05  # Brief muzzle flash
        self.heat_buildup += 2  # Heat per shot
        
        return True
    
    def fire_burst(self, projectile_manager, current_time, burst_count=3, target_angle=None):
        """Fire a burst of shots"""
        shots_fired = 0
        burst_interval = 0.05  # 50ms between burst shots
        
        for i in range(burst_count):
            if self.can_fire(current_time + (i * burst_interval)):
                if self.fire(projectile_manager, current_time + (i * burst_interval), target_angle):
                    shots_fired += 1
        
        return shots_fired > 0
    
    def update(self, delta_time):
        """Update cannon state"""
        # Update muzzle flash timer
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= delta_time
        
        # Cool down heat buildup
        if self.heat_buildup > 0:
            cooling_rate = 20  # Heat units per second
            self.heat_buildup = max(0, self.heat_buildup - cooling_rate * delta_time)
    
    def _get_projectile_specs(self):
        """Get current projectile specifications"""
        # Use kinetic projectile data from weapons database
        base_projectile = WeaponsDatabase.get_kinetic_projectile("armor_piercing")
        
        if not base_projectile:
            # Fallback specifications
            return {
                "mass_kg": 0.05,  # 50 grams
                "velocity_kmh": self.projectile_speed * 3.6,  # Convert m/s to km/h
                "diameter_mm": 8,
                "material": "Tungsten Core",
                "damage_type": "kinetic"
            }
        
        # Apply cannon level/rarity modifiers
        enhanced_projectile = base_projectile.copy()
        enhanced_projectile["velocity_kmh"] = self.projectile_speed * 3.6
        
        # Damage scaling based on cannon level
        damage_multiplier = 1.0 + (self.cannon_level - 1) * 0.15
        if "damage_base" not in enhanced_projectile:
            enhanced_projectile["damage_base"] = self.base_damage
        enhanced_projectile["damage_base"] *= damage_multiplier
        
        # Apply rarity effects
        rarity_multipliers = {
            "Common": 1.0,
            "Uncommon": 1.1,
            "Rare": 1.25,
            "Epic": 1.4,
            "Legendary": 1.6
        }
        
        rarity_mult = rarity_multipliers.get(self.cannon_rarity, 1.0)
        enhanced_projectile["damage_base"] *= rarity_mult
        
        return enhanced_projectile
    
    def is_overheated(self):
        """Check if cannon is overheated"""
        return self.heat_buildup >= self.max_heat
    
    def get_heat_percentage(self):
        """Get current heat as percentage"""
        return self.heat_buildup / self.max_heat
    
    def draw_muzzle_flash(self, screen, effect_manager=None):
        """Draw muzzle flash effect"""
        if self.muzzle_flash_timer <= 0:
            return
        
        if effect_manager:
            # Use effect manager for proper muzzle flash
            for barrel_index in range(self.barrel_count):
                barrel_offset_x = (barrel_index - 0.5) * self.barrel_spacing
                flash_x = self.ship.x + barrel_offset_x
                flash_y = self.ship.y - 20
                
                effect_manager.add_muzzle_flash(
                    flash_x, flash_y, 
                    angle=-math.pi/2, 
                    size=0.6
                )
        else:
            # Simple fallback muzzle flash
            flash_alpha = int(255 * (self.muzzle_flash_timer / 0.05))
            flash_color = (255, 255, 150, flash_alpha)
            
            for barrel_index in range(self.barrel_count):
                barrel_offset_x = (barrel_index - 0.5) * self.barrel_spacing
                flash_x = int(self.ship.x + barrel_offset_x)
                flash_y = int(self.ship.y - 25)
                
                # Simple flash rectangle
                flash_surface = pygame.Surface((8, 15), pygame.SRCALPHA)
                pygame.draw.rect(flash_surface, flash_color, (0, 0, 8, 15))
                screen.blit(flash_surface, (flash_x - 4, flash_y - 7))
    
    def upgrade_cannon(self, new_level=None, new_rarity=None):
        """Upgrade cannon level or rarity"""
        if new_level is not None:
            self.cannon_level = max(1, min(13, new_level))
        
        if new_rarity is not None and new_rarity in ["Common", "Uncommon", "Rare", "Epic", "Legendary"]:
            self.cannon_rarity = new_rarity
        
        # Recalculate stats based on new level/rarity
        self._recalculate_stats()
    
    def _recalculate_stats(self):
        """Recalculate cannon stats after upgrade"""
        # Base stats scale with level
        level_multiplier = 1.0 + (self.cannon_level - 1) * 0.1
        
        self.base_damage = int(15 * level_multiplier)
        self.projectile_speed = int(800 * (1.0 + (self.cannon_level - 1) * 0.05))
        
        # Fire rate increases slightly with level
        self.fire_rate = 8.0 + (self.cannon_level - 1) * 0.2
        self.shot_interval = 1.0 / self.fire_rate
        
        # Higher levels have better accuracy
        base_spread = math.pi / 48
        accuracy_improvement = (self.cannon_level - 1) * 0.1
        self.spread_angle = base_spread * (1.0 - accuracy_improvement)
    
    def get_cannon_info(self):
        """Get cannon statistics for UI display"""
        return {
            "level": self.cannon_level,
            "rarity": self.cannon_rarity,
            "damage_per_shot": self.base_damage,
            "fire_rate": self.fire_rate,
            "projectile_speed": self.projectile_speed,
            "heat_percentage": self.get_heat_percentage(),
            "overheated": self.is_overheated(),
            "accuracy": 1.0 - (self.spread_angle / (math.pi / 48))
        }


class CannonManager:
    """Manages cannon projectiles separately from other projectiles"""
    
    def __init__(self):
        self.cannon_shots = []
        self.shots_fired_this_second = 0
        self.last_second_timer = 0
    
    def add_cannon_shot(self, x, y, vx, vy, projectile_data, is_player_shot=True):
        """Add a cannon projectile"""
        shot = CannonProjectile(x, y, vx, vy, projectile_data, is_player_shot)
        self.cannon_shots.append(shot)
        
        if is_player_shot:
            self.shots_fired_this_second += 1
        
        return shot
    
    def update(self, delta_time, enemies, player_ship, screen_width, screen_height):
        """Update all cannon projectiles and handle collisions"""
        # Update shot counter
        self.last_second_timer += delta_time
        if self.last_second_timer >= 1.0:
            self.shots_fired_this_second = 0
            self.last_second_timer = 0
        
        # Update projectiles
        for shot in self.cannon_shots[:]:
            if not shot.update(delta_time):
                self.cannon_shots.remove(shot)
                continue
            
            # Check screen boundaries
            if (shot.x < -50 or shot.x > screen_width + 50 or 
                shot.y < -50 or shot.y > screen_height + 50):
                shot.active = False
                self.cannon_shots.remove(shot)
                continue
            
            # Check collisions
            self._check_shot_collisions(shot, enemies, player_ship)
    
    def _check_shot_collisions(self, shot, enemies, player_ship):
        """Check cannon shot collisions with targets"""
        if not shot.active:
            return
        
        collision_radius = 8  # Cannon shots are small
        
        if shot.is_player_shot:
            # Player shots vs enemies
            for enemy in enemies[:]:
                if not hasattr(enemy, 'x') or not hasattr(enemy, 'y') or not enemy.active:
                    continue
                
                distance = math.hypot(shot.x - enemy.x, shot.y - enemy.y)
                if distance < collision_radius + enemy.radius:
                    # Hit enemy
                    was_killed = enemy.take_damage(shot.damage, "kinetic")
                    shot.active = False
                    
                    # Remove shot from list
                    if shot in self.cannon_shots:
                        self.cannon_shots.remove(shot)
                    
                    return True
        else:
            # Enemy shots vs player
            if player_ship and hasattr(player_ship, 'x'):
                distance = math.hypot(shot.x - player_ship.x, shot.y - player_ship.y)
                player_radius = getattr(player_ship, 'collision_radius', 20)
                
                if distance < collision_radius + player_radius:
                    # Hit player
                    player_ship.take_damage(shot.damage, "kinetic")
                    shot.active = False
                    
                    if shot in self.cannon_shots:
                        self.cannon_shots.remove(shot)
                    
                    return True
        
        return False
    
    def draw(self, screen):
        """Draw all cannon projectiles"""
        for shot in self.cannon_shots:
            if shot.active:
                shot.draw(screen)
    
    def get_active_shot_count(self):
        """Get number of active cannon shots"""
        return len([shot for shot in self.cannon_shots if shot.active])
    
    def get_shots_per_second(self):
        """Get current shots per second rate"""
        return self.shots_fired_this_second
    
    def clear_all_shots(self):
        """Clear all cannon shots"""
        self.cannon_shots.clear()
        self.shots_fired_this_second = 0


# Integration functions for existing ship classes
def add_universal_cannon_to_ship(ship_class):
    """Add universal cannon capability to any ship class"""
    
    def __init_cannon__(self, *args, **kwargs):
        # Call original init
        self.__original_init__(*args, **kwargs)
        
        # Add cannon system
        self.universal_cannon = UniversalCannon(self)
    
    def fire_universal_cannon(self, projectile_manager, target_angle=None):
        """Fire the universal cannon"""
        current_time = pygame.time.get_ticks() / 1000.0  # Convert to seconds
        return self.universal_cannon.fire(projectile_manager, current_time, target_angle)
    
    def fire_cannon_burst(self, projectile_manager, burst_count=3, target_angle=None):
        """Fire a cannon burst"""
        current_time = pygame.time.get_ticks() / 1000.0
        return self.universal_cannon.fire_burst(projectile_manager, current_time, burst_count, target_angle)
    
    def update_cannon(self, delta_time):
        """Update cannon state (call this in ship's update method)"""
        if hasattr(self, 'universal_cannon'):
            self.universal_cannon.update(delta_time)
    
    def draw_cannon_effects(self, screen, effect_manager=None):
        """Draw cannon muzzle flashes"""
        if hasattr(self, 'universal_cannon'):
            self.universal_cannon.draw_muzzle_flash(screen, effect_manager)
    
    def get_cannon_info(self):
        """Get cannon information"""
        if hasattr(self, 'universal_cannon'):
            return self.universal_cannon.get_cannon_info()
        return None
    
    def upgrade_cannon(self, level=None, rarity=None):
        """Upgrade cannon"""
        if hasattr(self, 'universal_cannon'):
            self.universal_cannon.upgrade_cannon(level, rarity)
    
    # Store original init and replace
    ship_class.__original_init__ = ship_class.__init__
    ship_class.__init__ = __init_cannon__
    
    # Add methods to class
    ship_class.fire_universal_cannon = fire_universal_cannon
    ship_class.fire_cannon_burst = fire_cannon_burst
    ship_class.update_cannon = update_cannon
    ship_class.draw_cannon_effects = draw_cannon_effects
    ship_class.get_cannon_info = get_cannon_info
    ship_class.upgrade_cannon = upgrade_cannon
    
    return ship_class