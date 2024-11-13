import numpy as np
import pandas as pd
from faker import Faker
import random
from pathlib import Path

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)
fake = Faker()

# Constants for the game system
RANKS = ['Iron', 'Bronze', 'Silver', 'Gold', 'Diamond', 'Platinum']
EVOLUTION_STAGES = ['Initiate', 'Awakened', 'Core', 'Essence', 'Transcendent']
RACES = ['Human', 'Beast', 'Spirit', 'Construct', 'Mythical']
CLASSES = ['Warrior', 'Mage', 'Rogue', 'Healer', 'Tank', 'Support']
SKILL_CATEGORIES = ['Attack', 'Defense', 'Utility', 'Movement', 'Recovery']
ORIGIN_WORLDS = ['Earth', 'Pallimustus', 'Shadow Realm', 'Crystal Sea', 'Waste']

def generate_core_stats(level, rank_index):
    """Generate core stats based on level and rank."""
    base_stats = {
        'Power': np.random.normal(100 * (rank_index + 1) * (level/10), 20),
        'Vitality': np.random.normal(80 * (rank_index + 1) * (level/10), 15),
        'Spirit': np.random.normal(90 * (rank_index + 1) * (level/10), 18),
        'Endurance': np.random.normal(85 * (rank_index + 1) * (level/10), 16),
        'Magic': np.random.normal(95 * (rank_index + 1) * (level/10), 19)
    }
    return {k: max(1, round(v)) for k, v in base_stats.items()}

def generate_combat_metrics(core_stats, level):
    """Generate combat metrics based on core stats and level."""
    power_factor = core_stats['Power'] / 100
    vitality_factor = core_stats['Vitality'] / 100
    
    return {
        'Damage_Output': round(np.random.normal(power_factor * level * 50, 10)),
        'Survival_Rate': min(100, round(np.random.normal(vitality_factor * 60, 5))),
        'Kill_Count': round(np.random.exponential(power_factor * level))
    }

def generate_skills(level, rank_index):
    """Generate skills based on level and rank."""
    num_skills = min(50, round(np.random.normal(level * 0.8 + rank_index * 3, 2)))
    skill_distribution = {
        'Common': 0.5,
        'Uncommon': 0.3,
        'Rare': 0.15,
        'Epic': 0.04,
        'Legendary': 0.01
    }
    
    skills = {
        'Total_Skills': num_skills,
        'Common_Skills': 0,
        'Uncommon_Skills': 0,
        'Rare_Skills': 0,
        'Epic_Skills': 0,
        'Legendary_Skills': 0
    }
    
    for _ in range(num_skills):
        rarity = np.random.choice(list(skill_distribution.keys()), 
                                p=list(skill_distribution.values()))
        skills[f'{rarity}_Skills'] += 1
    
    return skills

def generate_character():
    """Generate a single character's data."""
    level = round(np.random.normal(30, 10))
    level = max(1, min(100, level))  # Clamp between 1 and 100
    
    rank_index = min(5, max(0, int(level/20)))  # Higher levels tend to higher ranks
    rank = RANKS[rank_index]
    
    evolution_index = min(4, max(0, int(level/25)))  # Evolution stages tied to level
    evolution = EVOLUTION_STAGES[evolution_index]
    
    core_stats = generate_core_stats(level, rank_index)
    combat_metrics = generate_combat_metrics(core_stats, level)
    skills = generate_skills(level, rank_index)
    
    character = {
        'Name': fake.name(),
        'Race': random.choice(RACES),
        'Class': random.choice(CLASSES),
        'Origin_World': random.choice(ORIGIN_WORLDS),
        'Level': level,
        'Rank': rank,
        'Evolution_Stage': evolution,
        **core_stats,
        **combat_metrics,
        **skills
    }
    
    return character

def generate_dataset(num_characters=1000):
    """Generate the complete dataset."""
    characters = [generate_character() for _ in range(num_characters)]
    df = pd.DataFrame(characters)
    
    # Add some noise and outliers
    outlier_indices = np.random.choice(len(df), size=int(len(df) * 0.05), replace=False)
    for idx in outlier_indices:
        # Multiply some numeric columns by a large factor for outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        col = np.random.choice(numeric_cols)
        df.loc[idx, col] *= np.random.uniform(2, 5)
    
    return df

def save_dataset(df, output_dir='../data'):
    """Save the dataset to CSV files."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save raw data
    df.to_csv(f'{output_dir}/raw_data.csv', index=False)
    
    # Create and save processed data (with some basic preprocessing)
    processed_df = df.copy()
    
    # Normalize numeric columns
    numeric_cols = processed_df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        processed_df[f'{col}_normalized'] = (processed_df[col] - processed_df[col].mean()) / processed_df[col].std()
    
    processed_df.to_csv(f'{output_dir}/processed_data.csv', index=False)

if __name__ == '__main__':
    print("Generating HWFWM character dataset...")
    df = generate_dataset(1000)
    save_dataset(df, 'data')
    print("Dataset generated successfully!")
    print(f"Total characters generated: {len(df)}")
    print("\nSample of numeric columns statistics:")
    print(df.describe())