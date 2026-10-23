import matplotlib.pyplot as plt
from geographic_analysis import load_location_data
from geographic_analysis import top_neighbourhoods

df = load_location_data("RawData/Traffic Collisions - 4326.csv")

top_10 = top_neighbourhoods(df, 10)

plt.barh(top_10.index, top_10.values)

plt.show()