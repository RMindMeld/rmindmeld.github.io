# HWFWM Dataset Data Dictionary

## Overview
This document provides detailed information about the variables in the He Who Fights With Monsters (HWFWM) character dataset. The dataset contains information about character attributes, progression metrics, combat statistics, and skill distributions.

## Character Attributes

### Basic Information
| Variable | Type | Description | Possible Values |
|----------|------|-------------|-----------------|
| Name | String | Character's full name | Generated names |
| Race | String | Character's species/race | Human, Beast, Spirit, Construct, Mythical |
| Class | String | Character's combat role/specialization | Warrior, Mage, Rogue, Healer, Tank, Support |
| Origin_World | String | Character's world of origin | Earth, Pallimustus, Shadow Realm, Crystal Sea, Waste |

### Progression Metrics
| Variable | Type | Description | Range/Values |
|----------|------|-------------|--------------|
| Level | Integer | Character's current level | 1-100 |
| Rank | String | Character's power rank | Iron, Bronze, Silver, Gold, Diamond, Platinum |
| Evolution_Stage | String | Character's evolutionary stage | Initiate, Awakened, Core, Essence, Transcendent |

### Core Stats
| Variable | Type | Description | Range |
|----------|------|-------------|--------|
| Power | Integer | Raw offensive capability | ≥1 |
| Vitality | Integer | Health and life force | ≥1 |
| Spirit | Integer | Mental and magical resilience | ≥1 |
| Endurance | Integer | Stamina and physical resilience | ≥1 |
| Magic | Integer | Magical power and control | ≥1 |

### Combat Metrics
| Variable | Type | Description | Range |
|----------|------|-------------|--------|
| Damage_Output | Integer | Average damage dealt | ≥0 |
| Survival_Rate | Integer | Percentage of successful combat survival | 0-100 |
| Kill_Count | Integer | Number of defeated opponents | ≥0 |

### Skill Distribution
| Variable | Type | Description | Range |
|----------|------|-------------|--------|
| Total_Skills | Integer | Total number of skills possessed | ≥0 |
| Common_Skills | Integer | Number of common rarity skills | ≥0 |
| Uncommon_Skills | Integer | Number of uncommon rarity skills | ≥0 |
| Rare_Skills | Integer | Number of rare rarity skills | ≥0 |
| Epic_Skills | Integer | Number of epic rarity skills | ≥0 |
| Legendary_Skills | Integer | Number of legendary rarity skills | ≥0 |

## Statistical Distributions and Correlations

### Level Distribution
- Follows a normal distribution with mean 30 and standard deviation 10
- Clamped between 1 and 100
- Influences rank and evolution stage progression

### Rank Progression
- Tied to level progression (roughly every 20 levels)
- Higher ranks correlate with higher core stats
- Influences skill acquisition rate

### Core Stats Generation
- Base values follow normal distributions
- Scaled by rank and level
- Minimum value of 1 enforced
- Correlations:
  - Power influences Damage_Output and Kill_Count
  - Vitality influences Survival_Rate

### Skill Distribution
- Total skills follow normal distribution based on level and rank
- Rarity distribution:
  - Common: 50%
  - Uncommon: 30%
  - Rare: 15%
  - Epic: 4%
  - Legendary: 1%

### Combat Metrics
- Damage_Output: Influenced by Power and level
- Survival_Rate: Influenced by Vitality
- Kill_Count: Follows exponential distribution based on Power and level

## Data Generation Methodology

### Character Generation
1. Generate level following normal distribution
2. Determine rank and evolution stage based on level
3. Generate core stats scaled by level and rank
4. Calculate combat metrics based on core stats
5. Generate skills following rarity distribution
6. Add controlled random noise to create realistic variations

### Outlier Generation
- 5% of characters receive multiplied stats to create natural outliers
- Multipliers range from 2x to 5x on random numeric attributes

### Processed Data
The processed dataset includes additional normalized versions of numeric columns:
- Column_normalized = (value - mean) / standard_deviation