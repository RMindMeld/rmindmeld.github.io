import numpy as np
import pandas as pd
from scipy import stats
import os
from datetime import datetime, timedelta

np.random.seed(42)

def generate_starships(n=50):
    """Generate starship data with realistic correlations."""
    # Ship classes with their typical characteristics
    ship_classes = {
        'Constitution': {'size': 1, 'crew': 430, 'era': 'TOS'},
        'Galaxy': {'size': 1.8, 'crew': 1014, 'era': 'TNG'},
        'Intrepid': {'size': 0.8, 'crew': 141, 'era': 'VOY'},
        'Defiant': {'size': 0.5, 'crew': 50, 'era': 'DS9'},
        'Miranda': {'size': 0.9, 'crew': 350, 'era': 'TOS'},
        'Excelsior': {'size': 1.2, 'crew': 750, 'era': 'TOS'},
        'Sovereign': {'size': 1.5, 'crew': 855, 'era': 'TNG'},
        'Nova': {'size': 0.6, 'crew': 80, 'era': 'TNG'},
        'Nebula': {'size': 1.6, 'crew': 750, 'era': 'TNG'},
        'Olympic': {'size': 1.1, 'crew': 320, 'era': 'TNG'}
    }
    
    ship_class = np.random.choice(list(ship_classes.keys()), size=n)
    
    # Base specifications correlated with ship class
    size_multiplier = np.array([ship_classes[c]['size'] for c in ship_class])
    crew_capacity = np.array([ship_classes[c]['crew'] for c in ship_class])
    era = np.array([ship_classes[c]['era'] for c in ship_class])
    
    # Generate correlated specifications
    length = size_multiplier * 300 + np.random.normal(0, 20, n)
    width = length * 0.65 + np.random.normal(0, 10, n)
    height = length * 0.2 + np.random.normal(0, 5, n)
    
    # Warp capabilities correlate with era and size
    max_warp = np.where(era == 'TNG', 9.6, 8.0) + size_multiplier * 0.2 + np.random.normal(0, 0.1, n)
    
    # Shield strength correlates with size and era
    shield_strength = size_multiplier * 1000 + np.where(era == 'TNG', 500, 0) + np.random.normal(0, 100, n)
    
    # Weapons power correlates with size and era
    weapon_power = size_multiplier * 800 + np.where(era == 'TNG', 400, 0) + np.random.normal(0, 80, n)
    
    df = pd.DataFrame({
        'ship_id': range(1, n + 1),
        'name': [f'USS_{i}' for i in range(1, n + 1)],
        'class': ship_class,
        'registry': [f'NCC-{1701+i}' for i in range(n)],
        'era': era,
        'length': length.astype(int),
        'width': width.astype(int),
        'height': height.astype(int),
        'crew_capacity': crew_capacity,
        'max_warp': np.round(max_warp, 1),
        'shield_strength': shield_strength.astype(int),
        'weapon_power': weapon_power.astype(int)
    })
    
    return df

def generate_crew_members(ships_df, n=1000):
    """Generate crew member data."""
    ranks = ['Ensign', 'Lieutenant Junior Grade', 'Lieutenant', 'Lieutenant Commander', 
            'Commander', 'Captain', 'Admiral']
    rank_weights = [0.3, 0.2, 0.2, 0.15, 0.1, 0.04, 0.01]
    
    departments = ['Command', 'Engineering', 'Science', 'Medical', 'Security', 'Operations']
    dept_weights = [0.15, 0.25, 0.2, 0.15, 0.15, 0.1]
    
    species = ['Human', 'Vulcan', 'Andorian', 'Tellarite', 'Betazoid', 'Trill', 'Bajoran']
    species_weights = [0.6, 0.1, 0.05, 0.05, 0.08, 0.07, 0.05]
    
    # Generate base attributes
    rank = np.random.choice(ranks, size=n, p=rank_weights)
    department = np.random.choice(departments, size=n, p=dept_weights)
    species = np.random.choice(species, size=n, p=species_weights)
    
    # Experience correlates with rank
    rank_years = {'Ensign': 1, 'Lieutenant Junior Grade': 3, 'Lieutenant': 6, 
                 'Lieutenant Commander': 10, 'Commander': 15, 'Captain': 20, 'Admiral': 30}
    experience = np.array([rank_years[r] for r in rank]) + np.random.normal(0, 1, n)
    experience = np.maximum(experience, 0)
    
    # Generate ship assignments ensuring crew capacity is respected
    ship_assignments = []
    remaining_capacity = ships_df['crew_capacity'].copy()
    
    for _ in range(n):
        # Filter ships with remaining capacity
        available_ships = ships_df[remaining_capacity > 0]
        if len(available_ships) == 0:
            break
            
        # Assign to ship with probability proportional to remaining capacity
        probs = remaining_capacity[remaining_capacity > 0] / remaining_capacity[remaining_capacity > 0].sum()
        ship_id = np.random.choice(available_ships['ship_id'], p=probs)
        ship_assignments.append(ship_id)
        remaining_capacity[ship_id-1] -= 1
    
    df = pd.DataFrame({
        'crew_id': range(1, len(ship_assignments) + 1),
        'name': [f'Crew_{i}' for i in range(1, len(ship_assignments) + 1)],
        'rank': rank[:len(ship_assignments)],
        'department': department[:len(ship_assignments)],
        'species': species[:len(ship_assignments)],
        'years_experience': experience[:len(ship_assignments)].astype(int),
        'ship_id': ship_assignments
    })
    
    return df

