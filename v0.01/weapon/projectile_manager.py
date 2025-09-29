#!/usr/bin/env python3
import pygame
import math
import random
from damage_calculator import DamageCalculator

class ProjectileManager:
    """Projectile manager with pure joule damage and 0.6% screen scaling"""
    
    def __init__(self, screen_width, screen_height):
        # Active projectiles
        self.bombs = []
        self.kinetic_shots = []
        self.energy_beams = []
        
        # Screen boundaries for cleanup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cleanup_margin = 100
        
        # Calculate 0.6% scale factor for all projectiles
        self.scale_factor = 0.006
        self.base_size = min(screen_width, screen_height) * self.scale_factor
        
        # Reference to other systems
        self.effect_manager = None
        
        print(f"ProjectileManager: Scale={self.scale_factor:.3f}, Base size={self.base_size:.1f}px")
    
    def set_effect_manager(self, effect_manager):
        """Set reference to effect manager for visual effects"""
        self.effect_manager = effect_manager
    
    def add_bomb(self, x, y, vx, vy, bomb_stats, group_id):
        """Add bomb projectile with pure joule damage"""
        # Convert bomb stats to warhead data for damage calculator
        warhead_data = DamageCalculator.create_warhead_data_from_db(bomb_stats)
        
        bomb = {
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "warhead_data": warhead_data,
            "bomb_stats": bomb_stats,
            "group_id": group_id,
            "active": True,
            "lifetime": 10.0,
            "projectile_type": "bomb",
            "radius": max(4, int(self.base_size * 0.6)),  # Scaled bomb visual size
            "proximity_radius": max(15, int(self.base_size * 1.8))  # Scaled proximity fuse
        }
        
        self.bombs.append(bomb)
        print(f"Added bomb: {warhead_data['explosive_kg']:.1f}kg explosive, {warhead_data['shrapnel_kg']:.1f}kg shrapnel")
        return bomb
    
    def add_kinetic_shot(self, x, y, vx, vy, projectile_data, is_player_shot=True):
        """Add kinetic projectile with pure joule damage"""
        shot = {
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "projectile_data": projectile_data,
            "is_player_shot": is_player_shot,
            "active": True,
            "lifetime": 5.0,
            "projectile_type": "kinetic",
            "radius": max(2, int(self.base_size * 0.15))  # Scaled shot visual size
        }
        
        # Calculate and store pure joule damage
        shot["joule_damage"] = DamageCalculator.calculate_projectile_damage(projectile_data)
        
        self.kinetic_shots.append(shot)
        if is_player_shot:
            print(f"Player shot: {shot['joule_damage']:.0f} J kinetic energy")
        else:
            print(f"Enemy shot: {shot['joule_damage']:.0f} J kinetic energy")
        return shot
    
    def add_energy_beam(self, x, y, target_x, target_y, weapon_data, duration):
        """Add energy beam with pure joule damage"""
        beam = {
            "start_x": x,
            "start_y": y,
            "end_x": target_x,
            "end_y": target_y,
            "weapon_data": weapon_data,
            "remaining_duration": duration,
            "active": True,
            "projectile_type": "energy",
            "width": max(3, int(self.base_size * 0.25))  # Scaled beam width
        }
        
        # Calculate pure joule damage for this beam
        beam["joule_damage"] = DamageCalculator.calculate_energy_weapon_damage(
            weapon_data, (target_x, target_y), (x, y)
        )
        
        self.energy_beams.append(beam)
        print(f"Energy beam: {beam['joule_damage']:.0f} J energy pulse")
        return beam
    
    def update(self, delta_time, enemies, player_ship):
        """Update all projectiles and handle collisions with pure joule damage"""
        self._update_bombs(delta_time, enemies, player_ship)
        self._update_kinetic_shots(delta_time, enemies, player_ship)
        self._update_energy_beams(delta_time, enemies, player_ship)
        self._cleanup_projectiles()
    
    def _update_bombs(self, delta_time, enemies, player_ship):
        """Update bomb projectiles with proximity fusing"""
        for bomb in self.bombs[:]:
            if not bomb["active"]:
                continue
            
            # Update position
            bomb["x"] += bomb["vx"] * delta_time
            bomb["y"] += bomb["vy"] * delta_time
            bomb["lifetime"] -= delta_time
            
            # Auto-destruct if lifetime exceeded
            if bomb["lifetime"] <= 0:
                bomb["active"] = False
                continue
            
            # Check proximity fuse against living enemies
            enemy_positions = [(enemy.x, enemy.y) for enemy in enemies if hasattr(enemy, 'x') and enemy.alive]
            should_trigger, closest_target = DamageCalculator.check_proximity_trigger(
                (bomb["x"], bomb["y"]),
                (bomb["vx"], bomb["vy"]),
                enemy_positions,
                fuse_radius=bomb["proximity_radius"],
                delta_time=delta_time
            )
            
            if should_trigger:
                self._detonate_bomb(bomb, enemies, player_ship)
                bomb["active"] = False
    
    def _detonate_bomb(self, bomb, enemies, player_ship):
        """Handle bomb detonation with PURE JOULE DAMAGE"""
        explosion_center = (bomb["x"], bomb["y"])
        
        print(f"BOMB DETONATION: {bomb['warhead_data']['explosive_kg']:.1f}kg explosive at ({bomb['x']:.0f}, {bomb['y']:.0f})")
        
        # Create explosion visual effect - scaled
        if self.effect_manager:
            explosion_size = self._calculate_explosion_size(bomb["warhead_data"])
            self.effect_manager.add_explosion(
                bomb["x"], bomb["y"], 
                size=explosion_size * (self.base_size / 13), 
                duration=1.0
            )
        
        # Apply PURE JOULE damage to each living enemy
        for enemy in enemies[:]:
            if not hasattr(enemy, 'x') or not hasattr(enemy, 'y') or not enemy.alive:
                continue
            
            target_pos = (enemy.x, enemy.y)
            distance = DamageCalculator.calculate_distance(explosion_center, target_pos)
            
            # Calculate PURE JOULE damage - no scaling factors
            damage_joules = DamageCalculator.calculate_explosion_damage(
                explosion_center,
                target_pos,
                bomb["warhead_data"]
            )
            
            if damage_joules > 0:
                print(f"Enemy at {distance:.0f}px takes {damage_joules:.0f} J explosive damage")
                
                # Apply PURE JOULE damage
                was_killed = enemy.take_damage(damage_joules, "explosive")
                
                # Show damage text
                if self.effect_manager:
                    self.effect_manager.add_floating_text(
                        enemy.x, enemy.y, f"{damage_joules:.0f}J", was_killed
                    )
        
        # Check player friendly fire with PURE JOULE damage
        if player_ship:
            player_pos = (player_ship.x, player_ship.y)
            player_distance = DamageCalculator.calculate_distance(explosion_center, player_pos)
            
            player_damage_joules = DamageCalculator.calculate_explosion_damage(
                explosion_center,
                player_pos,
                bomb["warhead_data"]
            )
            
            if player_damage_joules > 0:
                # Reduced friendly fire (10%)
                friendly_fire_joules = player_damage_joules * 0.1
                print(f"Player takes {friendly_fire_joules:.0f} J friendly fire at {player_distance:.0f}px")
                player_ship.take_damage(friendly_fire_joules, "explosive")
    
    def _update_kinetic_shots(self, delta_time, enemies, player_ship):
        """Update kinetic projectiles with PURE JOULE damage"""
        for shot in self.kinetic_shots[:]:
            if not shot["active"]:
                continue
            
            # Update position
            shot["x"] += shot["vx"] * delta_time
            shot["y"] += shot["vy"] * delta_time
            shot["lifetime"] -= delta_time
            
            if shot["lifetime"] <= 0:
                shot["active"] = False
                continue
            
            # Check collisions
            if shot["is_player_shot"]:
                # Player shots vs enemies - PURE JOULE DAMAGE
                for enemy in enemies[:]:
                    if not hasattr(enemy, 'x') or not hasattr(enemy, 'y') or not enemy.alive:
                        continue
                    
                    # Scaled collision detection
                    collision_distance = shot["radius"] + enemy.radius
                    distance = math.hypot(shot["x"] - enemy.x, shot["y"] - enemy.y)
                    
                    if distance < collision_distance:
                        # Apply PURE JOULE damage
                        damage_joules = shot["joule_damage"]
                        
                        print(f"Player shot hits enemy: {damage_joules:.0f} J kinetic damage")
                        was_killed = enemy.take_damage(damage_joules, "kinetic")
                        
                        # Visual effects
                        if self.effect_manager:
                            self.effect_manager.add_impact_spark(shot["x"], shot["y"])
                            self.effect_manager.add_floating_text(
                                enemy.x, enemy.y, f"{damage_joules:.0f}J", was_killed
                            )
                        
                        shot["active"] = False
                        break
            else:
                # Enemy shots vs player - PURE JOULE DAMAGE
                if player_ship and hasattr(player_ship, 'x') and hasattr(player_ship, 'y'):
                    collision_distance = shot["radius"] + player_ship.radius
                    distance = math.hypot(shot["x"] - player_ship.x, shot["y"] - player_ship.y)
                    
                    if distance < collision_distance:
                        # Apply PURE JOULE damage to player
                        damage_joules = shot["joule_damage"]
                        
                        print(f"Enemy shot hits player: {damage_joules:.0f} J kinetic damage")
                        player_ship.take_damage(damage_joules, "kinetic")
                        
                        # Visual effects
                        if self.effect_manager:
                            self.effect_manager.add_impact_spark(shot["x"], shot["y"])
                            self.effect_manager.add_floating_text(
                                player_ship.x, player_ship.y, f"-{damage_joules:.0f}J", False
                            )
                        
                        shot["active"] = False
    
    def _update_energy_beams(self, delta_time, enemies, player_ship):
        """Update energy beam weapons with PURE JOULE damage"""
        for beam in self.energy_beams[:]:
            if not beam["active"]:
                continue
            
            beam["remaining_duration"] -= delta_time
            
            if beam["remaining_duration"] <= 0:
                beam["active"] = False
                continue
            
            # Energy beams do continuous PURE JOULE damage
            beam_start = (beam["start_x"], beam["start_y"])
            beam_end = (beam["end_x"], beam["end_y"])
            
            for enemy in enemies[:]:
                if not hasattr(enemy, 'x') or not hasattr(enemy, 'y') or not enemy.alive:
                    continue
                
                # Check beam intersection
                distance_to_beam = self._point_to_line_distance(
                    (enemy.x, enemy.y), beam_start, beam_end
                )
                
                if distance_to_beam < beam["width"]:
                    # Apply continuous PURE JOULE damage (scaled by delta time)
                    damage_joules_per_second = beam["joule_damage"]
                    damage_this_frame = damage_joules_per_second * delta_time
                    
                    print(f"Energy beam continuous damage: {damage_this_frame:.0f} J this frame")
                    enemy.take_damage(damage_this_frame, "energy")
    
    def _cleanup_projectiles(self):
        """Remove inactive projectiles and those outside screen bounds"""
        self.bombs = [bomb for bomb in self.bombs if bomb["active"] and self._is_in_bounds(bomb)]
        self.kinetic_shots = [shot for shot in self.kinetic_shots if shot["active"] and self._is_in_bounds(shot)]
        self.energy_beams = [beam for beam in self.energy_beams if beam["active"]]
    
    def _is_in_bounds(self, projectile):
        """Check if projectile is within screen bounds (with margin)"""
        margin = self.cleanup_margin
        return (-margin <= projectile["x"] <= self.screen_width + margin and 
                -margin <= projectile["y"] <= self.screen_height + margin)
    
    def _calculate_explosion_size(self, warhead_data):
        """Calculate visual explosion size based on warhead"""
        explosive_kg = warhead_data.get("explosive_kg", 0.5)
        size_multiplier = math.log(explosive_kg + 1) * 0.5
        return 1.0 * (1 + size_multiplier)
    
    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return math.hypot(px - closest_x, py - closest_y)
    
    def draw(self, screen):
        """Render all projectiles with 0.6% screen scaling"""
        # Draw bombs - scaled size
        for bomb in self.bombs:
            if bomb["active"]:
                pygame.draw.circle(screen, (255, 255, 0), (int(bomb["x"]), int(bomb["y"])), bomb["radius"])
                
                # Draw proximity fuse indicator - scaled
                pygame.draw.circle(screen, (255, 255, 100), 
                                 (int(bomb["x"]), int(bomb["y"])), 
                                 bomb["proximity_radius"], 1)
        
        # Draw kinetic shots - scaled size
        for shot in self.kinetic_shots:
            if shot["active"]:
                color = (0, 255, 255) if shot["is_player_shot"] else (255, 100, 100)
                pygame.draw.circle(screen, color, (int(shot["x"]), int(shot["y"])), shot["radius"])
        
        # Draw energy beams - scaled width
        for beam in self.energy_beams:
            if beam["active"]:
                alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.01))
                beam_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                
                pygame.draw.line(beam_surface, (255, 0, 255, alpha), 
                               (beam["start_x"], beam["start_y"]), 
                               (beam["end_x"], beam["end_y"]), beam["width"])
                
                screen.blit(beam_surface, (0, 0))
    
    def get_projectile_count(self):
        """Get total number of active projectiles"""
        return len([p for p in self.bombs if p["active"]]) + \
               len([p for p in self.kinetic_shots if p["active"]]) + \
               len([p for p in self.energy_beams if p["active"]])
    
    def clear_all_projectiles(self):
        """Clear all projectiles (for scene transitions)"""
        self.bombs.clear()
        self.kinetic_shots.clear()
        self.energy_beams.clear()