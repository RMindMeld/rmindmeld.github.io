# HWFWM Dataset Data Dictionary

## Core Statistics

| Variable | Type | Description | Range | Distribution |
|----------|------|-------------|--------|--------------|
| Power | Float | Represents raw physical and magical power | 0-100 | Normal distribution (mean=60, std=15) |
| Vitality | Float | Represents health and endurance | 0-100 | Normal distribution (mean=55, std=12) |
| Speed | Float | Represents movement and action speed | 0-100 | Normal distribution (mean=50, std=10) |
| Recovery | Float | Represents healing and regeneration rate | 0-100 | Normal distribution (mean=45, std=8) |
| Control | Float | Represents magical control and precision | 0-100 | Normal distribution (mean=40, std=7) |

## Derived Statistics

| Variable | Type | Description | Calculation |
|----------|------|-------------|-------------|
| Health | Float | Total health points | (Vitality × 10) + (Level × 5) + random noise |
| Mana | Float | Total mana points | (Control × 8) + (Level × 3) + random noise |
| Attack | Float | Attack power | (Power × 2) + (Level × 2) + random noise |
| Defense | Float | Defense power | (Vitality × 1.5) + (Level × 1.5) + random noise |

## Character Information

| Variable | Type | Description | Values/Range |
|----------|------|-------------|--------------|
| Essence | Float | Character's essence rating | 1-10 (right-skewed gamma distribution) |
| Class | String | Character's primary role | Fighter, Mage, Healer, Tank, Support, Scout, Summoner, Controller, Buffer, Debuffer |
| Achievement_Rank | String | Character's achievement rank | Bronze, Silver, Gold, Platinum, Diamond, Ruby, Sapphire, Emerald, Master, Grandmaster |
| Level | Integer | Character's current level | 1-100 |
| Experience | Integer | Total experience points | Level × 1000 + random(0-999) |
| Skills | List | List of character's skills | 5 random skills from skill pool |

## Correlations

The core statistics have the following correlation matrix:

```
           Power  Vitality  Speed  Recovery  Control
Power      1.0    0.6      0.4    0.3       0.2
Vitality   0.6    1.0      0.5    0.4       0.3
Speed      0.4    0.5      1.0    0.7       0.4
Recovery   0.3    0.4      0.7    1.0       0.5
Control    0.2    0.3      0.4    0.5       1.0
```

## Distribution Notes

1. Core stats follow normal distributions with different means and standard deviations
2. Essence ratings follow a gamma distribution, skewed towards lower values
3. Achievement ranks follow a beta distribution, favoring lower ranks
4. Class distribution is weighted, with common classes (Fighter, Mage) being more frequent
5. Skills are randomly selected without replacement from a pool of 20 possible skills
6. Derived stats include random noise to simulate natural variation

## Data Generation Details

- Dataset is generated using Python with numpy, pandas, and scipy
- All negative values in derived statistics are clipped to 0
- Core statistics are generated using Cholesky decomposition to maintain correlation structure
- Each character is guaranteed to have exactly 5 unique skills