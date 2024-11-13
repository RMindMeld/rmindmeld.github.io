import numpy as np
import pandas as pd
from scipy import stats
import random

def generate_correlated_stats(n_samples=100):
    """Generate correlated character stats."""
    # Create correlation matrix for core stats
    corr_matrix = np.array([
        [1.0, 0.6, 0.4, 0.3, 0.2],  # Power
        [0.6, 1.0, 0.5, 0.4, 0.3],  # Vitality
        [0.4, 0.5, 1.0, 0.7, 0.4],  # Speed
        [0.3, 0.4, 0.7, 1.0, 0.5],  # Recovery
        [0.2, 0.3, 0.4, 0.5, 1.0]   # Control
    ])
    
    # Generate correlated normal distributions
    mean = np.array([60, 55, 50, 45, 40])
    std = np.array([15, 12, 10, 8, 7])
    
    L = np.linalg.cholesky(corr_matrix)
    uncorrelated = np.random.normal(size=(n_samples, 5))
    correlated = uncorrelated @ L.T
    
    # Scale and shift to desired mean and std
    for i in range(5):
        correlated[:, i] = correlated[:, i] * std[i] + mean[i]
    
    return np.clip(correlated, 0, 100)

def generate_essence_ratings():
    """Generate essence ratings following a right-skewed distribution."""
    base = np.random.gamma(2, 1.5)
    return min(10, max(1, round(base, 1)))

def generate_class():
    """Generate character class with weighted probabilities."""
    classes = [
        "Fighter", "Mage", "Healer", "Tank", "Support",
        "Scout", "Summoner", "Controller", "Buffer", "Debuffer"
    ]
    weights = [0.2, 0.15, 0.1, 0.1, 0.1, 0.1, 0.05, 0.08, 0.07, 0.05]
    return np.random.choice(classes, p=weights)

def generate_achievement_rank():
    """Generate achievement ranks with appropriate distribution."""
    ranks = [
        "Bronze", "Silver", "Gold", "Platinum", "Diamond",
        "Ruby", "Sapphire", "Emerald", "Master", "Grandmaster"
    ]
    # Use beta distribution to favor lower ranks
    rank_idx = int(stats.beta(2, 5).rvs() * len(ranks))
    return ranks[min(rank_idx, len(ranks)-1)]

def generate_skills(n_skills=5):
    """Generate a set of skills for a character."""
    all_skills = [
        "Fireball", "Healing Touch", "Shield Wall", "Swift Strike", "Mind Control",
        "Shadow Step", "Lightning Bolt", "Earth Shield", "Wind Slash", "Water Heal",
        "Flame Barrier", "Ice Spike", "Thunder Clap", "Nature's Embrace", "Dark Pulse",
        "Light Beam", "Time Warp", "Space Rip", "Gravity Well", "Energy Burst"
    ]
    return random.sample(all_skills, k=min(n_skills, len(all_skills)))

def generate_dataset(n_samples=100):
    """Generate the complete dataset."""
    # Generate core stats
    stats = generate_correlated_stats(n_samples)
    
    # Create base dataframe
    df = pd.DataFrame(stats, columns=['Power', 'Vitality', 'Speed', 'Recovery', 'Control'])
    
    # Add other characteristics
    df['Essence'] = [generate_essence_ratings() for _ in range(n_samples)]
    df['Class'] = [generate_class() for _ in range(n_samples)]
    df['Achievement_Rank'] = [generate_achievement_rank() for _ in range(n_samples)]
    df['Level'] = np.random.randint(1, 101, size=n_samples)
    df['Experience'] = df['Level'] * 1000 + np.random.randint(0, 1000, size=n_samples)
    df['Skills'] = [generate_skills() for _ in range(n_samples)]
    
    # Generate derived stats with some noise
    df['Health'] = df['Vitality'] * 10 + df['Level'] * 5 + np.random.normal(0, 50, n_samples)
    df['Mana'] = df['Control'] * 8 + df['Level'] * 3 + np.random.normal(0, 30, n_samples)
    df['Attack'] = df['Power'] * 2 + df['Level'] * 2 + np.random.normal(0, 20, n_samples)
    df['Defense'] = df['Vitality'] * 1.5 + df['Level'] * 1.5 + np.random.normal(0, 15, n_samples)
    
    # Ensure non-negative values
    for col in ['Health', 'Mana', 'Attack', 'Defense']:
        df[col] = df[col].clip(lower=0)
    
    return df

if __name__ == "__main__":
    # Generate dataset
    df = generate_dataset(1000)
    
    # Save to CSV
    df.to_csv("../data/hwfwm_characters.csv", index=False)
    print("Dataset generated successfully!")