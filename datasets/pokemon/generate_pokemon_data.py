import numpy as np
import pandas as pd
from scipy import stats
import os

np.random.seed(42)

def generate_types():
    """Generate Pokemon types and their effectiveness relationships."""
    types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 
        'Bug', 'Rock', 'Ghost', 'Dragon'
    ]
    
    # Create effectiveness matrix (0.5 = not very effective, 1 = normal, 2 = super effective, 0 = no effect)
    effectiveness = np.ones((len(types), len(types)))
    
    # Define type effectiveness based on Gen 1 rules
    type_chart = {
        'Normal': {'Rock': 0.5, 'Ghost': 0},
        'Fire': {'Fire': 0.5, 'Water': 0.5, 'Grass': 2, 'Ice': 2, 'Bug': 2, 'Rock': 0.5, 'Dragon': 0.5},
        'Water': {'Fire': 2, 'Water': 0.5, 'Grass': 0.5, 'Ground': 2, 'Rock': 2, 'Dragon': 0.5},
        'Electric': {'Water': 2, 'Electric': 0.5, 'Grass': 0.5, 'Ground': 0, 'Flying': 2, 'Dragon': 0.5},
        'Grass': {'Fire': 0.5, 'Water': 2, 'Grass': 0.5, 'Poison': 0.5, 'Ground': 2, 'Flying': 0.5, 'Bug': 0.5, 'Rock': 2, 'Dragon': 0.5},
        'Ice': {'Water': 0.5, 'Grass': 2, 'Ice': 0.5, 'Ground': 2, 'Flying': 2, 'Dragon': 2},
        'Fighting': {'Normal': 2, 'Ice': 2, 'Poison': 0.5, 'Flying': 0.5, 'Psychic': 0.5, 'Bug': 0.5, 'Rock': 2, 'Ghost': 0},
        'Poison': {'Grass': 2, 'Poison': 0.5, 'Ground': 0.5, 'Bug': 2, 'Rock': 0.5, 'Ghost': 0.5},
        'Ground': {'Fire': 2, 'Electric': 2, 'Grass': 0.5, 'Poison': 2, 'Flying': 0, 'Bug': 0.5, 'Rock': 2},
        'Flying': {'Electric': 0.5, 'Grass': 2, 'Fighting': 2, 'Bug': 2, 'Rock': 0.5},
        'Psychic': {'Fighting': 2, 'Poison': 2, 'Psychic': 0.5},
        'Bug': {'Fire': 0.5, 'Grass': 2, 'Fighting': 0.5, 'Poison': 2, 'Flying': 0.5, 'Psychic': 2},
        'Rock': {'Fire': 2, 'Ice': 2, 'Fighting': 0.5, 'Ground': 0.5, 'Flying': 2, 'Bug': 2},
        'Ghost': {'Normal': 0, 'Psychic': 0, 'Ghost': 2},
        'Dragon': {'Dragon': 2}
    }
    
    # Fill effectiveness matrix
    for i, type1 in enumerate(types):
        for j, type2 in enumerate(types):
            if type1 in type_chart and type2 in type_chart[type1]:
                effectiveness[i, j] = type_chart[type1][type2]
    
    # Create DataFrame for type effectiveness
    effectiveness_df = pd.DataFrame(effectiveness, columns=types, index=types)
    
    return pd.DataFrame({'type_id': range(1, len(types) + 1), 'name': types}), effectiveness_df

def generate_moves():
    """Generate Pokemon moves with realistic distributions."""
    move_types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 
        'Bug', 'Rock', 'Ghost', 'Dragon'
    ]
    
    n_moves = 165  # Approximate number of moves in Gen 1
    
    # Generate move properties with correlations
    power = np.random.gamma(shape=2, scale=20, size=n_moves)
    power = np.clip(power, 0, 100)
    power[np.random.rand(n_moves) < 0.2] = 0  # Status moves have 0 power
    
    # Accuracy correlates negatively with power
    accuracy = 100 - (power * 0.2) + np.random.normal(0, 10, n_moves)
    accuracy = np.clip(accuracy, 0, 100)
    accuracy[accuracy > 95] = 100  # Many moves have 100% accuracy
    
    # PP values are discrete and generally inverse to power
    pp = np.select(
        [power == 0, power <= 30, power <= 60, power <= 90, power <= 100],
        [35, 30, 25, 20, 15]
    )
    
    moves_df = pd.DataFrame({
        'move_id': range(1, n_moves + 1),
        'name': [f'Move_{i}' for i in range(1, n_moves + 1)],
        'type': np.random.choice(move_types, size=n_moves),
        'category': np.where(power == 0, 'Status',
                           np.where(np.random.rand(n_moves) < 0.8, 'Physical', 'Special')),
        'power': power.astype(int),
        'accuracy': accuracy.astype(int),
        'pp': pp
    })
    
    return moves_df

