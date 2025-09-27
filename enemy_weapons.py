#!/usr/bin/env python3
import pygame
import math
import random
from weapons_database import WeaponsDatabase

class EnemyWeapon:
    """Base class for enemy weapons"""
    
    def __init__(self, weapon_type, fire_rate, damage, projectile_speed, accuracy=0.8):
        self.weapon_type = weapon_type
        self.fire_rate = fire_rate  # Shots per second
        self.damage = damage
        self.projectile_speed = projectile_speed
        self.accuracy = accuracy  # 0.0 to 1.0
        
        # Firing state
        self.last_shot_time = 0
        self.shot_interval = 1.0 / fire_rate
        self.ammo = -1  # Unlimited by default
        
        # Targeting
        self.max_range = 600
        self.lead_target = True
    
    def can_fire(self, current_time):
        """Check if weapon can fire"""
        return ((current_time - self.last_shot_time) >= self.shot_interval and 
                (self.ammo != 0))
    
    def fire(self, shooter_pos, target_pos, target_velocity, projectile_manager, current_time):
        """Fire at target"""
        if not self.can_fire(current_time):
            return False
        
        # Calculate firing angle
        firing_angle = self._calculate_firing_angle(shooter_pos, target_pos, target_velocity)
        if firing_angle is None:
            return False
        
        # Apply accuracy
        accuracy_spread = math.pi / 12 * (1.0 - self.accuracy)  # 15 degrees max spread
        firing_angle += random.uniform(-accuracy_spread, accuracy_spread)
        
        # Create projectile
        success = self._create_projectile(shooter_pos, firing_angle, projectile_manager)
        
        if success:
            self.last_shot_time = current_time
            if self.ammo > 0:
                self.ammo -= 1
        
        return success
    
    def _calculate_firing_angle(self, shooter_pos, target_pos, target_velocity):
        """Calculate angle to hit moving target"""
        dx = target_pos[0] - shooter_pos[0]
        dy = target_pos[1] - shooter_pos[1]
        distance = math.hypot(dx, dy)
        
        # Check range
        if distance > self.max_range:
            return None
        
        if self.lead_target and target_velocity:
            # Lead target calculation
            time_to_impact = distance / self.projectile_speed
            predicted_x = target_pos[0] + target_velocity[0] * time_to_impact
            predicted_y = target_pos[1] + target_velocity[1] * time_to_impact
            
            # Recalculate angle to predicted position
            dx = predicted_x - shooter_pos[0]
            dy = predicted_y - shooter_pos[1]
        
        return math.atan2(dy, dx)
    
    def _create_projectile(self, shooter_pos, angle, projectile_manager):
        """Create projectile (override in subclasses)"""
        vx = math.cos(angle) * self.projectile_speed
        vy = math.sin(angle) * self.projectile_speed
        
        # Basic projectile data
        projectile_data = {
            'mass_kg': 0.01,
            'velocity_kmh': self.projectile_speed * 3.6,
            'damage_base': self.damage,
            'projectile_type': self.weapon_type
        }
        
        return projectile_manager.add_kinetic_shot(
            shooter_pos[0], shooter_pos[1], vx, vy, 
            projectile_data, is_player_shot=False
        )


class EnemyBlaster(EnemyWeapon):
    """Basic enemy energy weapon"""
    
    def __init__(self, level=1):
        damage = 8 + (level * 2)
        fire_rate = 2.0 + (level * 0.3)
        speed = 200 + (level * 20)
        accuracy = 0.7 + (level * 0.05)
        
        super().__init__("blaster", fire_rate, damage, speed, accuracy)
        self.color = (255, 100, 100)  # Red energy bolts


class EnemyCannon(EnemyWeapon):
    """Enemy kinetic weapon"""
    
    def __init__(self, level=1):
        damage = 12 + (level * 3)
        fire_rate = 1.5 + (level * 0.2)
        speed = 300 + (level * 30)
        accuracy = 0.8 + (level * 0.03)
        
        super().__init__("cannon", fire_rate, damage, speed, accuracy)
        self.color = (200, 200, 100)  # Yellow projectiles


