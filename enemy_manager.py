#!/usr/bin/env python3
import pygame
import math
import random

class BasicEnemy:
    """Enemy with progression integration"""
    
    def __init__(self, x, y, enemy_type="fighter", level=1, screen_width=1920, screen_height=1080):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.level = level
        
        # Calculate 0.6% scale factor
        self.scale_factor = 0.006
        self.base_size = min(screen_width, screen_height) * self.scale_factor
        
        # Movement properties - scaled to screen
        self.vx = random.uniform(-50, 50) * (self.base_size / 13)
        self.vy = random.uniform(20, 60) * (self.base_size / 13)
        self.max_speed = 80 * (self.base_size / 13)
        
        # Combat properties based on level and constants
        hp_scale = (self.base_size / 13) ** 1.5
        self.max_hp = int(self._calculate_realistic_hp(enemy_type, level) * hp_scale)
        self.current_hp = self.max_hp
        self.damage = int((5 + level) * hp_scale)
        
        # Visual properties - scaled
        base_radius = {"fighter": 12, "bomber": 16, "scout": 8}
        self.radius = max(4, int((base_radius.get(enemy_type, 12) + level * 2) * (self.base_size / 13)))
        self.color = self._get_enemy_color()
        
        # Physics properties - scaled
        self.mass = 500.0 * (self.base_size / 13) * level
        
        # AI behavior
        self.behavior_timer = 0
        self.behavior_change_interval = random.uniform(2.0, 4.0)
        self.target_vx = self.vx
        self.shoot_timer = 0
        self.shoot_interval = random.uniform(1.5, 3.0)
        
        # Status flags
        self.active = True
        self.alive = True
        self.death_timer = 0
        
        # Progression tracking
        self.exp_value = self._calculate_exp_value()
        self.drop_level = level  # Used for drop calculation
        
        print(f"Created {enemy_type} L{level}: HP={self.max_hp}J, EXP={self.exp_value}")
    
    def _calculate_realistic_hp(self, enemy_type, level):
        """Calculate HP based on constants and type"""
        base_hp_joules = {
            "fighter": 1500,
            "bomber": 4000,
            "scout": 800
        }
        
        base_hp = base_hp_joules.get(enemy_type, 1500)
        level_multiplier = 1.0 + (level - 1) * 0.8
        return base_hp * level_multiplier
    
    def _calculate_exp_value(self):
        """Calculate experience value based on enemy stats"""
        base_exp = {"fighter": 10, "bomber": 15, "scout": 8}
        type_exp = base_exp.get(self.enemy_type, 10)
        level_bonus = (self.level - 1) * 5
        return type_exp + level_bonus
    
    def _get_enemy_color(self):
        """Get enemy color based on type and level"""
        base_colors = {
            "fighter": (255, 100, 100),
            "bomber": (100, 255, 100),
            "scout": (100, 100, 255)
        }
        
        base_color = base_colors.get(self.enemy_type, (150, 150, 150))
        level_mult = min(1.5, 1.0 + (self.level * 0.1))
        return tuple(min(255, int(c * level_mult)) for c in base_color)
    
    def update(self, delta_time, player_ship, screen_width, screen_height):
        """Update enemy AI and movement"""
        if not self.alive:
            return
        
        # Update behavior timer
        self.behavior_timer += delta_time
        if self.behavior_timer >= self.behavior_change_interval:
            self._change_behavior()
            self.behavior_timer = 0
        
        # Smooth movement toward target velocity
        accel = 100 * (self.base_size / 13)
        if self.vx < self.target_vx:
            self.vx = min(self.target_vx, self.vx + accel * delta_time)
        elif self.vx > self.target_vx:
            self.vx = max(self.target_vx, self.vx - accel * delta_time)
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Keep within screen bounds
        if self.x <= self.radius or self.x >= screen_width - self.radius:
            self.vx = -self.vx
            self.target_vx = -self.target_vx
            self.x = max(self.radius, min(screen_width - self.radius, self.x))
        
        # Shooting AI
        if self.alive and player_ship:
            self.shoot_timer += delta_time
            if self.shoot_timer >= self.shoot_interval:
                self._attempt_shoot(player_ship)
                self.shoot_timer = 0
                self.shoot_interval = random.uniform(2.0, 4.0)
    
    def _change_behavior(self):
        """Change enemy movement pattern"""
        behaviors = ["straight", "zigzag", "toward_player", "evasive"]
        behavior = random.choice(behaviors)
        
        speed_scale = self.base_size / 13
        
        if behavior == "straight":
            self.target_vx = random.uniform(-30, 30) * speed_scale
        elif behavior == "zigzag":
            self.target_vx = random.choice([-60, 60]) * speed_scale
        elif behavior == "toward_player":
            self.target_vx = random.uniform(-40, 40) * speed_scale
        elif behavior == "evasive":
            self.target_vx = random.uniform(-80, 80) * speed_scale
        
        self.behavior_change_interval = random.uniform(1.5, 3.5)
    
    def _attempt_shoot(self, player_ship):
        """Attempt to shoot at player"""
        if random.random() < 0.1:
            pass  # Placeholder for enemy weapons
    
    def take_damage(self, damage_joules, damage_type="generic"):
        """Apply damage with pure joule system"""
        if not self.alive:
            return False
        
        original_hp = self.current_hp
        self.current_hp -= damage_joules
        
        print(f"{self.enemy_type} L{self.level} took {damage_joules:.1f}J damage ({original_hp:.0f} -> {self.current_hp:.0f}J)")
        
        # Apply knockback
        if damage_joules > 100:
            knockback_force = math.sqrt(damage_joules) * 0.1
            knockback_angle = random.uniform(0, 2 * math.pi)
            self.vx += math.cos(knockback_angle) * knockback_force
            self.vy += math.sin(knockback_angle) * knockback_force
        
        # Check if killed
        if self.current_hp <= 0:
            self.current_hp = 0
            self.alive = False
            self.active = False
            print(f"{self.enemy_type} L{self.level} destroyed! Worth {self.exp_value} EXP")
            return True
        
        return False
    
    def is_dead(self):
        """Check if enemy is dead"""
        return not self.alive
    
    def is_off_screen(self, screen_height):
        """Check if enemy has moved off screen"""
        return self.y > screen_height + 50
    
    def draw(self, screen):
        """Draw enemy with level indicators"""
        if not self.alive:
            return
        
        # Main enemy body
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        
        # Health bar
        self._draw_health_bar(screen)
        
        # Level indicator
        if self.level > 1:
            font_size = max(12, int(20 * (self.base_size / 13)))
            font = pygame.font.Font(None, font_size)
            level_text = font.render(str(self.level), True, (255, 255, 255))
            text_rect = level_text.get_rect(center=(self.x, self.y))
            screen.blit(level_text, text_rect)
    
    def _draw_health_bar(self, screen):
        """Draw health bar above enemy"""
        bar_width = self.radius * 2
        bar_height = max(2, int(4 * (self.base_size / 13)))
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.radius - 10
        
        # Background (red)
        pygame.draw.rect(screen, (100, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        
        # Health (green)
        health_ratio = self.current_hp / self.max_hp
        health_width = int(bar_width * health_ratio)
        if health_width > 0:
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))