def generate_pokemon():
    """Generate Pokemon with realistic stat distributions and types."""
    n_pokemon = 151  # Number of Gen 1 Pokemon
    
    # Base stats with correlations
    hp = np.random.normal(65, 20, n_pokemon)
    attack = np.random.normal(70, 25, n_pokemon)
    defense = attack * 0.7 + np.random.normal(0, 20, n_pokemon)
    special = np.random.normal(75, 25, n_pokemon)
    speed = attack * 0.5 + np.random.normal(50, 20, n_pokemon)
    
    # Normalize stats to realistic ranges
    stats = [hp, attack, defense, special, speed]
    stats = [np.clip((s - s.min()) / (s.max() - s.min()) * 150 + 20, 20, 180) for s in stats]
    hp, attack, defense, special, speed = stats
    
    # Generate types (some Pokemon have two types)
    types = [
        'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 
        'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 
        'Bug', 'Rock', 'Ghost', 'Dragon'
    ]
    
    type1 = np.random.choice(types, size=n_pokemon)
    has_second_type = np.random.rand(n_pokemon) < 0.5
    type2 = np.where(has_second_type, np.random.choice(types, size=n_pokemon), None)
    
    # Ensure type2 is different from type1
    for i in range(n_pokemon):
        if type2[i] == type1[i]:
            type2[i] = None
    
    # Generate catch rates inversely proportional to total stats
    total_stats = hp + attack + defense + special + speed
    catch_rate = 255 - (total_stats / total_stats.max() * 230)
    
    pokemon_df = pd.DataFrame({
        'pokemon_id': range(1, n_pokemon + 1),
        'name': [f'Pokemon_{i}' for i in range(1, n_pokemon + 1)],
        'type1': type1,
        'type2': type2,
        'hp': hp.astype(int),
        'attack': attack.astype(int),
        'defense': defense.astype(int),
        'special': special.astype(int),
        'speed': speed.astype(int),
        'catch_rate': catch_rate.astype(int)
    })
    
    return pokemon_df

def generate_pokemon_moves():
    """Generate Pokemon-Move relationships."""
    pokemon_df = generate_pokemon()
    moves_df = generate_moves()
    
    relationships = []
    
    for pokemon_id in pokemon_df['pokemon_id']:
        # Number of moves varies by Pokemon
        n_moves = np.random.randint(2, 8)  # Pokemon can learn between 2 and 7 moves
        
        # Filter moves by type compatibility
        pokemon = pokemon_df[pokemon_df['pokemon_id'] == pokemon_id].iloc[0]
        pokemon_types = [pokemon['type1'], pokemon['type2']]
        
        # Prefer moves that match Pokemon's type
        compatible_moves = moves_df[
            (moves_df['type'].isin(pokemon_types)) |
            (moves_df['type'] == 'Normal')
        ]
        
        # If not enough compatible moves, add some random ones
        if len(compatible_moves) < n_moves:
            other_moves = moves_df[~moves_df['move_id'].isin(compatible_moves['move_id'])]
            compatible_moves = pd.concat([compatible_moves, other_moves])
        
        # Select moves
        selected_moves = compatible_moves.sample(n=min(n_moves, len(compatible_moves)))
        
        for _, move in selected_moves.iterrows():
            relationships.append({
                'pokemon_id': pokemon_id,
                'move_id': move['move_id'],
                'learn_method': np.random.choice(['Level Up', 'TM/HM', 'Start'], p=[0.6, 0.3, 0.1]),
                'learn_level': np.random.randint(1, 51) if np.random.random() < 0.6 else None
            })
    
    return pd.DataFrame(relationships)

def main():
    """Generate all datasets and save them."""
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate datasets
    types_df, type_effectiveness_df = generate_types()
    moves_df = generate_moves()
    pokemon_df = generate_pokemon()
    pokemon_moves_df = generate_pokemon_moves()
    
    # Save datasets
    types_df.to_csv('data/types.csv', index=False)
    type_effectiveness_df.to_csv('data/type_effectiveness.csv')
    moves_df.to_csv('data/moves.csv', index=False)
    pokemon_df.to_csv('data/pokemon.csv', index=False)
    pokemon_moves_df.to_csv('data/pokemon_moves.csv', index=False)

if __name__ == '__main__':
    main()