class EnemyMissileLauncher(EnemyWeapon):
    """Enemy missile system"""
    
    def __init__(self, level=1):
        damage = 25 + (level * 5)
        fire_rate = 0.5 + (level * 0.1)  # Slower fire rate
        speed = 150 + (level * 15)  # Slower but homing
        accuracy = 0.9  # High accuracy due to homing
        
        super().__init__("missile", fire_rate, damage, speed, accuracy)
        self.ammo = 6 + level  # Limited ammo
        self.color = (255, 255, 100)  # Bright yellow missiles
    
    def _create_projectile(self, shooter_pos, angle, projectile_manager):
        """Create homing missile"""
        vx = math.cos(angle) * self.projectile_speed
        vy = math.sin(angle) * self.projectile_speed
        
        # Missile projectile data with homing capability
        projectile_data = {
            'mass_kg': 0.5,
            'velocity_kmh': self.projectile_speed * 3.6,
            'damage_base': self.damage,
            'projectile_type': 'homing_missile',
            'homing': True,
            'turn_rate': 2.0  # Radians per second
        }
        
        # For now, create as kinetic shot (would need missile-specific projectile)
        return projectile_manager.add_kinetic_shot(
            shooter_pos[0], shooter_pos[1], vx, vy, 
            projectile_data, is_player_shot=False
        )


class EnemyWeaponSystem:
    """Weapon system for individual enemies"""
    
    def __init__(self, enemy_type, level=1):
        self.enemy_type = enemy_type
        self.level = level
        self.weapons = []
        
        # Equip weapons based on enemy type
        self._equip_weapons()
        
        # Firing behavior
        self.target_player = None
        self.firing_range = 400
        self.aggressive = True
        self.burst_fire = False
        self.burst_count = 0
        self.max_burst = 3
    
    def _equip_weapons(self):
        """Equip weapons based on enemy type and level"""
        if self.enemy_type == "fighter":
            # Basic fighter: blaster + optional cannon at higher levels
            self.weapons.append(EnemyBlaster(self.level))
            if self.level >= 3:
                self.weapons.append(EnemyCannon(self.level - 1))
        
        elif self.enemy_type == "bomber":
            # Bomber: missiles + defensive blaster
            self.weapons.append(EnemyMissileLauncher(self.level))
            self.weapons.append(EnemyBlaster(max(1, self.level - 1)))
            self.firing_range = 500  # Longer range
        
        elif self.enemy_type == "scout":
            # Scout: rapid-fire blaster, hit and run
            rapid_blaster = EnemyBlaster(self.level)
            rapid_blaster.fire_rate *= 1.5  # Faster firing
            rapid_blaster.damage *= 0.8  # Less damage per shot
            self.weapons.append(rapid_blaster)
            self.burst_fire = True
            self.firing_range = 300  # Shorter range, more aggressive
    
    def update(self, delta_time, owner_position, player_ship, projectile_manager):
        """Update weapon system and handle firing"""
        if not player_ship or not self.aggressive:
            return
        
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check if player is in range
        distance_to_player = math.hypot(
            player_ship.x - owner_position[0],
            player_ship.y - owner_position[1]
        )
        
        if distance_to_player > self.firing_range:
            return
        
        # Get player velocity for lead targeting
        player_velocity = (0, 0)  # Would get from player ship if available
        if hasattr(player_ship, 'vx') and hasattr(player_ship, 'vy'):
            player_velocity = (player_ship.vx, player_ship.vy)
        
        # Fire weapons
        if self.burst_fire:
            self._handle_burst_fire(owner_position, (player_ship.x, player_ship.y), 
                                  player_velocity, projectile_manager, current_time)
        else:
            self._handle_normal_fire(owner_position, (player_ship.x, player_ship.y), 
                                   player_velocity, projectile_manager, current_time)
    
    def _handle_normal_fire(self, owner_pos, target_pos, target_vel, projectile_manager, current_time):
        """Handle normal firing pattern"""
        for weapon in self.weapons:
            # Random chance to fire (prevents all weapons firing at once)
            if random.random() < 0.3:  # 30% chance per weapon per update
                weapon.fire(owner_pos, target_pos, target_vel, projectile_manager, current_time)
    
    def _handle_burst_fire(self, owner_pos, target_pos, target_vel, projectile_manager, current_time):
        """Handle burst firing pattern"""
        if self.burst_count <= 0:
            # Start new burst
            self.burst_count = self.max_burst
        
        if self.burst_count > 0:
            # Fire primary weapon
            if self.weapons:
                if self.weapons[0].fire(owner_pos, target_pos, target_vel, projectile_manager, current_time):
                    self.burst_count -= 1
    
    def set_aggressive(self, aggressive):
        """Set firing behavior"""
        self.aggressive = aggressive
    
    def get_weapon_info(self):
        """Get weapon information for debugging"""
        return {
            'weapon_count': len(self.weapons),
            'weapon_types': [w.weapon_type for w in self.weapons],
            'aggressive': self.aggressive,
            'burst_fire': self.burst_fire,
            'firing_range': self.firing_range
        }


