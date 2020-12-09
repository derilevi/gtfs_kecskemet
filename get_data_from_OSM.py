import json
import requests

api_url = "https://www.openstreetmap.org/api/0.6/relation/#id/full.json"
mapping_update = False

stops = {}
stops_out = {}
shapes = {}

source_json = open("data/route_OSM_stops_mapping.json","r",encoding="utf8")
routes = json.load(source_json)
source_json.close()

for route_id, route_data in routes.items():
	print(route_id)
	ways = []
	way_nodes = []
	shapes[route_data["OSM"]] = []
	routes[route_id]["stops"] = []
	url = api_url.replace("#id", str(route_data["OSM"]))
	req = requests.get(url)
	data = req.json()
	for member in data["elements"][-1]["members"]:
		# get route stops
		if member["type"] == "node":
			routes[route_id]["stops"].append(member["ref"])
			for item in data["elements"]:
				if item["id"] == member["ref"]:
					stops[item["id"]] = item
		# get route ways
		if member["type"] == "way":
			for item in data["elements"]:
				if item["id"] == member["ref"]:
					ways.append(item)
	# get shape coords from ways
	first_way = True
	for way in ways:
		if len(way_nodes) > 0:
			# check way direction
			if way_nodes[-1] != way["nodes"][0]:
				if way_nodes[-1] == way["nodes"][::-1][0]:
					way["nodes"] = way["nodes"][::-1]
				elif first_way and way_nodes[::-1][-1] == way["nodes"][0]:
					way_nodes = way_nodes[::-1]
				elif first_way and way_nodes[::-1][-1] == way["nodes"][::-1][0]:
					way_nodes = way_nodes[::-1]
					way["nodes"] = way["nodes"][::-1]
				else:
					print("ERROR in OSM relation:", route_data["OSM"])
			if first_way == True:
				first_way = False
		for way_node in way["nodes"]:
			if len(way_nodes) == 0 or way_nodes[-1] != way_node:
				way_nodes.append(way_node)
	for node in way_nodes:
		for item in data["elements"]:
			if item["id"] == node:
				shapes[route_data["OSM"]].append([item["lat"], item["lon"]])

if mapping_update == True:
	f = open("data/route_OSM_stops_mapping.json","w",encoding="utf8")
	json.dump(routes, f, indent=2)
	f.close()

for stop_id, stop_data in sorted(stops.items()):
	stop_name = stop_data["tags"]["name"]
	stop_lat = str(stop_data["lat"])
	stop_lon = str(stop_data["lon"])
	stops_out[stop_id] = {"stop_name": stop_name, "stop_lat": stop_lat, "stop_lon": stop_lon}
stops_json = open("data/stops.json","w",encoding="utf8")
json.dump(stops_out, stops_json, ensure_ascii=False, indent=2)
stops_json.close()

shapes_json = open("data/shapes.json","w",encoding="utf8")
json.dump(shapes, shapes_json, ensure_ascii=False, indent=2)
shapes_json.close()
