#!/usr/bin/env python3
import pygame
import sys
from enum import Enum
import math
import random

# Complete RPG System Integration
class RPGBombSystem:
    def __init__(self):
        self.base_explosive_kg = {1: 0.5, 2: 0.8, 3: 1.2, 4: 1.8, 5: 2.5, 6: 3.5, 7: 4.8, 8: 6.5, 9: 8.5, 10: 11.0, 11: 14.0, 12: 18.0, 13: 23.0}
        self.ENERGY_PER_KG = 4184000
        self.base_cooldown = 4.0
        self.breach_bomb_multiplier = 5
    
    def get_bomb_energy(self, level):
        explosive_kg = self.base_explosive_kg.get(level, 0.5)
        return explosive_kg * self.ENERGY_PER_KG
    
    def calculate_bomb_damage(self, level, use_breach_bomb=False):
        energy_per_bomb = self.get_bomb_energy(level)
        num_bombs = self.breach_bomb_multiplier if use_breach_bomb else 1
        return {
            'total_damage': energy_per_bomb * num_bombs,
            'energy_per_bomb': energy_per_bomb,
            'num_bombs': num_bombs
        }

class InventorySystem:
    def __init__(self):
        self.kerr_scrap = 0
        self.rare_metals = 0
        self.energy_cores = 0
        self.visible = False
        print("Inventory system initialized")
    
    def add_item(self, item_type, amount=1):
        if hasattr(self, item_type):
            current = getattr(self, item_type)
            setattr(self, item_type, current + amount)
            print(f"Added {amount} {item_type}, total: {current + amount}")
            return True
        return False
    
    def toggle_visibility(self):
        self.visible = not self.visible
        print(f"Inventory {'OPENED' if self.visible else 'CLOSED'}")
        return self.visible

class DropSystem:
    def __init__(self, inventory):
        self.inventory = inventory
    
    def award_drops(self, enemy_type, enemy_level):
        if random.random() < 0.4:  # 40% drop chance
            amount = 1 + enemy_level
            self.inventory.add_item('kerr_scrap', amount)
            return [{'type': 'kerr_scrap', 'amount': amount}]
        return []

class ProgressionIntegrator:
    def __init__(self):
        self.rpg_bombs = RPGBombSystem()
        self.inventory = InventorySystem()
        self.drop_system = DropSystem(self.inventory)
        
        self.player_level = 1
        self.experience = 0
        self.stat_points = 0
        self.attack = 1
        self.defense = 1
        self.evasion = 1
        self.shield = 1
        
        self.show_level_up = False
        self.level_up_timer = 0
        self.show_stat_allocation = False
        
        print("ProgressionIntegrator initialized")
    
    def get_bomb_level(self):
        return min(13, self.attack)
    
    def handle_input(self, key):
        print(f"ProgressionIntegrator.handle_input called with key: {pygame.key.name(key)}")
        
        if key == pygame.K_i:
            print("Handling inventory key in progression system")
            result = self.inventory.toggle_visibility()
            print(f"Inventory toggle returned: {result}")
            return True
        
        if key == pygame.K_c and self.stat_points > 0:
            self.show_stat_allocation = not self.show_stat_allocation
            return True
        
        if self.show_stat_allocation:
            if key == pygame.K_1:
                return self.allocate_stat_point("attack")
            elif key == pygame.K_2:
                return self.allocate_stat_point("defense")
            elif key == pygame.K_3:
                return self.allocate_stat_point("evasion")
            elif key == pygame.K_4:
                return self.allocate_stat_point("shield")
        
        return False
    
    def allocate_stat_point(self, stat_name):
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
        
        self.stat_points -= 1
        print(f"Allocated point to {stat_name}. Remaining: {self.stat_points}")
        return True
    
    def on_enemy_killed(self, enemy_type, enemy_level):
        exp_gained = 10 + enemy_level * 3
        self.experience += exp_gained
        
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
        
        drops = self.drop_system.award_drops(enemy_type, enemy_level)
        
        return {
            'exp_gained': exp_gained,
            'leveled_up': leveled_up,
            'drops': drops
        }
    
    def fire_breach_bomb(self, projectile_manager, ship_pos):
        bomb_level = self.get_bomb_level()
        bomb_data = self.rpg_bombs.calculate_bomb_damage(bomb_level, use_breach_bomb=True)
        
        angles = [-math.pi/2 - math.pi/12, -math.pi/2 - math.pi/24, -math.pi/2, 
                  -math.pi/2 + math.pi/24, -math.pi/2 + math.pi/12]
        
        for angle in angles:
            explosive_kg = bomb_data['energy_per_bomb'] / self.rpg_bombs.ENERGY_PER_KG
            
            bomb_stats = {
                "min_damage": int(bomb_data['energy_per_bomb'] * 0.8),
                "max_damage": int(bomb_data['energy_per_bomb'] * 1.2),
                "mass_kg": max(1.0, explosive_kg * 3),
                "velocity_kmh": 800,
                "diameter_mm": 75 + bomb_level * 5,
                "length_mm": 300 + bomb_level * 20,
                "shrapnel_kg": explosive_kg * 2
            }
            
            velocity_ms = 800 * 1000 / 3600
            vx = math.cos(angle) * velocity_ms
            vy = math.sin(angle) * velocity_ms
            
            projectile_manager.add_bomb(
                ship_pos[0], ship_pos[1] - 25,
                vx, vy,
                bomb_stats,
                f"breach_bomb_{random.randint(1000, 9999)}"
            )
        
        return self.rpg_bombs.base_cooldown
    
    def update(self, delta_time):
        if self.level_up_timer > 0:
            self.level_up_timer -= delta_time
            if self.level_up_timer <= 0:
                self.show_level_up = False
                if self.stat_points > 0:
                    self.show_stat_allocation = True
    
    def get_ui_data(self):
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
                'bomb_level': self.get_bomb_level(),
                'show_level_up': self.show_level_up,
                'show_stat_allocation': self.show_stat_allocation
            },
            'inventory': {
                'visible': self.inventory.visible,
                'resources': {
                    'kerr_scrap': self.inventory.kerr_scrap,
                    'rare_metals': self.inventory.rare_metals,
                    'energy_cores': self.inventory.energy_cores
                }
            }
        }