# Integration functions for existing enemy system
def add_weapons_to_basic_enemy(enemy_class):
    """Add weapon system to BasicEnemy class"""
    
    def __init_weapons__(self, *args, **kwargs):
        # Call original init
        self.__original_init__(*args, **kwargs)
        
        # Add weapon system
        self.weapon_system = EnemyWeaponSystem(self.enemy_type, self.level)
        
        # Adjust firing behavior based on enemy type
        if self.enemy_type == "bomber":
            self.shoot_interval *= 1.5  # Bombers fire less frequently
        elif self.enemy_type == "scout":
            self.shoot_interval *= 0.7  # Scouts fire more frequently
    
    def update_weapons(self, delta_time, player_ship, projectile_manager):
        """Update weapon system (call this in enemy's update method)"""
        if hasattr(self, 'weapon_system'):
            self.weapon_system.update(delta_time, (self.x, self.y), player_ship, projectile_manager)
    
    def get_weapon_info(self):
        """Get weapon system info"""
        if hasattr(self, 'weapon_system'):
            return self.weapon_system.get_weapon_info()
        return None
    
    def set_aggressive(self, aggressive):
        """Set enemy aggression"""
        if hasattr(self, 'weapon_system'):
            self.weapon_system.set_aggressive(aggressive)
    
    # Store original init and replace
    enemy_class.__original_init__ = enemy_class.__init__
    enemy_class.__init__ = __init_weapons__
    
    # Add methods to class
    enemy_class.update_weapons = update_weapons
    enemy_class.get_weapon_info = get_weapon_info
    enemy_class.set_aggressive = set_aggressive
    
    return enemy_class


