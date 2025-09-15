import pandas as pd
import os

# Read the training data
df = pd.read_csv("app/train_data.csv")

# Create the test_data directory if it doesn't exist
os.makedirs("app/test_data", exist_ok=True)

# Randomly sample 20% of the data for testing
test_df = df.sample(frac=0.2, random_state=42)

# Save the test data to app/test_data/test_data.csv
test_df.to_csv("app/test_data/test_data.csv", index=False)

print("Test data generated and saved to app/test_data/test_data.csv")