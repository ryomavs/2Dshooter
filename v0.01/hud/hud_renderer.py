#!/usr/bin/env python3
import pygame
import math

class HUDRenderer:
    """HUD renderer with 0.6% screen scaling and inertia physics display"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate 0.6% scale factor
        self.scale_factor = 0.006
        self.base_size = min(screen_width, screen_height) * self.scale_factor
        
        # HUD layout configuration - all scaled
        self.margin = max(10, int(20 * (self.base_size / 13)))
        self.bar_height = max(12, int(24 * (self.base_size / 13)))
        self.bar_width = max(150, int(300 * (self.base_size / 13)))
        
        # Font sizes - scaled
        self.font_size_large = max(16, int(32 * (self.base_size / 13)))
        self.font_size_medium = max(12, int(24 * (self.base_size / 13)))
        self.font_size_small = max(9, int(18 * (self.base_size / 13)))
        
        # Fonts
        self.font_large = pygame.font.Font(None, self.font_size_large)
        self.font_medium = pygame.font.Font(None, self.font_size_medium)
        self.font_small = pygame.font.Font(None, self.font_size_small)
        
        # Colors
        self.colors = {
            'hp_bar': (255, 50, 50),
            'hp_bg': (100, 20, 20),
            'shield_bar': (50, 150, 255),
            'shield_bg': (20, 60, 100),
            'cannon_heat': (255, 200, 50),
            'cannon_heat_bg': (100, 80, 20),
            'text_primary': (255, 255, 255),
            'text_secondary': (200, 200, 200),
            'text_warning': (255, 255, 100),
            'text_danger': (255, 100, 100),
            'hud_bg': (0, 0, 0, 128),
            'velocity_indicator': (0, 255, 255),
            'physics_debug': (255, 255, 0)
        }
        
        # HUD element positions
        self.positions = self._calculate_positions()
        
        # Animation states
        self.damage_flash_timer = 0
        self.low_health_pulse = 0
        
        print(f"HUD initialized: Scale={self.scale_factor:.3f}, Base size={self.base_size:.1f}px")
    
    def _calculate_positions(self):
        """Calculate positions for HUD elements - all scaled"""
        positions = {}
        
        # Top-left status area
        positions['hp_bar'] = (self.margin, self.margin)
        positions['shield_bar'] = (self.margin, self.margin + self.bar_height + 10)
        positions['cannon_heat'] = (self.margin, self.margin + (self.bar_height + 10) * 2)
        positions['physics_info'] = (self.margin, self.margin + (self.bar_height + 10) * 3)
        
        # Top-right info area
        info_x = self.screen_width - max(200, int(250 * (self.base_size / 13)))
        positions['wave_info'] = (info_x, self.margin)
        positions['score_info'] = (info_x, self.margin + 40)
        positions['enemy_count'] = (info_x, self.margin + 80)
        
        # Bottom-left weapon info
        positions['weapon_info'] = (self.margin, self.screen_height - max(60, int(120 * (self.base_size / 13))))
        
        # Bottom-right system info
        positions['system_info'] = (self.screen_width - max(150, int(300 * (self.base_size / 13))), 
                                   self.screen_height - max(40, int(80 * (self.base_size / 13))))
        
        return positions
    
    def update(self, delta_time):
        """Update HUD animations"""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= delta_time
        
        self.low_health_pulse += delta_time * 4
    
    def draw(self, screen, player_ship, current_wave, enemy_manager=None, projectile_manager=None):
        """Draw complete HUD with inertia physics display"""
        if not player_ship:
            return
        
        # Draw main HUD elements
        self._draw_health_bars(screen, player_ship)
        self._draw_wave_info(screen, current_wave, enemy_manager)
        self._draw_weapon_info(screen, player_ship)
        self._draw_physics_info(screen, player_ship)
        
        # Draw optional elements
        if projectile_manager:
            self._draw_performance_info(screen, projectile_manager)
        
        # Draw damage indicator if active
        if self.damage_flash_timer > 0:
            self._draw_damage_indicator(screen)
    
    def _draw_health_bars(self, screen, player_ship):
        """Draw HP and shield bars with joule values"""
        # HP Bar
        hp_pos = self.positions['hp_bar']
        hp_ratio = max(0, player_ship.current_hp / player_ship.max_hp)
        
        # Background
        pygame.draw.rect(screen, self.colors['hp_bg'], 
                        (hp_pos[0], hp_pos[1], self.bar_width, self.bar_height))
        
        # HP fill with low health warning
        hp_color = self.colors['hp_bar']
        if hp_ratio < 0.25:
            pulse = abs(math.sin(self.low_health_pulse))
            hp_color = (255, int(50 + 100 * pulse), int(50 * pulse))
        
        hp_fill_width = int(self.bar_width * hp_ratio)
        if hp_fill_width > 0:
            pygame.draw.rect(screen, hp_color,
                            (hp_pos[0], hp_pos[1], hp_fill_width, self.bar_height))
        
        # HP text with joule values
        hp_text = f"Hull: {int(player_ship.current_hp)}J / {int(player_ship.max_hp)}J"
        text_surface = self.font_medium.render(hp_text, True, self.colors['text_primary'])
        text_rect = text_surface.get_rect(center=(hp_pos[0] + self.bar_width//2, hp_pos[1] + self.bar_height//2))
        screen.blit(text_surface, text_rect)
        
        # Shield Bar
        shield_pos = self.positions['shield_bar']
        shield_ratio = max(0, player_ship.current_shield / player_ship.max_shield)
        
        # Background
        pygame.draw.rect(screen, self.colors['shield_bg'],
                        (shield_pos[0], shield_pos[1], self.bar_width, self.bar_height))
        
        # Shield fill
        shield_fill_width = int(self.bar_width * shield_ratio)
        if shield_fill_width > 0:
            pygame.draw.rect(screen, self.colors['shield_bar'],
                            (shield_pos[0], shield_pos[1], shield_fill_width, self.bar_height))
        
        # Shield text with joule values
        shield_text = f"Shield: {int(player_ship.current_shield)}J / {int(player_ship.max_shield)}J"
        text_surface = self.font_medium.render(shield_text, True, self.colors['text_primary'])
        text_rect = text_surface.get_rect(center=(shield_pos[0] + self.bar_width//2, shield_pos[1] + self.bar_height//2))
        screen.blit(text_surface, text_rect)
        
        # Cannon heat (if ship has universal cannon)
        if hasattr(player_ship, 'universal_cannon'):
            self._draw_cannon_heat_bar(screen, player_ship.universal_cannon)
    
    def _draw_cannon_heat_bar(self, screen, cannon):
        """Draw cannon heat/overheat bar"""
        heat_pos = self.positions['cannon_heat']
        heat_ratio = cannon.get_heat_percentage()
        
        # Background
        pygame.draw.rect(screen, self.colors['cannon_heat_bg'],
                        (heat_pos[0], heat_pos[1], self.bar_width, self.bar_height))
        
        # Heat fill
        heat_fill_width = int(self.bar_width * heat_ratio)
        if heat_fill_width > 0:
            heat_color = self.colors['cannon_heat']
            if heat_ratio > 0.8:
                heat_color = (255, int(200 * (1.0 - heat_ratio)), 50)
            
            pygame.draw.rect(screen, heat_color,
                            (heat_pos[0], heat_pos[1], heat_fill_width, self.bar_height))
        
        # Heat text
        heat_text = "OVERHEATED!" if cannon.is_overheated() else f"Cannon: {int(heat_ratio * 100)}%"
        text_color = self.colors['text_danger'] if cannon.is_overheated() else self.colors['text_primary']
        text_surface = self.font_medium.render(heat_text, True, text_color)
        text_rect = text_surface.get_rect(center=(heat_pos[0] + self.bar_width//2, heat_pos[1] + self.bar_height//2))
        screen.blit(text_surface, text_rect)
    
    def _draw_physics_info(self, screen, player_ship):
        """Draw inertia physics information"""
        physics_pos = self.positions['physics_info']
        
        # Get physics data
        if hasattr(player_ship, 'get_velocity'):
            vx, vy = player_ship.get_velocity()
            velocity_magnitude = math.hypot(vx, vy)
            kinetic_energy = player_ship.get_kinetic_energy()
            
            # Velocity display
            velocity_text = f"Velocity: {velocity_magnitude:.1f} m/s"
            velocity_surface = self.font_small.render(velocity_text, True, self.colors['velocity_indicator'])
            screen.blit(velocity_surface, physics_pos)
            
            # Kinetic energy display
            energy_text = f"Kinetic: {kinetic_energy:.0f} J"
            energy_surface = self.font_small.render(energy_text, True, self.colors['physics_debug'])
            screen.blit(energy_surface, (physics_pos[0], physics_pos[1] + 20))
            
            # Mass display
            mass_text = f"Mass: {player_ship.mass:.0f} kg"
            mass_surface = self.font_small.render(mass_text, True, self.colors['text_secondary'])
            screen.blit(mass_surface, (physics_pos[0], physics_pos[1] + 40))
    
    def _draw_wave_info(self, screen, current_wave, enemy_manager):
        """Draw wave information with scaling info"""
        wave_pos = self.positions['wave_info']
        
        # Wave number
        wave_text = f"Wave {current_wave}"
        wave_surface = self.font_large.render(wave_text, True, self.colors['text_primary'])
        screen.blit(wave_surface, wave_pos)
        
        # Enemy count with scale info
        enemy_pos = self.positions['enemy_count']
        if enemy_manager:
            debug_info = enemy_manager.debug_info()
            enemies_text = f"Enemies: {debug_info['enemies_active']}"
            if debug_info['enemies_to_spawn'] > 0:
                enemies_text += f" (+{debug_info['enemies_to_spawn']})"
            
            enemies_surface = self.font_medium.render(enemies_text, True, self.colors['text_secondary'])
            screen.blit(enemies_surface, enemy_pos)
            
            # Kills this wave
            kills_text = f"Kills: {debug_info['enemies_killed_this_wave']}"
            kills_surface = self.font_medium.render(kills_text, True, self.colors['text_secondary'])
            screen.blit(kills_surface, (enemy_pos[0], enemy_pos[1] + 30))
            
            # Scale factor display
            scale_text = f"Scale: {debug_info['scale_factor']:.1%}"
            scale_surface = self.font_small.render(scale_text, True, self.colors['text_secondary'])
            screen.blit(scale_surface, (enemy_pos[0], enemy_pos[1] + 55))
    
    def _draw_weapon_info(self, screen, player_ship):
        """Draw weapon cooldown and ability info"""
        weapon_pos = self.positions['weapon_info']
        
        # Ship type
        ship_text = f"Ship: {player_ship.ship_type}"
        ship_surface = self.font_medium.render(ship_text, True, self.colors['text_primary'])
        screen.blit(ship_surface, weapon_pos)
        
        # Weapon cooldowns
        if hasattr(player_ship, 'cooldowns'):
            y_offset = 30
            for weapon, cooldown_time in player_ship.cooldowns.items():
                if cooldown_time > 0:
                    cooldown_text = f"{weapon.replace('_', ' ').title()}: {cooldown_time:.1f}s"
                    color = self.colors['text_warning']
                else:
                    cooldown_text = f"{weapon.replace('_', ' ').title()}: READY"
                    color = self.colors['text_secondary']
                
                cooldown_surface = self.font_small.render(cooldown_text, True, color)
                screen.blit(cooldown_surface, (weapon_pos[0], weapon_pos[1] + y_offset))
                y_offset += 20
        
        # Special status effects
        if hasattr(player_ship, 'overcharge_active') and player_ship.overcharge_active:
            overcharge_text = f"OVERCHARGED: {player_ship.overcharge_timer:.1f}s"
            overcharge_surface = self.font_medium.render(overcharge_text, True, (255, 255, 0))
            screen.blit(overcharge_surface, (weapon_pos[0], weapon_pos[1] + y_offset))
    
    def _draw_performance_info(self, screen, projectile_manager):
        """Draw performance information with joule damage tracking"""
        perf_pos = self.positions['system_info']
        
        # Projectile count
        proj_count = projectile_manager.get_projectile_count()
        proj_text = f"Projectiles: {proj_count}"
        proj_surface = self.font_small.render(proj_text, True, self.colors['text_secondary'])
        screen.blit(proj_surface, perf_pos)
        
        # Scale information
        scale_text = f"Scale: {self.scale_factor:.1%}"
        scale_surface = self.font_small.render(scale_text, True, self.colors['text_secondary'])
        screen.blit(scale_surface, (perf_pos[0], perf_pos[1] + 20))
    
    def _draw_damage_indicator(self, screen):
        """Draw red flash when player takes damage"""
        alpha = int(100 * (self.damage_flash_timer / 0.5))
        damage_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        damage_surface.fill((255, 0, 0, alpha))
        screen.blit(damage_surface, (0, 0))
    
    def draw_controls_help(self, screen):
        """Draw control hints with inertia physics information"""
        controls = [
            "Controls:",
            "Arrow Keys - Thrust (Inertia)",
            "Left Ctrl - Cannon", 
            "Space - Breach Bomb",
            "Q - Cluster Strike", 
            "Z - Overcharge",
            "F1 - Toggle Help",
            "ESC - Pause",
            "",
            "Physics:",
            "Ship has realistic inertia",
            "Damage in pure joules",
            "0.6% screen scaling"
        ]
        
        # Background panel - scaled
        panel_width = max(150, int(200 * (self.base_size / 13)))
        panel_height = len(controls) * max(12, int(25 * (self.base_size / 13))) + 20
        panel_x = self.screen_width - panel_width - self.margin
        panel_y = self.screen_height // 2 - panel_height // 2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['hud_bg'])
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Control text
        line_height = max(12, int(25 * (self.base_size / 13)))
        for i, control in enumerate(controls):
            if control == "":
                continue
            elif control in ["Controls:", "Physics:"]:
                color = self.colors['text_warning']
            else:
                color = self.colors['text_secondary']
            
            control_surface = self.font_small.render(control, True, color)
            screen.blit(control_surface, (panel_x + 10, panel_y + 10 + i * line_height))
    
    def trigger_damage_flash(self):
        """Trigger damage indicator flash"""
        self.damage_flash_timer = 0.5
    
    def draw_game_over(self, screen, final_wave, total_kills, survival_time):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, self.colors['text_danger'])
        game_over_rect = game_over_text.get_rect(center=(self.screen_width//2, self.screen_height//2 - 100))
        screen.blit(game_over_text, game_over_rect)
        
        # Stats
        stats = [
            f"Final Wave: {final_wave}",
            f"Total Kills: {total_kills}",
            f"Survival Time: {survival_time:.1f}s",
            f"Physics: Pure joule damage with inertia",
            f"Scale: {self.scale_factor:.1%} screen scaling"
        ]
        
        for i, stat in enumerate(stats):
            stat_surface = self.font_medium.render(stat, True, self.colors['text_primary'])
            stat_rect = stat_surface.get_rect(center=(self.screen_width//2, self.screen_height//2 - 20 + i * 40))
            screen.blit(stat_surface, stat_rect)
        
        # Restart hint
        restart_text = self.font_medium.render("Press ESC to return to menu", True, self.colors['text_secondary'])
        restart_rect = restart_text.get_rect(center=(self.screen_width//2, self.screen_height//2 + 150))
        screen.blit(restart_text, restart_rect)
    
    def draw_wave_complete(self, screen, wave_number, next_wave_timer):
        """Draw wave completion notification"""
        # Background panel - scaled
        panel_width = max(200, int(400 * (self.base_size / 13)))
        panel_height = max(50, int(100 * (self.base_size / 13)))
        panel_x = self.screen_width//2 - panel_width//2
        panel_y = self.screen_height//2 - panel_height//2
        
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['hud_bg'])
        pygame.draw.rect(panel_surface, self.colors['text_primary'], (0, 0, panel_width, panel_height), 2)
        screen.blit(panel_surface, (panel_x, panel_y))
        
        # Wave complete text
        wave_text = f"Wave {wave_number} Complete!"
        wave_surface = self.font_large.render(wave_text, True, self.colors['text_primary'])
        wave_rect = wave_surface.get_rect(center=(panel_width//2, panel_height//3))
        panel_surface.blit(wave_surface, wave_rect)
        
        # Next wave timer
        timer_text = f"Next wave in {next_wave_timer:.1f}s"
        timer_surface = self.font_medium.render(timer_text, True, self.colors['text_secondary'])
        timer_rect = timer_surface.get_rect(center=(panel_width//2, panel_height*2//3))
        panel_surface.blit(timer_surface, timer_rect)