import matplotlib.pyplot as plt
from geographic_analysis import load_location_data
from geographic_analysis import top_neighbourhoods
from geographic_analysis import pedestrians_involved
from geographic_analysis import bicycle_involved
from geographic_analysis import injury_collision_involved

def plot_top_neighbourhood(df):

    top_10 = top_neighbourhoods(df, 10)

    plt.figure(figsize=(14,7))

    plt.subplots_adjust(left=0.30)

    bar = plt.barh(top_10.index, top_10.values)

    plt.gca().invert_yaxis()

    plt.title("Top 10 Toronto Neighbourhood by Traffic Collisions (2024-2025)")

    plt.ylabel("Neighbourhood in Toronto")

    plt.xlabel("Number of Collisions")

    plt.gca().bar_label(bar, padding=3)

    plt.show()


def plot_pedestrian_and_bicycle_involved(df):

    pedestrian = pedestrians_involved(df)
    bicycle = bicycle_involved(df)
    
    plt.figure(figsize=(14,7))

    plt.gca().invert_yaxis()

    categories = ["Pedestrain", "Bicycle"]
    value = [pedestrian, bicycle]
    
    bar = plt.barh(categories, value)
    
    plt.title("Pedestrian and Bicycle involved in Traffic Collisions (2024-2025)")
    
    plt.ylabel("Type of Road User")
    
    plt.xlabel("Number of Collisions")
    
    plt.gca().bar_label(bar, padding=3)
    
    plt.show()

def plot_injury_and_non_injury(df):

    injury = injury_collision_involved(df)
    total_raw_data = len(df)
    non_injury = total_raw_data - injury

    plt.figure(figsize=(14,7))

    categories = ["Injury", "Non Injury"]
    value = [injury, non_injury]

    bar = plt.barh(categories, value)

    plt.title("Injury vs Non-Injury in Traffic Collisions (2024-2025)")

    plt.ylabel("Injured vs Non-Injured")

    plt.xlabel("Number of Collisions")

    plt.gca().bar_label(bar, padding=3)

    plt.margins(0.1)

    plt.show()



if __name__ == "__main__":

    df = load_location_data("RawData/Traffic Collisions - 4326.csv")

    plot_top_neighbourhood(df)
    plot_pedestrian_and_bicycle_involved(df)
    plot_injury_and_non_injury(df)