class EnemyFormation:
    """Coordinated enemy formation with synchronized attacks"""
    
    def __init__(self, formation_type, enemy_list, level=1):
        self.formation_type = formation_type
        self.enemies = enemy_list
        self.level = level
        
        # Formation behavior
        self.formation_leader = enemy_list[0] if enemy_list else None
        self.attack_pattern = "synchronized"
        self.last_formation_attack = 0
        self.formation_attack_interval = 3.0  # Seconds between coordinated attacks
        
        # Apply formation bonuses
        self._apply_formation_bonuses()
    
    def _apply_formation_bonuses(self):
        """Apply bonuses for fighting in formation"""
        if self.formation_type == "wing":
            # Wing formation: increased accuracy
            for enemy in self.enemies:
                if hasattr(enemy, 'weapon_system'):
                    for weapon in enemy.weapon_system.weapons:
                        weapon.accuracy *= 1.2
        
        elif self.formation_type == "line":
            # Line formation: increased damage
            for enemy in self.enemies:
                if hasattr(enemy, 'weapon_system'):
                    for weapon in enemy.weapon_system.weapons:
                        weapon.damage *= 1.15
        
        elif self.formation_type == "swarm":
            # Swarm: increased fire rate
            for enemy in self.enemies:
                if hasattr(enemy, 'weapon_system'):
                    for weapon in enemy.weapon_system.weapons:
                        weapon.fire_rate *= 1.3
    
    def update_formation(self, delta_time, player_ship, projectile_manager):
        """Update formation behavior"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Check for coordinated attack
        if (current_time - self.last_formation_attack) >= self.formation_attack_interval:
            if self.attack_pattern == "synchronized" and len(self.enemies) > 1:
                self._execute_synchronized_attack(player_ship, projectile_manager, current_time)
    
    def _execute_synchronized_attack(self, player_ship, projectile_manager, current_time):
        """Execute coordinated attack pattern"""
        if not player_ship:
            return
        
        # All enemies fire at once
        for enemy in self.enemies:
            if hasattr(enemy, 'weapon_system') and enemy.active:
                # Force fire regardless of normal timing
                for weapon in enemy.weapon_system.weapons:
                    weapon.fire((enemy.x, enemy.y), (player_ship.x, player_ship.y), 
                              (0, 0), projectile_manager, current_time)
        
        self.last_formation_attack = current_time
    
    def remove_enemy(self, enemy):
        """Remove enemy from formation"""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
            
            # Reassign leader if needed
            if enemy == self.formation_leader and self.enemies:
                self.formation_leader = self.enemies[0]
    
    def is_formation_intact(self):
        """Check if formation still has active members"""
        active_count = sum(1 for enemy in self.enemies if enemy.active)
        return active_count > 1


class EnemyWeaponManager:
    """Manages all enemy weapon systems and coordinated attacks"""
    
    def __init__(self):
        self.formations = []
        self.weapon_stats = {
            'shots_fired': 0,
            'hits_scored': 0,
            'damage_dealt': 0
        }
        
        print("EnemyWeaponManager initialized")
    
    def create_formation(self, formation_type, enemy_list, level=1):
        """Create enemy formation"""
        if len(enemy_list) > 1:
            formation = EnemyFormation(formation_type, enemy_list, level)
            self.formations.append(formation)
            return formation
        return None
    
    def update_all_formations(self, delta_time, player_ship, projectile_manager):
        """Update all enemy formations"""
        for formation in self.formations[:]:
            if formation.is_formation_intact():
                formation.update_formation(delta_time, player_ship, projectile_manager)
            else:
                self.formations.remove(formation)
    
    def on_enemy_death(self, enemy):
        """Handle enemy death - remove from formations"""
        for formation in self.formations:
            formation.remove_enemy(enemy)
    
    def on_projectile_fired(self):
        """Track enemy projectile fired"""
        self.weapon_stats['shots_fired'] += 1
    
    def on_player_hit(self, damage):
        """Track successful hit on player"""
        self.weapon_stats['hits_scored'] += 1
        self.weapon_stats['damage_dealt'] += damage
    
    def get_accuracy(self):
        """Get overall enemy accuracy"""
        if self.weapon_stats['shots_fired'] > 0:
            return self.weapon_stats['hits_scored'] / self.weapon_stats['shots_fired']
        return 0.0
    
    def get_stats(self):
        """Get weapon statistics"""
        return self.weapon_stats.copy()
    
    def clear_stats(self):
        """Clear weapon statistics"""
        self.weapon_stats = {
            'shots_fired': 0,
            'hits_scored': 0,
            'damage_dealt': 0
        }


# Factory functions for creating armed enemies
def create_armed_fighter(x, y, level=1):
    """Create a fighter with appropriate weapons"""
    from enemy_manager import BasicEnemy  # Import here to avoid circular import
    
    # Create basic enemy and add weapons
    enemy = BasicEnemy(x, y, "fighter", level)
    add_weapons_to_basic_enemy(type(enemy))
    enemy.__init__(x, y, "fighter", level)  # Reinitialize with weapons
    
    return enemy

def create_armed_bomber(x, y, level=1):
    """Create a bomber with missile systems"""
    from enemy_manager import BasicEnemy
    
    enemy = BasicEnemy(x, y, "bomber", level)
    add_weapons_to_basic_enemy(type(enemy))
    enemy.__init__(x, y, "bomber", level)
    
    # Bombers are less maneuverable but more dangerous
    enemy.max_speed *= 0.8
    enemy.max_hp *= 1.3
    
    return enemy

def create_armed_scout(x, y, level=1):
    """Create a fast scout with rapid-fire weapons"""
    from enemy_manager import BasicEnemy
    
    enemy = BasicEnemy(x, y, "scout", level)
    add_weapons_to_basic_enemy(type(enemy))
    enemy.__init__(x, y, "scout", level)
    
    # Scouts are faster but more fragile
    enemy.max_speed *= 1.4
    enemy.max_hp *= 0.7
    
    return enemy