def generate_missions(ships_df, n=200):
    """Generate mission data."""
    mission_types = ['Exploration', 'Diplomatic', 'Scientific', 'Defense', 'Emergency Response']
    type_weights = [0.3, 0.25, 0.2, 0.15, 0.1]
    
    status_options = ['Completed', 'In Progress', 'Failed', 'Aborted']
    status_weights = [0.7, 0.15, 0.1, 0.05]
    
    # Generate base mission data
    mission_type = np.random.choice(mission_types, size=n, p=type_weights)
    status = np.random.choice(status_options, size=n, p=status_weights)
    
    # Generate stardates (roughly corresponding to TNG era)
    start_stardate = 41000.0 + np.random.uniform(0, 10000, n)
    
    # Duration correlates with mission type
    base_duration = {
        'Exploration': 30,
        'Diplomatic': 15,
        'Scientific': 45,
        'Defense': 10,
        'Emergency Response': 5
    }
    duration = np.array([base_duration[t] for t in mission_type]) + np.random.normal(0, 5, n)
    duration = np.maximum(duration, 1)
    
    # Assign ships based on mission type and ship capabilities
    ship_assignments = []
    for m_type in mission_type:
        if m_type in ['Defense', 'Emergency Response']:
            # Prefer combat-capable ships
            weights = ships_df['weapon_power'] / ships_df['weapon_power'].sum()
        elif m_type == 'Scientific':
            # Prefer larger ships with science capabilities
            weights = ships_df['length'] / ships_df['length'].sum()
        else:
            # Equal weights for other missions
            weights = np.ones(len(ships_df)) / len(ships_df)
        
        ship_assignments.append(np.random.choice(ships_df['ship_id'], p=weights))
    
    df = pd.DataFrame({
        'mission_id': range(1, n + 1),
        'ship_id': ship_assignments,
        'type': mission_type,
        'status': status,
        'stardate': np.round(start_stardate, 1),
        'duration_days': duration.astype(int),
        'priority': np.random.randint(1, 6, n)
    })
    
    return df

def generate_mission_logs(missions_df, n_logs_per_mission=5):
    """Generate mission log entries."""
    log_types = ['Standard', 'Alert', 'Discovery', 'Encounter', 'Technical']
    type_weights = [0.5, 0.15, 0.15, 0.1, 0.1]
    
    logs = []
    for _, mission in missions_df.iterrows():
        n_logs = np.random.poisson(n_logs_per_mission)
        for i in range(n_logs):
            log_type = np.random.choice(log_types, p=type_weights)
            stardate = mission['stardate'] + (mission['duration_days'] * i / n_logs)
            
            logs.append({
                'log_id': len(logs) + 1,
                'mission_id': mission['mission_id'],
                'type': log_type,
                'stardate': round(stardate, 1),
                'content': f'Log entry for mission {mission["mission_id"]} - Entry {i+1}'
            })
    
    return pd.DataFrame(logs)

def generate_ship_systems(ships_df):
    """Generate ship systems and their status."""
    system_types = [
        'Warp Drive', 'Impulse Engines', 'Shields', 'Weapons', 'Life Support',
        'Sensors', 'Communications', 'Transporters', 'Environmental', 'Power Grid'
    ]
    
    systems = []
    for _, ship in ships_df.iterrows():
        for sys_type in system_types:
            # Efficiency correlates with ship era and size
            base_efficiency = 85 if ship['era'] == 'TNG' else 75
            efficiency = base_efficiency + np.random.normal(0, 5)
            efficiency = np.clip(efficiency, 0, 100)
            
            systems.append({
                'system_id': len(systems) + 1,
                'ship_id': ship['ship_id'],
                'type': sys_type,
                'efficiency': round(efficiency, 1),
                'last_maintenance': ship['stardate'] - np.random.uniform(0, 100)
            })
    
    return pd.DataFrame(systems)

def main():
    """Generate all datasets and save them."""
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate primary datasets
    ships_df = generate_starships()
    crew_df = generate_crew_members(ships_df)
    missions_df = generate_missions(ships_df)
    logs_df = generate_mission_logs(missions_df)
    systems_df = generate_ship_systems(ships_df)
    
    # Save all datasets
    ships_df.to_csv('data/starships.csv', index=False)
    crew_df.to_csv('data/crew_members.csv', index=False)
    missions_df.to_csv('data/missions.csv', index=False)
    logs_df.to_csv('data/mission_logs.csv', index=False)
    systems_df.to_csv('data/ship_systems.csv', index=False)

if __name__ == '__main__':
    main()