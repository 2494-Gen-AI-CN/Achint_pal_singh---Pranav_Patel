import matplotlib.pyplot as plt
from geographic_analysis import load_location_data
from geographic_analysis import top_neighbourhoods

df = load_location_data("RawData/Traffic Collisions - 4326.csv")

top_10 = top_neighbourhoods(df, 10)

plt.figure(figsize=(14,7))

plt.subplots_adjust(left=0.30)


plt.barh(top_10.index, top_10.values)

plt.gca().invert_yaxis()

plt.title("Top 10 Neighbourhood with most collision (2024-2025)")

plt.ylabel("Neighbourhood in Toronto")

plt.xlabel("No of Collisions")

plt.show()