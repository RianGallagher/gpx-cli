import gpxpy
import gpxpy.gpx
from math import radians, cos, sin, asin, sqrt
import sys


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    r = 6371
    return c * r

# Parsing an existing file:
# -------------------------


gpx_file = open('test.gpx', 'r')
gpx = gpxpy.parse(gpx_file)

distance_to_check = sys.argv[1]

distance_elevation_list = [{'Distance': 0, 'Elevation': 0}]

distance = 0
elevation = 0

closest_difference = float("inf")
closest_distance = 0
final_elevation = 0

for track in gpx.tracks:
    for segment in track.segments:
        points = segment.points
        for i in range(0, len(points)):
            item1 = points[i]
            if i + 1 < len(points):
                item2 = points[i + 1]
                # Do something with item1 and item2
                hav = haversine(item1.longitude, item1.latitude,
                                item2.longitude, item2.latitude)
                # print(hav)
                distance += hav

                elevation_difference = item2.elevation - item1.elevation

                if elevation_difference > 0:
                    elevation += elevation_difference

                distance_elevation_list.append(
                    {'Distance': distance, 'Elevation': elevation})

                current_differnece = abs(distance - float(distance_to_check))
                if current_differnece < closest_difference:
                    closest_difference = current_differnece
                    closest_distance = distance
                    final_elevation = elevation


# print(distance_elevation_list)
print("Elevation gain at {closest_distance}km is {final_elevation}m".format(
    closest_distance=round(closest_distance, 2), final_elevation=round(final_elevation, 2)))
# print("Closest elevation: {final_elevation}m".format(
#     final_elevation=round(final_elevation, 2)))

print("Total Distance: {distance}km".format(distance=round(distance, 2)))
print("Total Elevation Gain: {elevation}m".format(elevation=round(elevation, 2)))
