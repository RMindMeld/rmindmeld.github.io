import numpy as np
import pandas as pd
from scipy import stats
import os

np.random.seed(42)

def generate_characters(n=100):
    """Generate character data with correlated stats."""
    # Base stats with correlations
    strength = np.random.normal(50, 15, n)
    # Vitality correlates with strength
    vitality = strength * 0.6 + np.random.normal(40, 10, n)
    # Intelligence inversely correlates with strength
    intelligence = 100 - (strength * 0.3) + np.random.normal(50, 15, n)
    # Agility slightly negative correlation with strength
    agility = 90 - (strength * 0.2) + np.random.normal(45, 15, n)
    
    # Normalize all stats to 1-100 range
    stats = [strength, vitality, intelligence, agility]
    stats = [(s - s.min()) / (s.max() - s.min()) * 99 + 1 for s in stats]
    strength, vitality, intelligence, agility = stats
    
    classes = np.random.choice(
        ['Warrior', 'Mage', 'Rogue', 'Paladin', 'Warlock'],
        size=n,
        p=[0.3, 0.25, 0.2, 0.15, 0.1]
    )
    
    levels = np.random.gamma(shape=2, scale=10, size=n)
    levels = np.clip(levels, 1, 50).astype(int)
    
    df = pd.DataFrame({
        'character_id': range(1, n + 1),
        'name': [f'Character_{i}' for i in range(1, n + 1)],
        'class': classes,
        'level': levels,
        'strength': strength.astype(int),
        'vitality': vitality.astype(int),
        'intelligence': intelligence.astype(int),
        'agility': agility.astype(int),
        'experience': levels * 1000 + np.random.normal(0, 100, n).astype(int)
    })
    
    return df

def generate_items(n=200):
    """Generate item data with correlated properties."""
    rarity_weights = {
        'Common': 0.4,
        'Uncommon': 0.3,
        'Rare': 0.2,
        'Epic': 0.08,
        'Legendary': 0.02
    }
    
    rarity = np.random.choice(
        list(rarity_weights.keys()),
        size=n,
        p=list(rarity_weights.values())
    )
    
    # Base item power correlates with rarity
    rarity_power = {'Common': 1, 'Uncommon': 2, 'Rare': 3, 'Epic': 4, 'Legendary': 5}
    base_power = np.array([rarity_power[r] for r in rarity])
    
    power = base_power * 10 + np.random.normal(0, 2, n)
    durability = power * 0.7 + np.random.normal(50, 10, n)
    value = power * 100 + np.random.exponential(1000, n)
    
    item_types = np.random.choice(
        ['Weapon', 'Armor', 'Accessory', 'Consumable'],
        size=n,
        p=[0.4, 0.3, 0.2, 0.1]
    )
    
    df = pd.DataFrame({
        'item_id': range(1, n + 1),
        'name': [f'Item_{i}' for i in range(1, n + 1)],
        'type': item_types,
        'rarity': rarity,
        'power': power.astype(int),
        'durability': durability.astype(int),
        'value': value.astype(int)
    })
    
    return df

def generate_skills(n=50):
    """Generate skill data."""
    skill_types = np.random.choice(
        ['Attack', 'Defense', 'Support', 'Magic'],
        size=n,
        p=[0.4, 0.2, 0.2, 0.2]
    )
    
    # Base power correlates with level requirement
    level_req = np.random.gamma(shape=2, scale=10, size=n)
    level_req = np.clip(level_req, 1, 50).astype(int)
    
    power = level_req * 5 + np.random.normal(0, 10, n)
    mana_cost = power * 0.8 + np.random.normal(0, 5, n)
    
    df = pd.DataFrame({
        'skill_id': range(1, n + 1),
        'name': [f'Skill_{i}' for i in range(1, n + 1)],
        'type': skill_types,
        'power': power.astype(int),
        'mana_cost': mana_cost.astype(int),
        'level_requirement': level_req
    })
    
    return df

def generate_character_items(characters_df, items_df, avg_items_per_char=3):
    """Generate character-item relationships."""
    relationships = []
    
    for char_id in characters_df['character_id']:
        # Number of items varies by character level
        char_level = characters_df.loc[characters_df['character_id'] == char_id, 'level'].iloc[0]
        n_items = np.random.poisson(avg_items_per_char * (char_level/10 + 1))
        n_items = min(n_items, len(items_df))
        
        if n_items > 0:
            char_items = np.random.choice(items_df['item_id'], size=n_items, replace=False)
            for item_id in char_items:
                relationships.append({
                    'character_id': char_id,
                    'item_id': item_id,
                    'acquisition_date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=np.random.randint(0, 365))
                })
    
    return pd.DataFrame(relationships)

def generate_character_skills(characters_df, skills_df):
    """Generate character-skill relationships."""
    relationships = []
    
    for _, char in characters_df.iterrows():
        # Skills available based on level and class
        available_skills = skills_df[skills_df['level_requirement'] <= char['level']]
        
        # Number of skills varies by level
        n_skills = min(
            np.random.binomial(len(available_skills), char['level']/60),
            len(available_skills)
        )
        
        if n_skills > 0:
            char_skills = np.random.choice(available_skills['skill_id'], size=n_skills, replace=False)
            for skill_id in char_skills:
                relationships.append({
                    'character_id': char['character_id'],
                    'skill_id': skill_id,
                    'mastery_level': np.random.randint(1, char['level'])
                })
    
    return pd.DataFrame(relationships)

def main():
    """Generate all datasets and save them."""
    # Create output directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate primary datasets
    characters_df = generate_characters()
    items_df = generate_items()
    skills_df = generate_skills()
    
    # Generate relationship datasets
    char_items_df = generate_character_items(characters_df, items_df)
    char_skills_df = generate_character_skills(characters_df, skills_df)
    
    # Save all datasets
    characters_df.to_csv('data/characters.csv', index=False)
    items_df.to_csv('data/items.csv', index=False)
    skills_df.to_csv('data/skills.csv', index=False)
    char_items_df.to_csv('data/character_items.csv', index=False)
    char_skills_df.to_csv('data/character_skills.csv', index=False)

if __name__ == '__main__':
    main()