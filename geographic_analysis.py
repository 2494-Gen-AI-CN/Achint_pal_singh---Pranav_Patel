 
# import the module pandas 
import pandas as pd

# Loading .csv file
df = pd.read_csv("RawData/Traffic Collisions - 4326.csv", encoding="utf-8")

# Filtering the data by the Year 2024-2025
filter_by_year = df[(df["OCC_YEAR"] >= 2024) & (df["OCC_YEAR"] <= 2025)]

# Filtering the data by missing entry in neighbourhood 
filter_by_missing_neighbourhood = filter_by_year[filter_by_year["NEIGHBOURHOOD_158"] == "NSA"]

# Filtering the data by valid entries in neighbourhood 
filter_by_contains_neighbourhood = filter_by_year[filter_by_year["NEIGHBOURHOOD_158"] != "NSA"]

# Filtering the data by motorcycle collision 
filter_by_motorcycle_collision = filter_by_year[(filter_by_year["MOTORCYCLE"] == "YES") & (filter_by_year["INJURY_COLLISIONS"] == "YES")]

print(filter_by_motorcycle_collision)