class InventoryUI:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def draw_inventory(self, screen, inventory_data, player_data):
        if not inventory_data['visible']:
            return
        
        # Semi-transparent background
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Main panel
        panel_width = 800
        panel_height = 600
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 80), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (100, 100, 200), (panel_x, panel_y, panel_width, panel_height), 3)
        
        # Title
        title = self.font_large.render("INVENTORY & STATS", True, (255, 255, 100))
        title_rect = title.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        screen.blit(title, title_rect)
        
        # Player info
        y_offset = panel_y + 100
        info_lines = [
            f"Level: {player_data['level']} (Bomb Level: {player_data['bomb_level']})",
            f"Attack: {player_data['attack']} | Defense: {player_data['defense']} | Evasion: {player_data['evasion']} | Shield: {player_data['shield']}",
            f"Stat Points Available: {player_data['stat_points']}",
            "",
            "RESOURCES:",
            f"Kerr Scrap: {inventory_data['resources']['kerr_scrap']}",
            f"Rare Metals: {inventory_data['resources']['rare_metals']}",
            f"Energy Cores: {inventory_data['resources']['energy_cores']}",
            "",
            "CONTROLS:",
            "I - Close Inventory",
            "C - Stat Allocation (if points available)",
            "1-4 - Allocate stat points (Attack/Defense/Evasion/Shield)"
        ]
        
        for line in info_lines:
            if line:
                color = (255, 255, 100) if "Stat Points" in line and player_data['stat_points'] > 0 else (255, 255, 255)
                if line == "RESOURCES:" or line == "CONTROLS:":
                    color = (100, 255, 100)
                
                text = self.font_small.render(line, True, color)
                screen.blit(text, (panel_x + 30, y_offset))
            y_offset += 30
    
    def draw_level_up_notification(self, screen, player_data):
        if not player_data.get('show_level_up', False):
            return
        
        panel_width = 500
        panel_height = 150
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
        alpha = int(200 + 50 * pulse)
        
        pygame.draw.rect(screen, (255, 255, 0, alpha), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height), 4)
        
        level_text = f"LEVEL UP! Now Level {player_data['level']}"
        level_surface = self.font_large.render(level_text, True, (0, 0, 0))
        level_rect = level_surface.get_rect(center=(panel_x + panel_width//2, panel_y + 60))
        screen.blit(level_surface, level_rect)
        
        if player_data['stat_points'] > 0:
            points_text = f"You have {player_data['stat_points']} stat points! Press C"
            points_surface = self.font_medium.render(points_text, True, (0, 0, 0))
            points_rect = points_surface.get_rect(center=(panel_x + panel_width//2, panel_y + 100))
            screen.blit(points_surface, points_rect)
    
    def draw_stat_allocation(self, screen, player_data):
        if not player_data.get('show_stat_allocation', False):
            return
        
        panel_width = 600
        panel_height = 400
        panel_x = (self.screen_width - panel_width) // 2
        panel_y = (self.screen_height - panel_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 80, 220), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, (255, 255, 100), (panel_x, panel_y, panel_width, panel_height), 3)
        
        title = f"ALLOCATE STAT POINTS ({player_data['stat_points']} available)"
        title_surface = self.font_large.render(title, True, (255, 255, 100))
        title_rect = title_surface.get_rect(center=(panel_x + panel_width//2, panel_y + 40))
        screen.blit(title_surface, title_rect)
        
        y_offset = panel_y + 100
        stats = [
            ("1", "ATTACK", player_data['attack'], f"Bomb Level: {player_data['bomb_level']} → {min(13, player_data['attack'] + 1)}"),
            ("2", "DEFENSE", player_data['defense'], f"Damage Resist: {(player_data['defense']-1)*5:.0f}% → {player_data['defense']*5:.0f}%"),
            ("3", "EVASION", player_data['evasion'], f"Dodge: {(player_data['evasion']-1)*3:.0f}% → {player_data['evasion']*3:.0f}%"),
            ("4", "SHIELD", player_data['shield'], f"Capacity: +{(player_data['shield']-1)*500:.0f}J → +{player_data['shield']*500:.0f}J")
        ]
        
        for key, name, current, effect in stats:
            key_text = f"[{key}] {name}: {current}"
            key_surface = self.font_medium.render(key_text, True, (255, 255, 255))
            screen.blit(key_surface, (panel_x + 50, y_offset))
            
            effect_surface = self.font_small.render(effect, True, (200, 200, 200))
            screen.blit(effect_surface, (panel_x + 70, y_offset + 25))
            
            y_offset += 60
        
        control_text = "Press 1-4 to allocate points | C to close"
        control_surface = self.font_small.render(control_text, True, (200, 200, 200))
        screen.blit(control_surface, (panel_x + 50, panel_y + panel_height - 40))

# Import existing systems
from weapons_database import WeaponsDatabase
from breacher_ship import BreacherShip
from effect_manager import EffectManager
from universal_cannon import add_universal_cannon_to_ship, CannonManager
from projectile_manager import ProjectileManager
from enemy_manager import EnemyManager
from hud_renderer import HUDRenderer

class GameState(Enum):
    MAIN_MENU = "main_menu"
    GAME_PLAYING = "game_playing"
    GAME_PAUSED = "game_paused"
    GAME_OVER = "game_over"

class InputManager:
    def __init__(self):
        self.keys_held = set()
        self.projectile_manager = None
        self.effect_manager = None
        self.progression_manager = None
        print("InputManager initialized")
    
    def set_managers(self, projectile_manager, effect_manager, progression_manager=None):
        self.projectile_manager = projectile_manager
        self.effect_manager = effect_manager
        self.progression_manager = progression_manager
        print(f"InputManager.set_managers called - progression_manager: {progression_manager is not None}")
    
    def handle_event(self, event, player_ship):
        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event, player_ship)
        elif event.type == pygame.KEYUP:
            self.keys_held.discard(event.key)
    
    def _handle_key_down(self, event, player_ship):
        key = event.key
        self.keys_held.add(key)
        
        print(f"Key pressed: {pygame.key.name(key)}")
        
        # CRITICAL: Progression system first
        if self.progression_manager:
            print("Calling progression_manager.handle_input")
            if self.progression_manager.handle_input(key):
                print("Progression system handled the key")
                return
        else:
            print("ERROR: No progression_manager in InputManager!")
        
        # Weapon handling
        if key == pygame.K_LCTRL:
            self._fire_universal_cannon(player_ship)
        elif key == pygame.K_SPACE:
            self._fire_breach_bomb_rpg(player_ship)
        elif key == pygame.K_q:
            self._fire_special_weapon(player_ship, "cluster_strike")
        elif key == pygame.K_z:
            self._fire_special_weapon(player_ship, "overcharge_warheads")
    
    def _fire_universal_cannon(self, player_ship):
        if self.projectile_manager:
            success = player_ship.fire_universal_cannon(self.projectile_manager)
            if success and self.effect_manager:
                self.effect_manager.add_muzzle_flash(player_ship.x, player_ship.y - 20)
    
    def _fire_breach_bomb_rpg(self, player_ship):
        if not self.projectile_manager or not self.progression_manager:
            print("Missing managers for RPG breach bomb")
            return
        
        if "breach_bomb" in player_ship.cooldowns:
            print(f"Breach bomb on cooldown: {player_ship.cooldowns['breach_bomb']:.1f}s")
            return
        
        try:
            cooldown = self.progression_manager.fire_breach_bomb(
                self.projectile_manager,
                (player_ship.x, player_ship.y)
            )
            
            player_ship.cooldowns["breach_bomb"] = cooldown
            
            if self.effect_manager:
                self.effect_manager.add_muzzle_flash(player_ship.x, player_ship.y - 25, size=2.0)
                self.effect_manager.add_screen_shake(0.3, 8.0)
            
            bomb_level = self.progression_manager.get_bomb_level()
            print(f"Fired RPG Breach_Bomb: Level {bomb_level}, 5 bombs")
            
        except Exception as e:
            print(f"Error firing RPG breach bomb: {e}")
    
    def _fire_special_weapon(self, player_ship, ability_name):
        if self.projectile_manager and ability_name in player_ship.get_special_abilities():
            success = player_ship.fire_special_weapon(ability_name, self.projectile_manager)
            if success and self.effect_manager:
                if ability_name == "cluster_strike":
                    for i in range(-3, 4):
                        self.effect_manager.add_muzzle_flash(
                            player_ship.x + i * 40, player_ship.y - 25, size=0.8
                        )
                elif ability_name == "overcharge_warheads":
                    self.effect_manager.add_energy_charge(player_ship.x, player_ship.y, duration=1.0)
    
    def on_enemy_killed(self, enemy_level, enemy_type):
        if self.progression_manager:
            return self.progression_manager.on_enemy_killed(enemy_type, enemy_level)
        return None
    
    def update(self, delta_time):
        if self.progression_manager:
            self.progression_manager.update(delta_time)

class GameDirector:
    def __init__(self):
        pygame.init()
        
        self.screen = pygame.display.set_mode((3840, 2160), pygame.FULLSCREEN)
        pygame.display.set_caption("MarsDefense - RPG Working")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_state = GameState.MAIN_MENU
        
        # Systems
        self.input_manager = None
        self.projectile_manager = None
        self.cannon_manager = None
        self.enemy_manager = None
        self.effect_manager = None
        self.hud_renderer = None
        self.progression_manager = None
        self.inventory_ui = None
        
        self.player_ship = None
        self.current_wave = 1
        self.game_start_time = 0
        
        self.delta_time = 0.0
        self.last_frame_time = pygame.time.get_ticks()
        
        self.wave_completion_timer = 0
        self.show_controls = False
        
        print("GameDirector initialized")
    
    def run(self):
        while self.running:
            self._update_delta_time()
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(60)
        
        self._cleanup()
    
    def _update_delta_time(self):
        current_time = pygame.time.get_ticks()
        self.delta_time = (current_time - self.last_frame_time) / 1000.0
        self.last_frame_time = current_time
    
    def _handle_events(self):
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.current_state == GameState.GAME_PLAYING:
                    self.current_state = GameState.GAME_PAUSED
                elif self.current_state == GameState.GAME_PAUSED:
                    self.current_state = GameState.GAME_PLAYING
                elif self.current_state == GameState.GAME_OVER:
                    self.end_current_run()
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
                self.show_controls = not self.show_controls
            
            if self.current_state == GameState.MAIN_MENU:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.start_new_game("Breacher")
            elif self.current_state == GameState.GAME_PLAYING:
                if self.input_manager and self.player_ship:
                    self.input_manager.handle_event(event, self.player_ship)
    
    def _update(self):
        if self.current_state == GameState.GAME_PLAYING:
            self._update_game()
    
    def _update_game(self):
        if not self.player_ship:
            return
        
        keys_pressed = pygame.key.get_pressed()
        
        if self.input_manager:
            self.input_manager.update(self.delta_time)
        
        self.player_ship.update(self.delta_time, keys_pressed)
        if hasattr(self.player_ship, 'update_cannon'):
            self.player_ship.update_cannon(self.delta_time)
        
        living_enemies = []
        if self.enemy_manager:
            self.enemy_manager.update(self.delta_time, self.player_ship)
            living_enemies = [enemy for enemy in self.enemy_manager.enemies if enemy.alive]
        
        if self.projectile_manager:
            if self.effect_manager and not hasattr(self.projectile_manager, 'effect_manager_set'):
                self.projectile_manager.set_effect_manager(self.effect_manager)
                self.projectile_manager.effect_manager_set = True
            
            self.projectile_manager.update(self.delta_time, living_enemies, self.player_ship)
        
        if self.cannon_manager:
            self.cannon_manager.update(self.delta_time, living_enemies, self.player_ship,
                                     self.screen.get_width(), self.screen.get_height())
        
        if self.effect_manager:
            self.effect_manager.update(self.delta_time)
        
        if self.hud_renderer:
            self.hud_renderer.update(self.delta_time)
        
        self._update_wave_progression()
        self._check_game_conditions()
    
    def _update_wave_progression(self):
        if self.enemy_manager and self.enemy_manager.is_wave_complete():
            self.wave_completion_timer += self.delta_time
            if self.wave_completion_timer >= 3.0:
                self._start_next_wave()
    
    def _render(self):
        self.screen.fill((0, 0, 0))
        
        if self.current_state == GameState.MAIN_MENU:
            self._render_main_menu()
        elif self.current_state == GameState.GAME_PLAYING:
            self._render_game()
        elif self.current_state == GameState.GAME_PAUSED:
            self._render_game()
            self._render_pause_overlay()
        elif self.current_state == GameState.GAME_OVER:
            self._render_game_over()
        
        pygame.display.flip()
    
    def _render_game(self):
        if self.player_ship:
            self.player_ship.draw(self.screen)
            if hasattr(self.player_ship, 'draw_cannon_effects'):
                self.player_ship.draw_cannon_effects(self.screen, self.effect_manager)
        
        if self.enemy_manager:
            self.enemy_manager.draw(self.screen)
        
        if self.projectile_manager:
            self.projectile_manager.draw(self.screen)
        
        if self.cannon_manager:
            self.cannon_manager.draw(self.screen)
        
        if self.effect_manager:
            self.effect_manager.draw(self.screen)
        
        if self.hud_renderer:
            self.hud_renderer.draw(self.screen, self.player_ship, self.current_wave,
                                 self.enemy_manager, self.projectile_manager)
        
        # RPG UI
        if self.progression_manager and self.inventory_ui:
            ui_data = self.progression_manager.get_ui_data()
            
            self.inventory_ui.draw_level_up_notification(self.screen, ui_data['player'])
            self.inventory_ui.draw_inventory(self.screen, ui_data['inventory'], ui_data['player'])
            self.inventory_ui.draw_stat_allocation(self.screen, ui_data['player'])
        
        if self.enemy_manager and self.enemy_manager.is_wave_complete() and self.wave_completion_timer > 0:
            remaining_time = max(0, 3.0 - self.wave_completion_timer)
            if self.hud_renderer:
                self.hud_renderer.draw_wave_complete(self.screen, self.current_wave, remaining_time)
        
        if self.show_controls and self.hud_renderer:
            self.hud_renderer.draw_controls_help(self.screen)
    
    def _render_main_menu(self):
        font = pygame.font.Font(None, 72)
        title = font.render("MarsDefense - RPG Working Edition", True, (255, 255, 255))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 400))
        
        menu_font = pygame.font.Font(None, 48)
        instructions = [
            "Press ENTER to start with Breacher ship",
            "I - Inventory | C - Stats | Space - Breach Bomb (5 bombs)",
            "Attack stat = Bomb level | Enemies drop Kerr Scrap",
            "F1 - Controls | ESC - Exit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = menu_font.render(instruction, True, (255, 255, 255))
            y_pos = 600 + i * 60
            self.screen.blit(text, (self.screen.get_width()//2 - text.get_width()//2, y_pos))
    
    def _render_pause_overlay(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        self.screen.blit(pause_text, (self.screen.get_width()//2 - pause_text.get_width()//2, 800))
    
    def _render_game_over(self):
        if self.hud_renderer:
            survival_time = (pygame.time.get_ticks() - self.game_start_time) / 1000.0
            total_kills = self.enemy_manager.total_enemies_killed if self.enemy_manager else 0
            self.hud_renderer.draw_game_over(self.screen, self.current_wave, total_kills, survival_time)
    
    def start_new_game(self, ship_type):
        print(f"Starting new game with {ship_type} - RPG Working Edition")
        
        # Initialize all systems
        self.input_manager = InputManager()
        self.projectile_manager = ProjectileManager(self.screen.get_width(), self.screen.get_height())
        self.cannon_manager = CannonManager()
        self.enemy_manager = EnemyManager(self.screen.get_width(), self.screen.get_height())
        self.effect_manager = EffectManager()
        self.hud_renderer = HUDRenderer(self.screen.get_width(), self.screen.get_height())
        
        # CRITICAL: Initialize RPG systems
        self.progression_manager = ProgressionIntegrator()
        self.inventory_ui = InventoryUI(self.screen.get_width(), self.screen.get_height())
        
        print(f"Created progression_manager: {self.progression_manager is not None}")
        print(f"Created inventory_ui: {self.inventory_ui is not None}")
        
        # CRITICAL: Connect systems properly
        self.input_manager.set_managers(
            self.projectile_manager,
            self.effect_manager,
            self.progression_manager
        )
        
        # Connect enemy manager to input manager for drops/XP
        self.enemy_manager.set_input_manager(self.input_manager)
        
        # Create player ship
        self.player_ship = self._create_player_ship(ship_type)
        
        # Connect damage flash
        if hasattr(self.player_ship, 'set_hud_renderer'):
            self.player_ship.set_hud_renderer(self.hud_renderer)
        else:
            def trigger_damage_flash():
                if self.hud_renderer:
                    self.hud_renderer.trigger_damage_flash()
            self.player_ship.trigger_damage_flash = trigger_damage_flash
        
        self.game_start_time = pygame.time.get_ticks()
        self.current_state = GameState.GAME_PLAYING
        
        # Start first wave
        self.enemy_manager.start_wave(1)
        
        print("RPG Game started successfully - all systems connected")
    
    def _create_player_ship(self, ship_type):
        if ship_type == "Breacher":
            ship = BreacherShip(self.screen.get_width(), self.screen.get_height())
        else:
            ship = BreacherShip(self.screen.get_width(), self.screen.get_height())
        
        add_universal_cannon_to_ship(type(ship))
        ship.__init__(self.screen.get_width(), self.screen.get_height())
        
        return ship
    
    def end_current_run(self, success=False):
        if not success:
            self.current_state = GameState.GAME_OVER
        else:
            self.current_state = GameState.MAIN_MENU
        
        self.player_ship = None
        self.current_wave = 1
        self.wave_completion_timer = 0
    
    def _check_game_conditions(self):
        if self.player_ship and self.player_ship.is_dead():
            if self.hud_renderer:
                self.hud_renderer.trigger_damage_flash()
            if self.effect_manager:
                self.effect_manager.add_explosion(self.player_ship.x, self.player_ship.y, 2.0, 1.5, "large")
            print(f"Player died! Final HP: {self.player_ship.current_hp}")
            self.end_current_run(success=False)
    
    def _start_next_wave(self):
        self.current_wave += 1
        self.wave_completion_timer = 0
        print(f"Starting wave {self.current_wave}")
        if self.enemy_manager:
            self.enemy_manager.start_wave(self.current_wave)
    
    def _cleanup(self):
        print("Cleaning up...")
        pygame.quit()
        sys.exit()

# Entry point
def main():
    director = GameDirector()
    director.run()

if __name__ == "__main__":
    main()