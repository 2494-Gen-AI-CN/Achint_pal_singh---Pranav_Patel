 
# import the module pandas 
import pandas as pd


# Loading .csv file
df = pd.read_csv("RawData/Traffic Collisions - 4326.csv", encoding="utf-8")


# Filtering the data by the Year 2024-2025
filter_by_year = df[(df["OCC_YEAR"] >= 2024) & (df["OCC_YEAR"] <= 2025)]

# Validating Neighbourhood_158 column 
validate_neighbourhood = filter_by_year["NEIGHBOURHOOD_158"].value_counts(dropna=False)

# Validating Bicycle
validate_bicycle = filter_by_year["BICYCLE"].value_counts(dropna=False)

# Validating Pedestrian 
validate_pedestrian = filter_by_year["PEDESTRIAN"].value_counts(dropna=False)

# Validating Injury Collisions 
validate_injury_collisions = filter_by_year["INJURY_COLLISIONS"].value_counts(dropna=False)

print(validate_neighbourhood)
print(validate_bicycle)
print(validate_pedestrian)
print(validate_injury_collisions)


# Filtering by valid entries in neighbourhood 
filter_by_contains_neighbourhood = filter_by_year[(filter_by_year["NEIGHBOURHOOD_158"] != "NSA") & (filter_by_year["NEIGHBOURHOOD_158"].notna()) ]

# Filtering by bicycle involved 
filter_by_bicycle_involved = filter_by_year[filter_by_year["BICYCLE"] == "YES"]

# Filtering by pedestrian involved 
filter_by_pedestrian_involved = filter_by_year[filter_by_year["PEDESTRIAN"] == "YES"]

# Filtering by injury collision 
filter_by_injury_involved = filter_by_year[filter_by_year["INJURY_COLLISIONS"] == "YES"]

# Final total filteration 
required_columns = [
    "OCC_YEAR",
    "NEIGHBOURHOOD_158",
    "BICYCLE",
    "PEDESTRIAN",
    "INJURY_COLLISIONS"
]

final_filteration = filter_by_year[required_columns].copy()

print(final_filteration)


# Filtering by missing entry in neighbourhood 
# filter_by_missing_neighbourhood = filter_by_year[(filter_by_year["NEIGHBOURHOOD_158"] == "NSA") | (filter_by_year["NEIGHBOURHOOD_158"].isna()) ]

# Filtering by motorcycle collision 
#filter_by_motorcycle_collision = filter_by_year[(filter_by_year["MOTORCYCLE"] == "YES") & (filter_by_year["INJURY_COLLISIONS"] == "YES")]

# Filtering by passengers involved 
#filter_by_passenger_involved = filter_by_year[filter_by_year["PASSENGER"] == "YES"]

