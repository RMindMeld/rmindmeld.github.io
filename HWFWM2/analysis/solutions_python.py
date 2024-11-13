import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for matplotlib
plt.style.use('seaborn')
sns.set_palette("husl")

def load_data():
    """Load and prepare the dataset."""
    df = pd.read_csv('../data/processed_data.csv')
    return df

# Exploratory Data Analysis Solutions

def plot_race_distribution(df):
    """
    Question 1: Character Race Distribution
    Plot the distribution of characters across different races
    """
    plt.figure(figsize=(10, 6))
    race_counts = df['Race'].value_counts()
    plt.pie(race_counts, labels=race_counts.index, autopct='%1.1f%%')
    plt.title('Character Race Distribution')
    plt.axis('equal')
    return plt

def analyze_level_distribution(df):
    """
    Question 2: Level Distribution Analysis
    Examine the distribution of character levels
    """
    plt.figure(figsize=(12, 6))
    sns.histplot(data=df, x='Level', kde=True)
    plt.title('Character Level Distribution')
    plt.xlabel('Level')
    plt.ylabel('Count')
    return plt

def plot_core_stats_correlation(df):
    """
    Question 3: Core Stats Correlation Matrix
    Identify relationships between core stats
    """
    core_stats = ['Power', 'Vitality', 'Spirit', 'Endurance', 'Magic']
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[core_stats].corr(), annot=True, cmap='coolwarm')
    plt.title('Core Stats Correlation Matrix')
    return plt

def plot_skill_rarity_distribution(df):
    """
    Question 4: Skill Rarity Distribution
    Analyze the distribution of skill rarities across characters
    """
    skill_cols = ['Common_Skills', 'Uncommon_Skills', 'Rare_Skills', 'Epic_Skills', 'Legendary_Skills']
    skill_data = df[skill_cols].mean()
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(skill_data.index, skill_data.values)
    plt.title('Average Skill Distribution by Rarity')
    plt.xticks(rotation=45)
    plt.ylabel('Average Number of Skills')
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom')
    return plt

# Statistical Analysis Solutions

def power_level_analysis(df):
    """
    Question 11: Power Level Statistical Tests
    Test if power levels significantly differ between races
    """
    # Perform one-way ANOVA
    races = df['Race'].unique()
    power_by_race = [df[df['Race'] == race]['Power'] for race in races]
    f_stat, p_value = stats.f_oneway(*power_by_race)
    
    # Create box plot
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Race', y='Power', data=df)
    plt.title(f'Power Distribution by Race\nANOVA: p-value = {p_value:.4f}')
    plt.xticks(rotation=45)
    return plt

def survival_rate_analysis(df):
    """
    Question 12: Survival Rate Factors
    Perform multiple regression to identify key survival rate factors
    """
    from sklearn.linear_model import LinearRegression
    
    # Prepare features
    features = ['Vitality', 'Endurance', 'Level']
    X = df[features]
    y = df['Survival_Rate']
    
    # Fit regression
    model = LinearRegression()
    model.fit(X, y)
    
    # Plot coefficients
    plt.figure(figsize=(10, 6))
    coef_df = pd.DataFrame({
        'Feature': features,
        'Coefficient': model.coef_
    })
    sns.barplot(x='Feature', y='Coefficient', data=coef_df)
    plt.title('Survival Rate Factors - Regression Coefficients')
    plt.xticks(rotation=45)
    return plt

# Character Optimization Solutions

def plot_optimal_stat_distribution(df):
    """
    Question 16: Optimal Stat Distribution
    Identify most effective stat distributions for combat
    """
    # Calculate combat effectiveness score
    df['Combat_Score'] = (df['Damage_Output'] * 0.4 + 
                         df['Survival_Rate'] * 0.4 + 
                         df['Kill_Count'] * 0.2)
    
    # Get top performers
    top_performers = df.nlargest(50, 'Combat_Score')
    
    # Create parallel coordinates plot
    fig = px.parallel_coordinates(
        top_performers,
        dimensions=['Power', 'Vitality', 'Spirit', 'Endurance', 'Magic', 'Combat_Score'],
        title='Stat Distribution of Top Performers'
    )
    fig.show()