class EnemyManager:
    """Enemy manager with progression integration"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Scale factor
        self.scale_factor = 0.006
        self.base_size = min(screen_width, screen_height) * self.scale_factor
        
        # Enemy tracking
        self.enemies = []
        self.enemies_killed_this_wave = 0
        self.total_enemies_killed = 0
        
        # Wave management
        self.current_wave = 1
        self.enemies_to_spawn = 0
        self.spawn_timer = 0
        self.spawn_interval = 2.0
        self.wave_complete = False
        self.wave_completion_timer = 0
        
        # Spawn positions
        self.spawn_positions = self._calculate_spawn_positions()
        
        # Progression integration
        self.input_manager = None  # Set by GameDirector
        
        print(f"EnemyManager with progression: Scale={self.scale_factor:.3f}")
    
    def set_input_manager(self, input_manager):
        """Set reference to input manager for progression callbacks"""
        self.input_manager = input_manager
    
    def _calculate_spawn_positions(self):
        """Calculate enemy spawn positions"""
        positions = []
        spawn_count = 8
        spawn_offset = max(25, int(50 * (self.base_size / 13)))
        
        for i in range(spawn_count):
            x = (self.screen_width / (spawn_count + 1)) * (i + 1)
            y = -spawn_offset
            positions.append((x, y))
        
        return positions
    
    def start_wave(self, wave_number):
        """Start new wave"""
        self.current_wave = wave_number
        self.wave_complete = False
        self.wave_completion_timer = 0
        self.enemies_killed_this_wave = 0
        
        # Enemy count from constants
        base_enemies = 5
        self.enemies_to_spawn = base_enemies + (wave_number - 1) * 2
        
        # Spawn rate
        self.spawn_interval = max(0.5, 2.0 - (wave_number * 0.1))
        
        print(f"Starting wave {wave_number} - {self.enemies_to_spawn} enemies")
    
    def update(self, delta_time, player_ship):
        """Update enemies with progression integration"""
        # Spawn new enemies
        if self.enemies_to_spawn > 0:
            self.spawn_timer += delta_time
            if self.spawn_timer >= self.spawn_interval:
                self._spawn_enemy()
                self.spawn_timer = 0
        
        # Update existing enemies
        for enemy in self.enemies[:]:
            if enemy.alive:
                enemy.update(delta_time, player_ship, self.screen_width, self.screen_height)
            
            # Handle dead enemies
            if not enemy.alive:
                # Award experience and drops through input manager
                if self.input_manager:
                    progression_result = self.input_manager.on_enemy_killed(
                        enemy.level, enemy.enemy_type
                    )
                    
                    if progression_result:
                        print(f"Player gained {progression_result['exp_gained']} EXP")
                        if progression_result['leveled_up']:
                            print("PLAYER LEVELED UP!")
                        if progression_result['drop']:
                            drop = progression_result['drop']
                            print(f"Dropped: {drop['amount']} {drop['type']}")
                
                self.enemies_killed_this_wave += 1
                self.total_enemies_killed += 1
                self.enemies.remove(enemy)
            
            # Remove off-screen enemies
            elif enemy.is_off_screen(self.screen_height):
                self.enemies.remove(enemy)
        
        # Check wave completion
        living_enemies = sum(1 for enemy in self.enemies if enemy.alive)
        if self.enemies_to_spawn <= 0 and living_enemies == 0 and not self.wave_complete:
            self.wave_complete = True
            self.wave_completion_timer = delta_time
            print(f"Wave {self.current_wave} complete!")
    
    def _spawn_enemy(self):
        """Spawn new enemy with appropriate level"""
        if self.enemies_to_spawn <= 0:
            return
        
        # Choose spawn position
        spawn_pos = random.choice(self.spawn_positions)
        
        # Enemy type based on wave
        if self.current_wave <= 2:
            enemy_type = "fighter"
        elif self.current_wave <= 5:
            enemy_type = random.choice(["fighter", "fighter", "bomber"])
        else:
            enemy_type = random.choice(["fighter", "bomber", "scout"])
        
        # Enemy level with scaling
        base_level = max(1, self.current_wave // 3)
        level_variance = random.randint(0, 2)
        enemy_level = base_level + level_variance
        
        # Create enemy
        enemy = BasicEnemy(spawn_pos[0], spawn_pos[1], enemy_type, enemy_level,
                          self.screen_width, self.screen_height)
        
        self.enemies.append(enemy)
        self.enemies_to_spawn -= 1
    
    def is_wave_complete(self):
        """Check if wave is complete"""
        return self.wave_complete
    
    def get_enemy_count(self):
        """Get living enemy count"""
        return sum(1 for enemy in self.enemies if enemy.alive)
    
    def clear_all_enemies(self):
        """Clear all enemies"""
        self.enemies.clear()
        self.enemies_to_spawn = 0
        self.wave_complete = False
    
    def draw(self, screen):
        """Draw all living enemies"""
        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(screen)
    
    def debug_info(self):
        """Return debug information"""
        living_enemies = sum(1 for enemy in self.enemies if enemy.alive)
        return {
            "wave": self.current_wave,
            "enemies_active": living_enemies,
            "enemies_to_spawn": self.enemies_to_spawn,
            "enemies_killed_this_wave": self.enemies_killed_this_wave,
            "total_killed": self.total_enemies_killed,
            "wave_complete": self.wave_complete,
            "scale_factor": self.scale_factor
        }