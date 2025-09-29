#!/usr/bin/env python3
import pygame
import math
import random

class Explosion:
    """Individual explosion effect"""
    
    def __init__(self, x, y, size=1.0, duration=0.8, explosion_type="standard"):
        self.x = x
        self.y = y
        self.base_size = size
        self.max_duration = duration
        self.remaining_duration = duration
        self.explosion_type = explosion_type
        
        # Visual properties
        self.current_radius = 0
        self.max_radius = int(30 * size)
        self.rings = []
        self.particles = []
        
        # Create explosion rings
        ring_count = max(3, int(4 * size))
        for i in range(ring_count):
            ring = {
                "radius": 0,
                "max_radius": self.max_radius * (0.7 + i * 0.3),
                "color": self._get_ring_color(i),
                "thickness": max(1, int(3 * size)),
                "delay": i * 0.05  # Stagger ring expansion
            }
            self.rings.append(ring)
        
        # Create particles for debris effect
        particle_count = int(15 * size)
        for _ in range(particle_count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(20, 80) * size
            particle = {
                "x": x,
                "y": y,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "size": random.uniform(1, 3) * size,
                "color": self._get_particle_color(),
                "life": random.uniform(0.3, 0.8)
            }
            self.particles.append(particle)
    
    def _get_ring_color(self, ring_index):
        """Get color for explosion ring based on type"""
        if self.explosion_type == "standard":
            colors = [(255, 255, 255), (255, 255, 100), (255, 150, 50), (200, 100, 100)]
        elif self.explosion_type == "energy":
            colors = [(255, 255, 255), (100, 255, 255), (50, 150, 255), (100, 100, 200)]
        elif self.explosion_type == "large":
            colors = [(255, 255, 255), (255, 200, 100), (255, 100, 50), (255, 50, 50)]
        else:
            colors = [(255, 255, 255), (200, 200, 200), (150, 150, 150), (100, 100, 100)]
        
        return colors[min(ring_index, len(colors) - 1)]
    
    def _get_particle_color(self):
        """Get random particle color"""
        colors = [
            (255, 255, 100), (255, 150, 50), (255, 100, 100), 
            (200, 200, 200), (255, 255, 255)
        ]
        return random.choice(colors)
    
    def update(self, delta_time):
        """Update explosion animation"""
        if self.remaining_duration <= 0:
            return False
        
        self.remaining_duration -= delta_time
        progress = 1.0 - (self.remaining_duration / self.max_duration)
        
        # Update rings
        for ring in self.rings:
            if progress >= ring["delay"]:
                ring_progress = min(1.0, (progress - ring["delay"]) / (1.0 - ring["delay"]))
                ring["radius"] = ring["max_radius"] * ring_progress
        
        # Update particles
        for particle in self.particles[:]:
            particle["x"] += particle["vx"] * delta_time
            particle["y"] += particle["vy"] * delta_time
            particle["vy"] += 50 * delta_time  # Gravity
            particle["vx"] *= 0.98  # Air resistance
            particle["life"] -= delta_time
            
            if particle["life"] <= 0:
                self.particles.remove(particle)
        
        return self.remaining_duration > 0
    
    def draw(self, screen):
        """Draw explosion effect"""
        if self.remaining_duration <= 0:
            return
        
        progress = 1.0 - (self.remaining_duration / self.max_duration)
        alpha = int(255 * (1.0 - progress) * 0.8)
        
        # Draw rings
        for ring in self.rings:
            if ring["radius"] > 0:
                # Create surface with alpha for ring
                ring_surface = pygame.Surface((ring["radius"] * 2 + 20, ring["radius"] * 2 + 20), pygame.SRCALPHA)
                ring_color = (*ring["color"], alpha)
                
                if ring["radius"] > ring["thickness"]:
                    pygame.draw.circle(ring_surface, ring_color, 
                                     (ring["radius"] + 10, ring["radius"] + 10), 
                                     int(ring["radius"]), ring["thickness"])
                else:
                    pygame.draw.circle(ring_surface, ring_color, 
                                     (ring["radius"] + 10, ring["radius"] + 10), 
                                     int(ring["radius"]))
                
                screen.blit(ring_surface, (self.x - ring["radius"] - 10, self.y - ring["radius"] - 10))
        
        # Draw particles
        for particle in self.particles:
            if particle["life"] > 0:
                particle_alpha = int(255 * (particle["life"] / 0.8))
                particle_color = (*particle["color"], particle_alpha)
                
                # Draw particle as small circle
                particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(particle_surface, particle_color, (3, 3), int(particle["size"]))
                screen.blit(particle_surface, (particle["x"] - 3, particle["y"] - 3))


class MuzzleFlash:
    """Muzzle flash effect for weapon firing"""
    
    def __init__(self, x, y, angle=0, size=1.0, flash_type="standard"):
        self.x = x
        self.y = y
        self.angle = angle
        self.size = size
        self.flash_type = flash_type
        self.duration = 0.1  # Very brief flash
        self.remaining_duration = self.duration
        
        # Flash properties
        self.length = int(20 * size)
        self.width = int(8 * size)
        self.sparks = []
        
        # Create sparks
        spark_count = int(5 * size)
        for _ in range(spark_count):
            spark_angle = angle + random.uniform(-0.5, 0.5)
            spark_speed = random.uniform(50, 150) * size
            spark = {
                "x": x,
                "y": y,
                "vx": math.cos(spark_angle) * spark_speed,
                "vy": math.sin(spark_angle) * spark_speed,
                "life": random.uniform(0.05, 0.15),
                "color": self._get_spark_color()
            }
            self.sparks.append(spark)
    
    def _get_spark_color(self):
        """Get random spark color"""
        colors = [(255, 255, 100), (255, 200, 50), (255, 150, 100), (255, 255, 255)]
        return random.choice(colors)
    
    def update(self, delta_time):
        """Update muzzle flash"""
        if self.remaining_duration <= 0:
            return False
        
        self.remaining_duration -= delta_time
        
        # Update sparks
        for spark in self.sparks[:]:
            spark["x"] += spark["vx"] * delta_time
            spark["y"] += spark["vy"] * delta_time
            spark["life"] -= delta_time
            
            if spark["life"] <= 0:
                self.sparks.remove(spark)
        
        return self.remaining_duration > 0
    
    def draw(self, screen):
        """Draw muzzle flash"""
        if self.remaining_duration <= 0:
            return
        
        progress = 1.0 - (self.remaining_duration / self.duration)
        alpha = int(255 * (1.0 - progress))
        
        # Main flash cone
        flash_color = (255, 255, 100, alpha)
        flash_surface = pygame.Surface((self.length * 2, self.width * 2), pygame.SRCALPHA)
        
        # Draw flash as elongated ellipse
        flash_rect = (0, self.width - self.width // 2, self.length, self.width)
        pygame.draw.ellipse(flash_surface, flash_color, flash_rect)
        
        # Rotate and position flash
        rotated_flash = pygame.transform.rotate(flash_surface, -math.degrees(self.angle))
        flash_rect = rotated_flash.get_rect(center=(self.x, self.y))
        screen.blit(rotated_flash, flash_rect)
        
        # Draw sparks
        for spark in self.sparks:
            if spark["life"] > 0:
                spark_alpha = int(255 * (spark["life"] / 0.15))
                spark_color = (*spark["color"], spark_alpha)
                
                spark_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(spark_surface, spark_color, (2, 2), 2)
                screen.blit(spark_surface, (spark["x"] - 2, spark["y"] - 2))


class FloatingText:
    """Floating damage/text numbers"""
    
    def __init__(self, x, y, text, color=(255, 255, 255), size=24, is_critical=False):
        self.x = x
        self.y = y
        self.start_y = y
        self.text = text
        self.color = color
        self.size = size
        self.is_critical = is_critical
        self.duration = 1.5 if is_critical else 1.0
        self.remaining_duration = self.duration
        
        # Movement
        self.vx = random.uniform(-20, 20)
        self.vy = -30 if is_critical else -20
        
        # Create text surface
        font_size = int(size * 1.5) if is_critical else size
        self.font = pygame.font.Font(None, font_size)
        self.surface = self.font.render(str(text), True, color)
        
        if is_critical:
            # Add outline for critical hits
            outline_surface = self.font.render(str(text), True, (0, 0, 0))
            temp_surface = pygame.Surface((self.surface.get_width() + 4, self.surface.get_height() + 4), pygame.SRCALPHA)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx != 0 or dy != 0:
                        temp_surface.blit(outline_surface, (dx + 2, dy + 2))
            temp_surface.blit(self.surface, (2, 2))
            self.surface = temp_surface
    
    def update(self, delta_time):
        """Update floating text"""
        if self.remaining_duration <= 0:
            return False
        
        self.remaining_duration -= delta_time
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Slow down movement over time
        self.vx *= 0.95
        self.vy *= 0.95
        
        return self.remaining_duration > 0
    
    def draw(self, screen):
        """Draw floating text"""
        if self.remaining_duration <= 0:
            return
        
        progress = 1.0 - (self.remaining_duration / self.duration)
        alpha = int(255 * (1.0 - progress))
        
        # Fade out text
        text_surface = self.surface.copy()
        text_surface.set_alpha(alpha)
        
        rect = text_surface.get_rect(center=(self.x, self.y))
        screen.blit(text_surface, rect)


class ScreenShake:
    """Screen shake effect for impacts"""
    
    def __init__(self, duration=0.3, intensity=5.0):
        self.duration = duration
        self.remaining_duration = duration
        self.intensity = intensity
        self.offset_x = 0
        self.offset_y = 0
    
    def update(self, delta_time):
        """Update screen shake"""
        if self.remaining_duration <= 0:
            self.offset_x = 0
            self.offset_y = 0
            return False
        
        self.remaining_duration -= delta_time
        
        # Calculate shake intensity (decreases over time)
        progress = 1.0 - (self.remaining_duration / self.duration)
        current_intensity = self.intensity * (1.0 - progress)
        
        # Random offset
        self.offset_x = random.uniform(-current_intensity, current_intensity)
        self.offset_y = random.uniform(-current_intensity, current_intensity)
        
        return self.remaining_duration > 0
    
    def get_offset(self):
        """Get current shake offset"""
        return (self.offset_x, self.offset_y)


class EffectManager:
    """Manages all visual effects"""
    
    def __init__(self):
        # Effect containers
        self.explosions = []
        self.muzzle_flashes = []
        self.floating_texts = []
        self.screen_shakes = []
        
        # Effect counters for performance monitoring
        self.effect_counts = {
            "explosions": 0,
            "muzzle_flashes": 0,
            "floating_texts": 0,
            "screen_shakes": 0
        }
        
        print("EffectManager initialized")
    
    def add_explosion(self, x, y, size=1.0, duration=0.8, explosion_type="standard"):
        """Add explosion effect"""
        explosion = Explosion(x, y, size, duration, explosion_type)
        self.explosions.append(explosion)
        self.effect_counts["explosions"] += 1
        return explosion
    
    def add_muzzle_flash(self, x, y, angle=0, size=1.0, flash_type="standard"):
        """Add muzzle flash effect"""
        flash = MuzzleFlash(x, y, angle, size, flash_type)
        self.muzzle_flashes.append(flash)
        self.effect_counts["muzzle_flashes"] += 1
        return flash
    
    def add_floating_text(self, x, y, text, is_critical=False, color=None):
        """Add floating damage text"""
        if color is None:
            color = (255, 255, 0) if is_critical else (255, 255, 255)
        
        floating_text = FloatingText(x, y, text, color, 24, is_critical)
        self.floating_texts.append(floating_text)
        self.effect_counts["floating_texts"] += 1
        return floating_text
    
    def add_screen_shake(self, duration=0.3, intensity=5.0):
        """Add screen shake effect"""
        shake = ScreenShake(duration, intensity)
        self.screen_shakes.append(shake)
        self.effect_counts["screen_shakes"] += 1
        return shake
    
    def add_impact_spark(self, x, y, angle=0):
        """Add impact sparks for projectile hits"""
        return self.add_muzzle_flash(x, y, angle + math.pi, 0.5, "impact")
    
    def add_energy_charge(self, x, y, duration=1.0):
        """Add energy charging effect"""
        return self.add_explosion(x, y, 0.5, duration, "energy")
    
    def update(self, delta_time):
        """Update all effects"""
        # Update explosions
        self.explosions = [exp for exp in self.explosions if exp.update(delta_time)]
        
        # Update muzzle flashes
        self.muzzle_flashes = [flash for flash in self.muzzle_flashes if flash.update(delta_time)]
        
        # Update floating texts
        self.floating_texts = [text for text in self.floating_texts if text.update(delta_time)]
        
        # Update screen shakes
        self.screen_shakes = [shake for shake in self.screen_shakes if shake.update(delta_time)]
    
    def draw(self, screen):
        """Draw all effects"""
        # Apply screen shake if active
        shake_offset = (0, 0)
        if self.screen_shakes:
            # Combine all active screen shakes
            total_x, total_y = 0, 0
            for shake in self.screen_shakes:
                offset_x, offset_y = shake.get_offset()
                total_x += offset_x
                total_y += offset_y
            shake_offset = (total_x, total_y)
        
        # Create temporary surface for shake effect
        if shake_offset != (0, 0):
            # For now, we'll skip the shake surface implementation
            # and just draw effects with offset positions
            pass
        
        # Draw explosions (back to front)
        for explosion in self.explosions:
            explosion.draw(screen)
        
        # Draw muzzle flashes
        for flash in self.muzzle_flashes:
            flash.draw(screen)
        
        # Draw floating texts (on top)
        for text in self.floating_texts:
            text.draw(screen)
    
    def clear_all_effects(self):
        """Clear all effects (for scene transitions)"""
        self.explosions.clear()
        self.muzzle_flashes.clear()
        self.floating_texts.clear()
        self.screen_shakes.clear()
        
        # Reset counters
        for key in self.effect_counts:
            self.effect_counts[key] = 0
    
    def get_effect_count(self):
        """Get total number of active effects"""
        return (len(self.explosions) + len(self.muzzle_flashes) + 
                len(self.floating_texts) + len(self.screen_shakes))
    
    def get_performance_info(self):
        """Get performance information about effects"""
        return {
            "active_explosions": len(self.explosions),
            "active_flashes": len(self.muzzle_flashes),
            "active_texts": len(self.floating_texts),
            "active_shakes": len(self.screen_shakes),
            "total_active": self.get_effect_count(),
            "lifetime_counts": self.effect_counts.copy()
        }
