import gpxpy
import gpxpy.gpx
from math import radians, cos, sin, asin, sqrt
import sys
import requests
import os
from dotenv import load_dotenv
import inquirer

load_dotenv()


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


bearer_token = os.environ.get('STRAVA_TOKEN')


def request_gpx(route_id):
    url = f"https://www.strava.com/api/v3/routes/{route_id}/export_gpx"
    headers = {
        'Authorization': f'Bearer {bearer_token}'
    }
    response = requests.request("GET", url, headers=headers)
    return response.text


route_id = sys.argv[1]
distance_to_check = sys.argv[2]

gpx_file = request_gpx(route_id)
gpx = gpxpy.parse(gpx_file)


distance_elevation_list = [{'Distance': 0.0, 'Elevation': 0.0}]

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


# A binary search to find the entry that has the distance closest to the distance entered.
def find_closest_entry(list: list[dict[str, float]], search_item: float):
    found = False
    search_list = list

    while found is False:
        middle = round(len(search_list) / 2)
        if (search_list[middle] == search_item or len(search_list) == 1):
            found = True
            break

        if (len(search_list) == 2):
            if (abs(search_list[0]["Distance"] - search_item) < abs(search_list[1]["Distance"] - search_item)):
                search_list = search_list[:1]
            else:
                search_list = search_list[1:]
            break

        if (search_list[middle]["Distance"] > search_item):
            search_list = search_list[:middle]
        else:
            search_list = search_list[middle:]

    return search_list[0]


print("Total Distance: {distance}km".format(distance=round(distance, 2)))
print("Total Elevation Gain: {elevation}m".format(
    elevation=round(elevation, 2)))

should_break = False
while not should_break:
    distance_question = inquirer.Text('distance', message="Distance"),
    distance = inquirer.prompt(distance_question)

    if distance["distance"] == "stop":
        should_break = True
        break

    closest_entry = find_closest_entry(
        distance_elevation_list, float(distance["distance"]))
    print("Elevation gain at {closest_distance}km is {final_elevation}m".format(
        closest_distance=round(closest_entry["Distance"], 2), final_elevation=round(closest_entry["Elevation"], 2)))
