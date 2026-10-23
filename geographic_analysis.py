 
# import the module pandas 
import pandas as pd
import numpy as np

df = pd.read_csv("RawData/Traffic Collisions - 4326.csv")

def load_location_data(csv_filepath):
    # Loading .csv file
    df = pd.read_csv(csv_filepath, encoding="utf-8")


    # Filtering the data by the Year 2024-2025
    filter_by_year = df[(df["OCC_YEAR"] >= 2024) & (df["OCC_YEAR"] <= 2025)]

    # Final total filteration 
    required_columns = [
        "OCC_YEAR",
        "NEIGHBOURHOOD_158",
        "BICYCLE",
        "PEDESTRIAN",
        "INJURY_COLLISIONS"
    ]

    final_filteration = filter_by_year[required_columns].copy()

    # Return the final filteration 
    return final_filteration

# # Validating Neighbourhood_158 column 
# validate_neighbourhood = filter_by_year["NEIGHBOURHOOD_158"].value_counts(dropna=False)

# # Validating Bicycle
# validate_bicycle = filter_by_year["BICYCLE"].value_counts(dropna=False)

# # Validating Pedestrian 
# validate_pedestrian = filter_by_year["PEDESTRIAN"].value_counts(dropna=False)

# # Validating Injury Collisions 
# validate_injury_collisions = filter_by_year["INJURY_COLLISIONS"].value_counts(dropna=False)

# # Filtering by valid entries in neighbourhood 
#     filter_by_contains_neighbourhood = filter_by_year[(filter_by_year["NEIGHBOURHOOD_158"] != "NSA") & (filter_by_year["NEIGHBOURHOOD_158"].notna()) ]

# # Filtering by bicycle involved 
#     filter_by_bicycle_involved = filter_by_year[filter_by_year["BICYCLE"] == "YES"]

# # Filtering by pedestrian involved 
#     filter_by_pedestrian_involved = filter_by_year[filter_by_year["PEDESTRIAN"] == "YES"]

# # Filtering by injury collision 
#     filter_by_injury_involved = filter_by_year[filter_by_year["INJURY_COLLISIONS"] == "YES"]

#     print(filter_by_contains_neighbourhood)
#     print(filter_by_bicycle_involved)
#     print(filter_by_pedestrian_involved)
#     print(filter_by_injury_involved)


# # Filtering by missing entry in neighbourhood 
# filter_by_missing_neighbourhood = filter_by_year[(filter_by_year["NEIGHBOURHOOD_158"] == "NSA") | (filter_by_year["NEIGHBOURHOOD_158"].isna()) ]

# # Filtering by motorcycle collision 
#filter_by_motorcycle_collision = filter_by_year[(filter_by_year["MOTORCYCLE"] == "YES") & (filter_by_year["INJURY_COLLISIONS"] == "YES")]

# # Filtering by passengers involved 
#filter_by_passenger_involved = filter_by_year[filter_by_year["PASSENGER"] == "YES"]


#-------- END OF TICKET B1 --------------------

def top_neighbourhoods(df, top_n=10):

    records_without_NSA_and_NaN = df[(df["NEIGHBOURHOOD_158"] != "NSA") & (df["NEIGHBOURHOOD_158"].notna())]
    top_ten_neighbourhood = records_without_NSA_and_NaN["NEIGHBOURHOOD_158"].value_counts()
    return top_ten_neighbourhood.head(top_n)


def pedestrians_involved(df):

    records_with_pedestrian_involved = (df["PEDESTRIAN"] == "YES").sum()
    return records_with_pedestrian_involved

def bicycle_involved(df):

    record_with_bicycle_involved = (df["BICYCLE"] == "YES").sum()
    return record_with_bicycle_involved

def injury_collision_involved(df):

    record_with_injury_collision = (df["INJURY_COLLISIONS"] == "YES").sum()
    return record_with_injury_collision

def classify_location_status(df):
    location_status = np.where((df["NEIGHBOURHOOD_158"] == "NSA") | df["NEIGHBOURHOOD_158"].isna(), "Unknown", "Known")

    df["Location_status"] = location_status

    return df

# For testing if the function produces correct output
if __name__ == "__main__":
    prepared_data = load_location_data(
        "RawData/Traffic Collisions - 4326.csv"
    )
    print(prepared_data.shape)
    result_top = top_neighbourhoods(prepared_data, 10)
    print(result_top)
    result_location_status = classify_location_status(prepared_data)
    print(result_location_status["Location_status"].value_counts())
    result_pedestrian = pedestrians_involved(prepared_data)
    print(result_pedestrian)
    result_bicycle = bicycle_involved(prepared_data)
    print(result_bicycle)
    result_injury = injury_collision_involved(prepared_data)
    print(result_injury)
    