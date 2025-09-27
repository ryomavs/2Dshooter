#!/usr/bin/env python3
import math

class DamageCalculator:
    """Pure physics-based damage calculation using raw joules - NO SCALING FACTORS"""
    
    # Physics constants
    EXPLOSIVE_JOULES_PER_KG = 4184000  # TNT equivalent
    PROXIMITY_FUSE_RADIUS = 20
    
    @staticmethod
    def calculate_distance(pos1, pos2):
        """Calculate distance between two positions"""
        return math.hypot(pos1[0] - pos2[0], pos1[1] - pos2[1])
    
    @staticmethod
    def calculate_explosion_damage(explosion_center, target_pos, warhead_data):
        """
        Calculate damage from explosive using pure joules - NO SCALING
        
        Args:
            explosion_center: (x, y) position of explosion
            target_pos: (x, y) position of target
            warhead_data: dict with explosive_kg, shrapnel data, velocity, diameter_mm
        
        Returns:
            total_damage: raw joules of energy delivered to target
        """
        distance = DamageCalculator.calculate_distance(explosion_center, target_pos)
        
        # Calculate effective damage radius based on warhead properties
        diameter_m = warhead_data.get("diameter_mm", 50) / 1000.0
        explosive_kg = warhead_data["explosive_kg"]
        
        # Damage radius scales with explosive amount and warhead size
        base_radius = 50  # Base game units
        diameter_factor = (diameter_m / 0.05) ** 0.5
        explosive_factor = (explosive_kg / 0.5) ** 0.3
        max_damage_radius = base_radius * diameter_factor * explosive_factor
        
        if distance > max_damage_radius:
            return 0.0
        
        # Explosive pressure wave damage - PURE JOULES
        explosive_joules = explosive_kg * DamageCalculator.EXPLOSIVE_JOULES_PER_KG
        pressure_damage = DamageCalculator._calculate_pressure_damage(
            explosive_joules, distance, diameter_m
        )
        
        # Kinetic shrapnel damage - PURE JOULES
        shrapnel_damage = DamageCalculator._calculate_shrapnel_damage(
            warhead_data, distance, diameter_m
        )
        
        total_damage_joules = pressure_damage + shrapnel_damage
        return max(0.0, total_damage_joules)
    
    @staticmethod
    def _calculate_pressure_damage(explosive_joules, distance, diameter_m):
        """Calculate explosive pressure wave damage in pure joules"""
        if distance <= 0:
            distance = 0.1
        
        # Warhead efficiency based on diameter
        diameter_efficiency = min(2.0, (diameter_m / 0.05) ** 0.2)
        
        # Total explosive energy available
        available_energy = explosive_joules * diameter_efficiency
        
        # Energy distribution follows inverse square law with distance
        effective_distance = max(1.0, distance / diameter_efficiency)
        falloff = 1.0 / (effective_distance ** 2)
        
        # Energy delivered to target position - PURE JOULES
        delivered_energy = available_energy * falloff
        
        return delivered_energy
    
    @staticmethod
    def _calculate_shrapnel_damage(warhead_data, distance, diameter_m):
        """Calculate kinetic shrapnel damage in pure joules"""
        if distance <= 0:
            distance = 0.1
        
        # Extract shrapnel properties
        shrapnel_kg = warhead_data.get("shrapnel_kg", warhead_data["total_mass"] * warhead_data["shrapnel_percent"])
        projectile_velocity = warhead_data["velocity"]  # m/s
        diameter_mm = warhead_data.get("diameter_mm", 50)
        length_mm = warhead_data.get("length_mm", 300)
        
        # Calculate fragment properties
        fragment_count = DamageCalculator._calculate_fragment_count(shrapnel_kg, diameter_mm, length_mm)
        fragment_mass = shrapnel_kg / fragment_count if fragment_count > 0 else 0
        
        # Fragment velocity distribution
        diameter_factor = diameter_mm / 50.0
        velocity_spread = 0.3 * diameter_factor
        min_velocity = projectile_velocity * (1 - velocity_spread)
        max_velocity = projectile_velocity * (1 + velocity_spread)
        avg_fragment_velocity = (min_velocity + max_velocity) / 2
        
        # Total kinetic energy of all fragments - PURE JOULES
        # KE = 0.5 * m * v²
        kinetic_energy_per_fragment = 0.5 * fragment_mass * (avg_fragment_velocity ** 2)
        total_kinetic_energy = kinetic_energy_per_fragment * fragment_count
        
        # Shrapnel effective range
        base_range = 60
        dispersion_factor = (diameter_mm / 50.0) ** 0.5
        energy_factor = (total_kinetic_energy / 1000000) ** 0.2
        max_shrapnel_range = base_range * dispersion_factor * energy_factor
        
        if distance > max_shrapnel_range:
            return 0.0
        
        # Fragment density falloff with distance
        falloff = max(0, (max_shrapnel_range - distance) / max_shrapnel_range)
        
        # Hit probability based on fragment density
        hit_probability = min(1.0, (fragment_count / 1000.0) * (falloff ** 0.5))
        
        # Energy delivered by fragments that hit target - PURE JOULES
        delivered_shrapnel_energy = total_kinetic_energy * hit_probability * falloff
        
        return delivered_shrapnel_energy
    
    @staticmethod
    def _calculate_fragment_count(shrapnel_mass, diameter_mm, length_mm):
        """Calculate number of fragments based on physical properties"""
        # Calculate shell surface area
        diameter_m = diameter_mm / 1000.0
        length_m = length_mm / 1000.0
        
        # Surface area = cylindrical surface + end caps
        cylindrical_area = math.pi * diameter_m * length_m
        end_caps_area = 2 * math.pi * (diameter_m / 2) ** 2
        total_surface_area = cylindrical_area + end_caps_area
        
        # Fragment density for military ordnance
        fragments_per_m2 = 3000
        base_fragment_count = total_surface_area * fragments_per_m2
        
        # Minimum viable fragment mass constraint
        min_fragment_mass = 0.0005  # 0.5 grams
        max_fragments_by_mass = shrapnel_mass / min_fragment_mass
        
        # Aspect ratio affects fragmentation
        aspect_ratio = length_m / diameter_m
        if aspect_ratio > 3:
            fragmentation_efficiency = 0.8  # Long, thin
        elif aspect_ratio < 1.5:
            fragmentation_efficiency = 1.2  # Short, wide
        else:
            fragmentation_efficiency = 1.0  # Standard
        
        base_fragment_count *= fragmentation_efficiency
        fragment_count = min(base_fragment_count, max_fragments_by_mass)
        
        return max(1, int(fragment_count))
    
    @staticmethod
    def calculate_projectile_damage(projectile_data, target_pos=None):
        """
        Calculate damage from kinetic projectiles in pure joules - NO SCALING
        
        Args:
            projectile_data: dict with mass_kg, velocity_kmh
            target_pos: optional for penetration calculations
        
        Returns:
            kinetic_energy_joules: pure kinetic energy in joules
        """
        mass = projectile_data["mass_kg"]  # kg
        velocity = projectile_data["velocity_kmh"] * 1000 / 3600  # Convert km/h to m/s
        
        # Pure kinetic energy: KE = 0.5 * m * v² - NO SCALING
        kinetic_energy_joules = 0.5 * mass * (velocity ** 2)
        
        return kinetic_energy_joules
    
    @staticmethod
    def calculate_energy_weapon_damage(weapon_data, target_pos, beam_origin):
        """
        Calculate damage from energy weapons in pure joules - NO SCALING
        
        Args:
            weapon_data: dict with power_mw, duration_ms
            target_pos: (x, y) position of target
            beam_origin: (x, y) position of weapon
        
        Returns:
            energy_joules: pure energy delivered in joules
        """
        power_mw = weapon_data["power_mw"]
        duration_ms = weapon_data["duration_ms"]
        beam_type = weapon_data.get("beam_type", "continuous")
        
        # Convert to standard units
        power_watts = power_mw * 1000000  # MW to watts
        duration_seconds = duration_ms / 1000.0  # ms to seconds
        
        # Energy delivered: E = Power × Time - PURE JOULES
        energy_joules = power_watts * duration_seconds
        
        # Distance-based energy dissipation
        distance = DamageCalculator.calculate_distance(beam_origin, target_pos)
        
        if beam_type == "continuous":
            falloff = max(0.1, 1.0 - (distance / 200))
        elif beam_type == "pulse":
            falloff = max(0.05, 1.0 - (distance / 150))
        else:
            falloff = 1.0
        
        # Energy delivered to target - PURE JOULES
        delivered_energy_joules = energy_joules * falloff
        
        return delivered_energy_joules
    
    @staticmethod
    def apply_target_modifiers(base_damage_joules, target_data, weapon_type):
        """
        Apply target-specific damage modifiers to joules
        
        Args:
            base_damage_joules: raw energy in joules
            target_data: dict with armor, shields, resistances
            weapon_type: "explosive", "kinetic", "energy"
        
        Returns:
            final_damage_joules: energy after target modifiers
        """
        damage = base_damage_joules
        
        # Apply armor reduction based on weapon type
        if weapon_type == "kinetic":
            armor_reduction = target_data.get("kinetic_armor", 0)
        elif weapon_type == "explosive":
            armor_reduction = target_data.get("explosive_armor", 0)
        elif weapon_type == "energy":
            armor_reduction = target_data.get("energy_armor", 0)
        else:
            armor_reduction = 0
        
        # Apply armor as energy absorption percentage
        damage *= (1.0 - armor_reduction)
        
        # Apply shield energy absorption
        shield_absorption = target_data.get("shield_absorption", 0)
        damage *= (1.0 - shield_absorption)
        
        return max(0.0, damage)
    
    @staticmethod
    def create_warhead_data_from_db(bomb_stats):
        """Convert database format to warhead data for pure joule calculations"""
        # Convert km/h to m/s
        velocity_ms = bomb_stats["velocity_kmh"] * 1000 / 3600
        
        # Extract data from database
        total_mass_kg = bomb_stats["mass_kg"]
        shrapnel_kg = bomb_stats["shrapnel_kg"]
        shrapnel_percent = shrapnel_kg / total_mass_kg
        
        # Estimate explosive content
        casing_mass = total_mass_kg * 0.2  # 20% casing
        explosive_kg = total_mass_kg - shrapnel_kg - casing_mass
        explosive_kg = max(0.1, explosive_kg)  # Minimum explosive
        
        # Physical dimensions
        diameter_mm = bomb_stats.get("diameter_mm", 75)
        length_mm = bomb_stats.get("length_mm", 300)
        
        return {
            "explosive_kg": explosive_kg,
            "shrapnel_percent": shrapnel_percent,
            "total_mass": total_mass_kg,
            "velocity": velocity_ms,
            "diameter_mm": diameter_mm,
            "length_mm": length_mm,
            "shrapnel_kg": shrapnel_kg
        }
    
    @staticmethod
    def check_proximity_trigger(projectile_pos, projectile_velocity, targets, fuse_radius=None, delta_time=0):
        """
        Check proximity fuse trigger with predictive timing
        
        Returns:
            (should_trigger, closest_target_pos)
        """
        if fuse_radius is None:
            fuse_radius = DamageCalculator.PROXIMITY_FUSE_RADIUS
        
        closest_distance = float('inf')
        closest_target = None
        
        # Current position check
        for target_pos in targets:
            distance = DamageCalculator.calculate_distance(projectile_pos, target_pos)
            if distance <= fuse_radius and distance < closest_distance:
                closest_distance = distance
                closest_target = target_pos
        
        # Predictive check to avoid missing fast targets
        if closest_target is None and delta_time > 0:
            next_x = projectile_pos[0] + projectile_velocity[0] * delta_time
            next_y = projectile_pos[1] + projectile_velocity[1] * delta_time
            next_pos = (next_x, next_y)
            
            for target_pos in targets:
                current_dist = DamageCalculator.calculate_distance(projectile_pos, target_pos)
                next_dist = DamageCalculator.calculate_distance(next_pos, target_pos)
                
                if next_dist <= fuse_radius and next_dist < current_dist:
                    if next_dist < closest_distance:
                        closest_distance = next_dist
                        closest_target = target_pos
        
        return (closest_target is not None, closest_target)