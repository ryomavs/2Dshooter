#!/usr/bin/env python3
import pygame
import math
import random

class ShipBase:
    """Ship base with realistic inertia physics and 0.6% screen scaling"""
    
    def __init__(self, screen_width, screen_height):
        # Screen boundaries
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate 0.6% scale factor for all elements
        self.scale_factor = 0.006
        self.base_size = min(screen_width, screen_height) * self.scale_factor
        
        # Position and movement with inertia
        self.x = screen_width // 2
        self.y = screen_height - 150
        self.vx = 0.0  # Current velocity
        self.vy = 0.0
        self.ax = 0.0  # Current acceleration
        self.ay = 0.0
        
        # Physics properties - scaled to screen size
        self.mass = 800.0 * (self.base_size / 13)  # Reduced mass for better responsiveness
        self.max_thrust = 150000.0 * (self.base_size / 13)  # Increased thrust
        self.drag_coefficient = 0.3  # Light drag for space combat feel
        self.max_velocity = 400 * (self.base_size / 13)  # Higher max velocity
        
        # Realistic stats in joules (scaled for balance)
        hp_scale = (self.base_size / 13) ** 1.5
        self.max_hp = int(25000 * hp_scale)
        self.current_hp = self.max_hp
        self.max_shield = int(15000 * hp_scale) 
        self.current_shield = self.max_shield
        
        # Visual properties - all scaled to 0.6% of screen
        self.radius = max(8, int(self.base_size))
        self.collision_radius = self.radius  # Add collision radius
        self.ship_length = int(self.base_size * 1.2)
        self.ship_width = int(self.base_size * 0.8)
        
        # Ship properties
        self.ship_type = "Generic"
        
        # Weapon cooldowns
        self.cooldowns = {}
        
        print(f"Ship created: Scale={self.scale_factor:.3f}, Size={self.base_size:.1f}, HP={self.max_hp}J, Mass={self.mass:.0f}kg")
    
    def update(self, delta_time, keys_pressed):
        """Update ship with inertia physics"""
        # Reset acceleration
        self.ax = 0.0
        self.ay = 0.0
        
        # Calculate thrust forces based on input
        if keys_pressed[pygame.K_LEFT]:
            self.ax -= self.max_thrust / self.mass
        if keys_pressed[pygame.K_RIGHT]:
            self.ax += self.max_thrust / self.mass
        if keys_pressed[pygame.K_UP]:
            self.ay -= self.max_thrust / self.mass
        if keys_pressed[pygame.K_DOWN]:
            self.ay += self.max_thrust / self.mass
        
        # Apply drag force (opposes velocity)
        velocity_magnitude = math.hypot(self.vx, self.vy)
        if velocity_magnitude > 0:
            # Drag force = -drag_coefficient * velocity
            drag_ax = -self.drag_coefficient * self.vx
            drag_ay = -self.drag_coefficient * self.vy
            self.ax += drag_ax
            self.ay += drag_ay
        
        # Update velocity using acceleration (Euler integration)
        self.vx += self.ax * delta_time
        self.vy += self.ay * delta_time
        
        # Limit maximum velocity
        velocity_magnitude = math.hypot(self.vx, self.vy)
        if velocity_magnitude > self.max_velocity:
            scale = self.max_velocity / velocity_magnitude
            self.vx *= scale
            self.vy *= scale
        
        # Update position using velocity
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Keep on screen with bounce physics
        if self.x <= self.radius:
            self.x = self.radius
            self.vx = abs(self.vx) * 0.3  # Bounce with energy loss
        elif self.x >= self.screen_width - self.radius:
            self.x = self.screen_width - self.radius
            self.vx = -abs(self.vx) * 0.3
            
        if self.y <= self.radius:
            self.y = self.radius
            self.vy = abs(self.vy) * 0.3
        elif self.y >= self.screen_height - self.radius:
            self.y = self.screen_height - self.radius
            self.vy = -abs(self.vy) * 0.3
        
        # Update cooldowns
        for weapon in list(self.cooldowns.keys()):
            self.cooldowns[weapon] -= delta_time
            if self.cooldowns[weapon] <= 0:
                del self.cooldowns[weapon]
    
    def draw(self, screen):
        """Draw the ship with scaled size"""
        color = self._get_ship_color()
        
        # Draw ship as triangle - scaled to 0.6% of screen
        points = [
            (self.x, self.y - self.ship_length // 2),
            (self.x - self.ship_width // 2, self.y + self.ship_length // 2),
            (self.x + self.ship_width // 2, self.y + self.ship_length // 2)
        ]
        pygame.draw.polygon(screen, color, points)
        
        # Draw velocity indicator for debugging inertia
        if abs(self.vx) > 5 or abs(self.vy) > 5:
            end_x = self.x + self.vx * 0.1
            end_y = self.y + self.vy * 0.1
            pygame.draw.line(screen, (0, 255, 255), (self.x, self.y), (end_x, end_y), 2)
        
        # Draw ship specifics
        self._draw_ship_specifics(screen)
    
    def _get_ship_color(self):
        """Get ship color (override in subclasses)"""
        return (255, 255, 255)
    
    def _draw_ship_specifics(self, screen):
        """Draw ship-specific elements (override in subclasses)"""
        pass
    
    def take_damage(self, damage_joules, damage_type="generic"):
        """Apply damage in joules to ship"""
        original_hp = self.current_hp
        original_shield = self.current_shield
        
        # Shield absorbs damage first
        if self.current_shield > 0:
            shield_damage = min(damage_joules, self.current_shield)
            self.current_shield -= shield_damage
            damage_joules -= shield_damage
            print(f"Shield absorbed {shield_damage:.1f} J, remaining: {self.current_shield:.1f} J")
        
        # Remaining damage goes to hull
        if damage_joules > 0:
            hull_damage = min(damage_joules, self.current_hp)
            self.current_hp -= hull_damage
            print(f"Hull took {hull_damage:.1f} J damage, remaining: {self.current_hp:.1f} J")
            
            # Apply physical impulse from damage (realistic knockback)
            impulse_strength = math.sqrt(hull_damage) * 0.01
            damage_angle = random.uniform(0, 2 * math.pi)
            self.vx += math.cos(damage_angle) * impulse_strength
            self.vy += math.sin(damage_angle) * impulse_strength
        
        # Trigger damage flash if available
        if hasattr(self, 'trigger_damage_flash'):
            self.trigger_damage_flash()
        
        return self.current_hp <= 0
    
    def is_dead(self):
        """Check if ship is destroyed"""
        return self.current_hp <= 0
    
    def get_special_abilities(self):
        """Get list of special abilities (override in subclasses)"""
        return []
    
    def fire_special_weapon(self, ability_name, projectile_manager):
        """Fire special weapon (override in subclasses)"""
        return False
    
    def get_velocity(self):
        """Get current velocity vector"""
        return (self.vx, self.vy)
    
    def get_kinetic_energy(self):
        """Get current kinetic energy of ship"""
        velocity_squared = self.vx * self.vx + self.vy * self.vy
        return 0.5 * self.mass * velocity_squared
    
    def apply_impulse(self, force_x, force_y):
        """Apply instantaneous force impulse (for explosions, collisions)"""
        impulse_x = force_x / self.mass
        impulse_y = force_y / self.mass
        self.vx += impulse_x
        self.vy += impulse_y
    
    def _recalculate_stats(self):
        """Recalculate ship stats (for upgrades)"""
        pass