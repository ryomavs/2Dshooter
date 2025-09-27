#!/usr/bin/env python3
import pygame

class InputManager:
    """Handles all input processing and weapon firing with progression system"""
    
    def __init__(self):
        # Default key bindings
        self.key_bindings = {
            # Universal weapons (all ships)
            "cannon": pygame.K_LCTRL,
            
            # Breacher special abilities  
            "breach_bomb": pygame.K_SPACE,
            "cluster_strike": pygame.K_q,
            "overcharge_warheads": pygame.K_z,
            
            # Future ship abilities (placeholders)
            "energy_beam": pygame.K_e,
            "kinetic_burst": pygame.K_r,
            "missile_volley": pygame.K_f,
            
            # Progression and UI
            "inventory": pygame.K_i,
            "character_sheet": pygame.K_c,
        }
        
        # Key reassignment system
        self.reassign_mode = False
        self.reassign_target = None
        
        # Track held keys for continuous actions
        self.keys_held = set()
        
        # Reference to game systems (will be set by GameDirector)
        self.projectile_manager = None
        self.effect_manager = None
        self.progression_manager = None
    
    def set_managers(self, projectile_manager, effect_manager, progression_manager=None):
        """Set references to game managers"""
        self.projectile_manager = projectile_manager
        self.effect_manager = effect_manager
        self.progression_manager = progression_manager
    
    def handle_event(self, event, player_ship):
        """Handle a single input event"""
        if event.type == pygame.KEYDOWN:
            self._handle_key_down(event, player_ship)
        elif event.type == pygame.KEYUP:
            self._handle_key_up(event, player_ship)
    
    def update(self, delta_time):
        """Update input manager (for continuous actions)"""
        # Update progression manager if available
        if self.progression_manager:
            self.progression_manager.update(delta_time)
    
    def _handle_key_down(self, event, player_ship):
        """Handle key press events"""
        key = event.key
        self.keys_held.add(key)
        
        # Handle key reassignment mode
        if self.reassign_mode:
            self._reassign_key(key)
            return
        
        # Handle progression system input first
        if self.progression_manager:
            if self.progression_manager.handle_input(key):
                return  # Progression system handled the input
        
        # Route weapon commands based on ship type and key bindings
        if key == self.key_bindings["cannon"]:
            self._fire_universal_cannon(player_ship)
        
        elif key == self.key_bindings["breach_bomb"]:
            self._fire_special_weapon(player_ship, "breach_bomb")
        
        elif key == self.key_bindings["cluster_strike"]:
            self._fire_special_weapon(player_ship, "cluster_strike")
        
        elif key == self.key_bindings["overcharge_warheads"]:
            self._fire_special_weapon(player_ship, "overcharge_warheads")
        
        elif key == self.key_bindings["inventory"]:
            self._open_inventory()
        
        # Add other weapon/ability handlers as needed
    
    def _handle_key_up(self, event, player_ship):
        """Handle key release events"""
        key = event.key
        self.keys_held.discard(key)
    
    def _fire_universal_cannon(self, player_ship):
        """Fire the universal cannon available to all ships"""
        if not self.projectile_manager:
            print("Warning: No projectile manager available")
            return
        
        success = player_ship.fire_universal_cannon(self.projectile_manager)
        if success:
            print(f"{player_ship.ship_type} fired universal cannon")
            # Add muzzle flash effect if effect manager available
            if self.effect_manager:
                self.effect_manager.add_muzzle_flash(player_ship.x, player_ship.y - 20)
    
    def _fire_special_weapon(self, player_ship, ability_name):
        """Fire ship-specific special weapons with stat modifiers"""
        if not self.projectile_manager:
            print("Warning: No projectile manager available")
            return
        
        # Check if ship supports this ability
        if ability_name not in player_ship.get_special_abilities():
            print(f"{player_ship.ship_type} does not support {ability_name}")
            return
        
        # Apply stat modifiers to weapon if progression manager available
        if self.progression_manager:
            modifiers = self.progression_manager.get_weapon_modifiers()
            player_ship.apply_stat_modifiers(modifiers)
        
        success = player_ship.fire_special_weapon(ability_name, self.projectile_manager)
        if success:
            print(f"{player_ship.ship_type} fired {ability_name}")
            # Add appropriate visual/audio effects
            self._add_weapon_effects(player_ship, ability_name)
    
    def _add_weapon_effects(self, player_ship, ability_name):
        """Add visual/audio effects for weapon firing"""
        if not self.effect_manager:
            return
        
        if ability_name == "breach_bomb":
            # Large muzzle flash for breach bomb
            self.effect_manager.add_muzzle_flash(player_ship.x, player_ship.y - 25, size=2.0)
            # Screen shake effect
            self.effect_manager.add_screen_shake(0.2, 5.0)
        
        elif ability_name == "cluster_strike":
            # Multiple small flashes
            for i in range(-3, 4):
                offset_x = i * 40
                self.effect_manager.add_muzzle_flash(
                    player_ship.x + offset_x, player_ship.y - 25, size=0.8
                )
        
        elif ability_name == "overcharge_warheads":
            # Energy charging effect
            self.effect_manager.add_energy_charge(player_ship.x, player_ship.y, duration=1.0)
    
    def _open_inventory(self):
        """Signal to open inventory screen"""
        # This will be handled by GameDirector state management
        print("Inventory requested")
    
    def on_enemy_killed(self, enemy_level, enemy_type):
        """Handle enemy death for progression"""
        if self.progression_manager:
            return self.progression_manager.on_enemy_killed(enemy_level, enemy_type)
        return None
    
    # Key binding management
    def start_key_reassignment(self, action_name):
        """Start reassigning a key binding"""
        if action_name in self.key_bindings:
            self.reassign_mode = True
            self.reassign_target = action_name
            print(f"Press new key for {action_name}")
            return True
        return False
    
    def _reassign_key(self, new_key):
        """Complete key reassignment"""
        if self.reassign_target:
            old_key = self.key_bindings[self.reassign_target]
            self.key_bindings[self.reassign_target] = new_key
            print(f"Reassigned {self.reassign_target}: {old_key} -> {new_key}")
        
        self.reassign_mode = False
        self.reassign_target = None
    
    def cancel_key_reassignment(self):
        """Cancel key reassignment"""
        self.reassign_mode = False
        self.reassign_target = None
        print("Key reassignment cancelled")
    
    def get_key_binding(self, action_name):
        """Get the current key binding for an action"""
        return self.key_bindings.get(action_name)
    
    def get_all_key_bindings(self):
        """Get all current key bindings"""
        return self.key_bindings.copy()
    
    def is_key_held(self, action_name):
        """Check if a key is currently being held"""
        key = self.key_bindings.get(action_name)
        return key in self.keys_held if key else False
    
    def get_movement_keys(self):
        """Get current movement key states for ship movement"""
        return {
            pygame.K_UP: pygame.K_UP in self.keys_held,
            pygame.K_DOWN: pygame.K_DOWN in self.keys_held,
            pygame.K_LEFT: pygame.K_LEFT in self.keys_held,
            pygame.K_RIGHT: pygame.K_RIGHT in self.keys_held
        }
    
    def get_ui_data(self):
        """Get UI data for progression system"""
        if self.progression_manager:
            return self.progression_manager.get_ui_data()
        return None
    
    def debug_print_bindings(self):
        """Print all current key bindings for debugging"""
        print("Current key bindings:")
        for action, key in self.key_bindings.items():
            key_name = pygame.key.name(key)
            print(f"  {action}: {key_name}")
    
    def simulate_key_press(self, action_name, player_ship):
        """Simulate a key press for testing purposes"""
        if action_name in self.key_bindings:
            fake_event = type('obj', (object,), {
                'type': pygame.KEYDOWN,
                'key': self.key_bindings[action_name]
            })
            self._handle_key_down(fake_event, player_ship)