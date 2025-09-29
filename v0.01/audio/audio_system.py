#!/usr/bin/env python3
import pygame
import random
import os
import math

class AudioSystem:
    """Manages all game audio - sound effects and music"""
    
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Audio settings
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.4
        self.enabled = True
        
        # Sound effect containers
        self.sound_cache = {}  # Loaded sound files
        self.playing_sounds = []  # Currently playing sounds
        
        # Music system
        self.current_music = None
        self.music_fade_timer = 0
        self.music_queue = []
        
        # Sound categories for volume control
        self.category_volumes = {
            'weapons': 0.8,
            'explosions': 1.0,
            'impacts': 0.6,
            'engine': 0.3,
            'ui': 0.5,
            'ambient': 0.4
        }
        
        # Generated sounds (procedural audio for when files aren't available)
        self.generated_sounds = {}
        
        print("AudioSystem initialized")
        self._generate_placeholder_sounds()
    
    def _generate_placeholder_sounds(self):
        """Generate procedural sound effects when audio files aren't available"""
        # This creates simple synthesized sounds using pygame
        
        # Explosion sound - noise burst with low-pass filter
        explosion_samples = []
        for i in range(8820):  # 0.2 seconds at 44100 Hz
            # White noise with envelope
            envelope = max(0, 1.0 - (i / 8820))
            noise = random.uniform(-1, 1) * envelope * 0.3
            explosion_samples.append([int(noise * 32767), int(noise * 32767)])
        
        explosion_sound = pygame.sndarray.make_sound(explosion_samples)
        self.generated_sounds['explosion'] = explosion_sound
        
        # Cannon fire - sharp pop with decay
        cannon_samples = []
        for i in range(2205):  # 0.05 seconds
            envelope = max(0, 1.0 - (i / 2205) ** 0.3)
            freq = 200 + (100 * envelope)
            wave = math.sin(2 * math.pi * freq * i / 44100) * envelope * 0.4
            cannon_samples.append([int(wave * 32767), int(wave * 32767)])
        
        cannon_sound = pygame.sndarray.make_sound(cannon_samples)
        self.generated_sounds['cannon'] = cannon_sound
        
        # Energy charge - rising tone
        charge_samples = []
        for i in range(22050):  # 0.5 seconds
            progress = i / 22050
            freq = 100 + (300 * progress)
            envelope = math.sin(math.pi * progress) * 0.3
            wave = math.sin(2 * math.pi * freq * i / 44100) * envelope
            charge_samples.append([int(wave * 32767), int(wave * 32767)])
        
        charge_sound = pygame.sndarray.make_sound(charge_samples)
        self.generated_sounds['energy_charge'] = charge_sound
        
        # Impact hit - short metallic clang
        impact_samples = []
        for i in range(1102):  # 0.025 seconds
            envelope = max(0, 1.0 - (i / 1102) ** 0.1)
            # Multiple frequencies for metallic sound
            wave = 0
            for freq in [800, 1200, 1600]:
                wave += math.sin(2 * math.pi * freq * i / 44100) * envelope * 0.1
            impact_samples.append([int(wave * 32767), int(wave * 32767)])
        
        impact_sound = pygame.sndarray.make_sound(impact_samples)
        self.generated_sounds['impact'] = impact_sound
        
        # Shield hit - electric zap
        shield_samples = []
        for i in range(3307):  # 0.075 seconds
            envelope = max(0, 1.0 - (i / 3307))
            # High frequency noise for electric effect
            noise = random.uniform(-1, 1) * envelope * 0.2
            freq_mod = 50 + random.uniform(-10, 10)
            wave = math.sin(2 * math.pi * freq_mod * i / 44100) * envelope * 0.1
            combined = (noise + wave) * 0.5
            shield_samples.append([int(combined * 32767), int(combined * 32767)])
        
        shield_sound = pygame.sndarray.make_sound(shield_samples)
        self.generated_sounds['shield_hit'] = shield_sound
        
        # Engine thrust - low rumble
        engine_samples = []
        for i in range(44100):  # 1 second loop
            # Low frequency rumble
            base_freq = 80
            wave = 0
            wave += math.sin(2 * math.pi * base_freq * i / 44100) * 0.3
            wave += math.sin(2 * math.pi * (base_freq * 1.5) * i / 44100) * 0.2
            wave += random.uniform(-0.1, 0.1)  # Add some noise
            engine_samples.append([int(wave * 32767 * 0.3), int(wave * 32767 * 0.3)])
        
        engine_sound = pygame.sndarray.make_sound(engine_samples)
        self.generated_sounds['engine'] = engine_sound
    
    def load_sound(self, sound_name, file_path, category='sfx'):
        """Load a sound file into cache"""
        if not self.enabled:
            return False
        
        try:
            if os.path.exists(file_path):
                sound = pygame.mixer.Sound(file_path)
                self.sound_cache[sound_name] = {
                    'sound': sound,
                    'category': category
                }
                print(f"Loaded sound: {sound_name}")
                return True
            else:
                print(f"Sound file not found: {file_path}")
                return False
        except Exception as e:
            print(f"Failed to load sound {sound_name}: {e}")
            return False
    
    def play_sound(self, sound_name, volume=1.0, pitch=1.0, position=None, loop=False):
        """Play a sound effect"""
        if not self.enabled:
            return None
        
        # Try to get sound from cache first
        sound_data = self.sound_cache.get(sound_name)
        if sound_data:
            sound = sound_data['sound']
            category = sound_data['category']
        else:
            # Fall back to generated sounds
            sound = self.generated_sounds.get(sound_name)
            category = 'sfx'
        
        if not sound:
            print(f"Sound not found: {sound_name}")
            return None
        
        # Calculate final volume
        category_vol = self.category_volumes.get(category, 1.0)
        final_volume = self.master_volume * self.sfx_volume * category_vol * volume
        
        # Apply positional audio if position given
        if position:
            # Simple stereo panning based on position (more complex 3D audio could be added)
            screen_center = 1920  # Assume 4K center
            pan = max(-1, min(1, (position[0] - screen_center) / screen_center))
            
            # Adjust volume for distance (simple implementation)
            distance_factor = 1.0  # Could add distance-based volume reduction
            final_volume *= distance_factor
        
        # Play sound
        try:
            channel = sound.play(loops=-1 if loop else 0)
            if channel:
                channel.set_volume(final_volume)
                
                # Store reference for management
                sound_info = {
                    'channel': channel,
                    'name': sound_name,
                    'category': category,
                    'start_time': pygame.time.get_ticks()
                }
                self.playing_sounds.append(sound_info)
                
                return channel
        except Exception as e:
            print(f"Failed to play sound {sound_name}: {e}")
        
        return None
    
    def stop_sound(self, sound_name):
        """Stop all instances of a specific sound"""
        for sound_info in self.playing_sounds[:]:
            if sound_info['name'] == sound_name:
                sound_info['channel'].stop()
                self.playing_sounds.remove(sound_info)
    
    def stop_category(self, category):
        """Stop all sounds in a category"""
        for sound_info in self.playing_sounds[:]:
            if sound_info['category'] == category:
                sound_info['channel'].stop()
                self.playing_sounds.remove(sound_info)
    
    def play_explosion(self, size=1.0, explosion_type="standard"):
        """Play explosion sound with size/type variation"""
        base_volume = 0.8 * size
        pitch_variation = random.uniform(0.9, 1.1)
        
        if explosion_type == "large":
            base_volume *= 1.3
            pitch_variation *= 0.8
        elif explosion_type == "energy":
            # Could play a different explosion sound
            pass
        
        return self.play_sound('explosion', volume=base_volume)
    
    def play_weapon_fire(self, weapon_type, ship_position=None):
        """Play weapon firing sound"""
        sound_map = {
            'cannon': 'cannon',
            'breach_bomb': 'explosion',  # Launcher sound
            'cluster_strike': 'cannon',
            'energy_beam': 'energy_charge'
        }
        
        sound_name = sound_map.get(weapon_type, 'cannon')
        volume = 0.6 if weapon_type == 'cannon' else 0.8
        
        return self.play_sound(sound_name, volume=volume, position=ship_position)
    
    def play_impact(self, impact_type="generic", position=None):
        """Play impact sound"""
        impact_sounds = {
            'shield': 'shield_hit',
            'armor': 'impact',
            'generic': 'impact'
        }
        
        sound_name = impact_sounds.get(impact_type, 'impact')
        volume = random.uniform(0.4, 0.7)
        
        return self.play_sound(sound_name, volume=volume, position=position)
    
    def play_engine(self, throttle=1.0, ship_position=None):
        """Play engine sound (looped)"""
        volume = 0.3 * throttle
        return self.play_sound('engine', volume=volume, position=ship_position, loop=True)
    
    def load_music(self, music_name, file_path):
        """Load background music"""
        if not self.enabled:
            return False
        
        try:
            if os.path.exists(file_path):
                # Store music info for later use
                self.music_queue.append({
                    'name': music_name,
                    'path': file_path
                })
                print(f"Music loaded: {music_name}")
                return True
            else:
                print(f"Music file not found: {file_path}")
                return False
        except Exception as e:
            print(f"Failed to load music {music_name}: {e}")
            return False
    
    def play_music(self, music_name, fade_in_time=0, loop=True):
        """Play background music"""
        if not self.enabled:
            return False
        
        # Find music in queue
        music_info = None
        for music in self.music_queue:
            if music['name'] == music_name:
                music_info = music
                break
        
        if not music_info:
            print(f"Music not found: {music_name}")
            return False
        
        try:
            if fade_in_time > 0:
                pygame.mixer.music.load(music_info['path'])
                pygame.mixer.music.play(loops=-1 if loop else 0, fade_ms=int(fade_in_time * 1000))
            else:
                pygame.mixer.music.load(music_info['path'])
                pygame.mixer.music.play(loops=-1 if loop else 0)
            
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
            self.current_music = music_name
            return True
        except Exception as e:
            print(f"Failed to play music {music_name}: {e}")
            return False
    
    def stop_music(self, fade_out_time=0):
        """Stop background music"""
        if fade_out_time > 0:
            pygame.mixer.music.fadeout(int(fade_out_time * 1000))
        else:
            pygame.mixer.music.stop()
        
        self.current_music = None
    
    def set_master_volume(self, volume):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        
        # Update currently playing music
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
    
    def set_category_volume(self, category, volume):
        """Set volume for a specific category"""
        self.category_volumes[category] = max(0.0, min(1.0, volume))
    
    def update(self, delta_time):
        """Update audio system (clean up finished sounds)"""
        if not self.enabled:
            return
        
        # Clean up finished sounds
        for sound_info in self.playing_sounds[:]:
            if not sound_info['channel'].get_busy():
                self.playing_sounds.remove(sound_info)
        
        # Update music fade if needed
        if self.music_fade_timer > 0:
            self.music_fade_timer -= delta_time
    
    def get_playing_sound_count(self):
        """Get number of currently playing sounds"""
        return len(self.playing_sounds)
    
    def enable_audio(self, enabled=True):
        """Enable or disable audio system"""
        self.enabled = enabled
        if not enabled:
            self.stop_all_sounds()
            self.stop_music()
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        for sound_info in self.playing_sounds:
            sound_info['channel'].stop()
        self.playing_sounds.clear()
    
    def cleanup(self):
        """Clean up audio system resources"""
        self.stop_all_sounds()
        self.stop_music()
        self.sound_cache.clear()
        self.generated_sounds.clear()
        pygame.mixer.quit()


