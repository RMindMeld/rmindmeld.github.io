# HWFWM Dataset Analysis Questions

## Exploratory Data Analysis (10 Questions)

1. **Character Race Distribution**
   - Objective: Analyze the distribution of characters across different races
   - Variables: Race
   - Visualization: Pie chart or bar plot
   - Complexity: Basic

2. **Level Distribution Analysis**
   - Objective: Examine the distribution of character levels
   - Variables: Level
   - Visualization: Histogram with kernel density estimation
   - Complexity: Basic

3. **Core Stats Correlation Matrix**
   - Objective: Identify relationships between core stats
   - Variables: Power, Vitality, Spirit, Endurance, Magic
   - Visualization: Heatmap correlation matrix
   - Complexity: Intermediate

4. **Skill Rarity Distribution**
   - Objective: Analyze the distribution of skill rarities across characters
   - Variables: Common_Skills, Uncommon_Skills, Rare_Skills, Epic_Skills, Legendary_Skills
   - Visualization: Stacked bar chart
   - Complexity: Basic

5. **Origin World Character Composition**
   - Objective: Compare character distributions across different origin worlds
   - Variables: Origin_World, Race, Class
   - Visualization: Grouped bar chart
   - Complexity: Intermediate

6. **Evolution Stage Progression**
   - Objective: Analyze the relationship between level and evolution stages
   - Variables: Level, Evolution_Stage
   - Visualization: Box plot
   - Complexity: Basic

7. **Class Distribution by Race**
   - Objective: Examine class preferences across different races
   - Variables: Race, Class
   - Visualization: Heatmap
   - Complexity: Intermediate

8. **Total Skills vs Level Relationship**
   - Objective: Analyze how total skills scale with level
   - Variables: Total_Skills, Level
   - Visualization: Scatter plot with trend line
   - Complexity: Basic

9. **Combat Metrics Overview**
   - Objective: Compare distributions of different combat metrics
   - Variables: Damage_Output, Survival_Rate, Kill_Count
   - Visualization: Multiple box plots
   - Complexity: Intermediate

10. **Rank Distribution by Origin World**
    - Objective: Compare rank distributions across origin worlds
    - Variables: Rank, Origin_World
    - Visualization: Stacked percentage bar chart
    - Complexity: Intermediate

## Statistical Analysis (5 Questions)

11. **Power Level Statistical Tests**
    - Objective: Test if power levels significantly differ between races
    - Variables: Power, Race
    - Visualization: Box plot with statistical test results
    - Complexity: Advanced

12. **Survival Rate Factors**
    - Objective: Perform multiple regression to identify key survival rate factors
    - Variables: Survival_Rate, Vitality, Endurance, Level, Rank
    - Visualization: Coefficient plot
    - Complexity: Advanced

13. **Skill Count Distribution Test**
    - Objective: Test if skill counts follow expected theoretical distribution
    - Variables: Total_Skills
    - Visualization: Q-Q plot
    - Complexity: Advanced

14. **Combat Effectiveness Clustering**
    - Objective: Identify natural groupings based on combat metrics
    - Variables: Damage_Output, Survival_Rate, Kill_Count
    - Visualization: K-means clustering plot
    - Complexity: Advanced

15. **Evolution Stage Transition Analysis**
    - Objective: Analyze the probability of evolution stage transitions
    - Variables: Level, Evolution_Stage
    - Visualization: Transition probability matrix heatmap
    - Complexity: Advanced

## Character Optimization (5 Questions)

16. **Optimal Stat Distribution**
    - Objective: Identify most effective stat distributions for combat
    - Variables: All core stats, Combat metrics
    - Visualization: Parallel coordinates plot
    - Complexity: Advanced

17. **Class-Specific Stat Analysis**
    - Objective: Determine optimal stat priorities for each class
    - Variables: Class, All core stats
    - Visualization: Radar charts by class
    - Complexity: Intermediate

18. **Skill Composition Impact**
    - Objective: Analyze how skill rarity composition affects combat performance
    - Variables: Skill distribution, Combat metrics
    - Visualization: Scatter plot matrix
    - Complexity: Advanced

19. **Race-Class Combination Analysis**
    - Objective: Identify most effective race-class combinations
    - Variables: Race, Class, Combat metrics
    - Visualization: Performance matrix heatmap
    - Complexity: Intermediate

20. **Evolution Stage Optimization**
    - Objective: Analyze optimal timing for evolution stage transitions
    - Variables: Level, Evolution_Stage, Combat metrics
    - Visualization: Line plot with performance indicators
    - Complexity: Advanced

## Progression Analysis (5 Questions)

21. **Level Progression Patterns**
    - Objective: Identify common level progression patterns
    - Variables: Level, Rank, Evolution_Stage
    - Visualization: Sankey diagram
    - Complexity: Advanced

22. **Skill Acquisition Rate**
    - Objective: Analyze how quickly characters acquire skills
    - Variables: Level, Total_Skills, Rank
    - Visualization: Line plot with confidence intervals
    - Complexity: Intermediate

23. **Power Scaling Analysis**
    - Objective: Examine how power scales with progression metrics
    - Variables: Power, Level, Rank, Evolution_Stage
    - Visualization: Multi-line plot
    - Complexity: Intermediate

24. **Rank Transition Analysis**
    - Objective: Analyze typical rank transition points
    - Variables: Level, Rank
    - Visualization: Violin plot
    - Complexity: Intermediate

25. **Skill Rarity Progression**
    - Objective: Track how skill rarity distribution changes with progression
    - Variables: Level, All skill rarity counts
    - Visualization: Stacked area chart
    - Complexity: Advanced

## Combat Effectiveness (5 Questions)

26. **Damage Output Factors**
    - Objective: Identify key factors influencing damage output
    - Variables: Damage_Output, All core stats, Level
    - Visualization: Feature importance plot
    - Complexity: Advanced

27. **Survival Analysis**
    - Objective: Analyze factors contributing to survival rate
    - Variables: Survival_Rate, All core stats, Skills
    - Visualization: Forest plot
    - Complexity: Advanced

28. **Kill Count Distribution**
    - Objective: Analyze kill count patterns across different character types
    - Variables: Kill_Count, Class, Rank
    - Visualization: Violin plot with box plot overlay
    - Complexity: Intermediate

29. **Combat Efficiency Ratio**
    - Objective: Calculate and analyze combat efficiency (damage/survival ratio)
    - Variables: Damage_Output, Survival_Rate
    - Visualization: Scatter plot with efficiency contours
    - Complexity: Advanced

30. **Elite Character Analysis**
    - Objective: Identify characteristics of top-performing characters
    - Variables: All combat metrics, All character attributes
    - Visualization: Parallel coordinates plot for top 5%
    - Complexity: Advanced