def analyze_class_stats(df):
    """
    Question 17: Class-Specific Stat Analysis
    Determine optimal stat priorities for each class
    """
    stats = ['Power', 'Vitality', 'Spirit', 'Endurance', 'Magic']
    class_stats = df.groupby('Class')[stats].mean()
    
    # Create radar chart
    fig = go.Figure()
    for class_name in df['Class'].unique():
        values = class_stats.loc[class_name].tolist()
        values.append(values[0])  # Complete the polygon
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=stats + [stats[0]],
            name=class_name
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, class_stats.max().max()])),
        showlegend=True,
        title='Average Stats by Class'
    )
    fig.show()

# Progression Analysis Solutions

def analyze_level_progression(df):
    """
    Question 21: Level Progression Patterns
    Identify common level progression patterns
    """
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='Rank', y='Level', data=df)
    plt.title('Level Distribution by Rank')
    plt.xticks(rotation=45)
    return plt

def skill_acquisition_analysis(df):
    """
    Question 22: Skill Acquisition Rate
    Analyze how quickly characters acquire skills
    """
    plt.figure(figsize=(12, 6))
    sns.regplot(x='Level', y='Total_Skills', data=df, scatter_kws={'alpha':0.5})
    plt.title('Skill Acquisition Rate by Level')
    plt.xlabel('Level')
    plt.ylabel('Total Skills')
    return plt

# Combat Effectiveness Solutions

def analyze_damage_output_factors(df):
    """
    Question 26: Damage Output Factors
    Identify key factors influencing damage output
    """
    from sklearn.ensemble import RandomForestRegressor
    
    # Prepare features
    features = ['Power', 'Vitality', 'Spirit', 'Endurance', 'Magic', 'Level']
    X = df[features]
    y = df['Damage_Output']
    
    # Fit random forest
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(X, y)
    
    # Plot feature importance
    plt.figure(figsize=(10, 6))
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': rf.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    sns.barplot(x='Feature', y='Importance', data=importance_df)
    plt.title('Damage Output - Feature Importance')
    plt.xticks(rotation=45)
    return plt

def analyze_elite_characters(df):
    """
    Question 30: Elite Character Analysis
    Identify characteristics of top-performing characters
    """
    # Calculate overall performance score
    df['Performance_Score'] = (
        df['Damage_Output'].rank(pct=True) * 0.4 +
        df['Survival_Rate'].rank(pct=True) * 0.4 +
        df['Kill_Count'].rank(pct=True) * 0.2
    )
    
    # Get top 5% performers
    top_performers = df.nlargest(int(len(df) * 0.05), 'Performance_Score')
    
    # Create summary statistics
    stats_summary = top_performers.describe()
    
    # Plot distributions of key metrics for elite characters
    fig, axes = plt.subplots(2, 2, figsize=(15, 15))
    
    sns.boxplot(data=top_performers, y='Power', ax=axes[0,0])
    axes[0,0].set_title('Power Distribution - Elite Characters')
    
    sns.boxplot(data=top_performers, y='Damage_Output', ax=axes[0,1])
    axes[0,1].set_title('Damage Output Distribution - Elite Characters')
    
    sns.countplot(data=top_performers, x='Class', ax=axes[1,0])
    axes[1,0].set_title('Class Distribution - Elite Characters')
    axes[1,0].tick_params(axis='x', rotation=45)
    
    sns.countplot(data=top_performers, x='Race', ax=axes[1,1])
    axes[1,1].set_title('Race Distribution - Elite Characters')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    return plt

if __name__ == '__main__':
    # Load the data
    df = load_data()
    
    # Example usage of analysis functions
    plot_race_distribution(df)
    plt.show()
    
    analyze_level_distribution(df)
    plt.show()
    
    plot_core_stats_correlation(df)
    plt.show()
    
    # Additional analysis can be run by calling other functions