class AudioManager:
    """High-level audio manager that connects to game events"""
    
    def __init__(self):
        self.audio_system = AudioSystem()
        
        # Audio event tracking
        self.last_explosion_time = 0
        self.explosion_cooldown = 0.1  # Prevent audio spam
        
        print("AudioManager initialized")
    
    def initialize_game_audio(self):
        """Initialize audio for game (load any required files)"""
        # This would load actual audio files if they exist
        # For now, we rely on generated sounds
        pass
    
    def on_weapon_fired(self, weapon_type, ship_position=None):
        """Handle weapon firing audio"""
        self.audio_system.play_weapon_fire(weapon_type, ship_position)
    
    def on_explosion(self, position, size=1.0, explosion_type="standard"):
        """Handle explosion audio"""
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Prevent audio spam from multiple simultaneous explosions
        if current_time - self.last_explosion_time < self.explosion_cooldown:
            return
        
        self.audio_system.play_explosion(size, explosion_type)
        self.last_explosion_time = current_time
    
    def on_projectile_hit(self, hit_type, position=None):
        """Handle projectile impact audio"""
        self.audio_system.play_impact(hit_type, position)
    
    def on_enemy_death(self, enemy_position=None):
        """Handle enemy death audio"""
        # Could play specific death sounds
        self.audio_system.play_explosion(0.5, "small")
    
    def on_player_damage(self, damage_type="generic"):
        """Handle player taking damage"""
        if damage_type == "shield":
            self.audio_system.play_impact("shield")
        else:
            self.audio_system.play_impact("armor")
    
    def start_game_music(self):
        """Start game background music"""
        # Would play actual music files if available
        pass
    
    def start_menu_music(self):
        """Start menu background music"""
        # Would play menu music if available
        pass
    
    def update(self, delta_time):
        """Update audio manager"""
        self.audio_system.update(delta_time)
    
    def get_audio_system(self):
        """Get reference to audio system for direct control"""
        return self.audio_system
    
    def cleanup(self):
        """Clean up audio manager"""
        self.audio_system.cleanup()
