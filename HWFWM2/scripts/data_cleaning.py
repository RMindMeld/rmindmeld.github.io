import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from pathlib import Path

def load_raw_data(data_dir='../data'):
    """Load the raw dataset."""
    raw_data_path = Path(data_dir) / 'raw_data.csv'
    if not raw_data_path.exists():
        raise FileNotFoundError(f"Raw data file not found at {raw_data_path}")
    return pd.read_csv(raw_data_path)

def handle_missing_values(df):
    """Handle any missing values in the dataset."""
    # Check for missing values
    missing_stats = df.isnull().sum()
    
    # Fill numeric columns with median
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
    
    # Fill categorical columns with mode
    categorical_columns = df.select_dtypes(exclude=[np.number]).columns
    df[categorical_columns] = df[categorical_columns].fillna(df[categorical_columns].mode().iloc[0])
    
    return df

def handle_outliers(df, columns, n_std=3):
    """
    Handle outliers using the z-score method.
    Parameters:
        df: DataFrame
        columns: List of columns to check for outliers
        n_std: Number of standard deviations to use as threshold
    """
    for column in columns:
        if column in df.select_dtypes(include=[np.number]).columns:
            mean = df[column].mean()
            std = df[column].std()
            
            # Calculate z-scores
            z_scores = np.abs((df[column] - mean) / std)
            
            # Cap values at n standard deviations
            df.loc[z_scores > n_std, column] = df[column].clip(
                lower=mean - n_std * std,
                upper=mean + n_std * std
            )
    
    return df

def create_derived_features(df):
    """Create new features from existing ones."""
    # Combat efficiency ratio
    df['Combat_Efficiency'] = df['Damage_Output'] / (df['Power'] + 1)  # Add 1 to avoid division by zero
    
    # Skill diversity score
    skill_columns = ['Common_Skills', 'Uncommon_Skills', 'Rare_Skills', 'Epic_Skills', 'Legendary_Skills']
    df['Skill_Diversity'] = df[skill_columns].apply(lambda x: -sum((x/x.sum()) * np.log2(x/x.sum() + 1e-10)), axis=1)
    
    # Progression rate
    df['Progression_Rate'] = df['Level'] / df.groupby('Rank')['Level'].transform('mean')
    
    # Overall power score
    df['Power_Score'] = (
        df['Power'] * 0.3 +
        df['Vitality'] * 0.2 +
        df['Spirit'] * 0.15 +
        df['Endurance'] * 0.15 +
        df['Magic'] * 0.2
    )
    
    # Survival efficiency
    df['Survival_Efficiency'] = df['Survival_Rate'] / (df['Vitality'] + df['Endurance'])
    
    return df

def normalize_numeric_features(df):
    """Normalize numeric features using StandardScaler."""
    scaler = StandardScaler()
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    
    # Create normalized versions of numeric columns
    normalized_data = scaler.fit_transform(df[numeric_columns])
    normalized_df = pd.DataFrame(
        normalized_data,
        columns=[f"{col}_normalized" for col in numeric_columns],
        index=df.index
    )
    
    # Add normalized columns to original dataframe
    return pd.concat([df, normalized_df], axis=1)

def encode_categorical_features(df):
    """Encode categorical features using one-hot encoding."""
    categorical_columns = ['Race', 'Class', 'Origin_World', 'Rank', 'Evolution_Stage']
    
    # Create one-hot encoded versions of categorical columns
    encoded_df = pd.get_dummies(
        df[categorical_columns],
        prefix=categorical_columns,
        prefix_sep='_'
    )
    
    # Add encoded columns to original dataframe
    return pd.concat([df, encoded_df], axis=1)

def clean_data(df):
    """
    Main function to clean and process the data.
    Applies all cleaning steps in sequence.
    """
    # Handle missing values
    df = handle_missing_values(df)
    
    # Handle outliers in numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df = handle_outliers(df, numeric_columns)
    
    # Create derived features
    df = create_derived_features(df)
    
    # Normalize numeric features
    df = normalize_numeric_features(df)
    
    # Encode categorical features
    df = encode_categorical_features(df)
    
    return df

def save_processed_data(df, data_dir='../data'):
    """Save the processed dataset."""
    output_path = Path(data_dir) / 'processed_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Processed data saved to {output_path}")
    
    # Save data description
    description_path = Path(data_dir) / 'data_description.txt'
    with open(description_path, 'w') as f:
        f.write("Dataset Summary:\n\n")
        f.write(f"Total Records: {len(df)}\n")
        f.write(f"Total Features: {len(df.columns)}\n\n")
        f.write("Numeric Features Summary:\n")
        f.write(df.describe().to_string())
        f.write("\n\nFeature Names:\n")
        f.write("\n".join(df.columns))

def main():
    """Main execution function."""
    print("Starting data cleaning process...")
    
    try:
        # Load raw data
        df = load_raw_data()
        print("Raw data loaded successfully")
        
        # Clean and process data
        processed_df = clean_data(df)
        print("Data cleaning completed")
        
        # Save processed data
        save_processed_data(processed_df)
        print("Data cleaning process completed successfully")
        
    except Exception as e:
        print(f"Error during data cleaning: {str(e)}")
        raise

if __name__ == "__main__":
    main()