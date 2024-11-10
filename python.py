import folium

# Create a map centered around Paris, France
m = folium.Map(location=[48.8566, 2.3522], zoom_start=6)

# Save the map as an HTML file
m.save('map.html')