import datetime
import json
import os
import zipfile

def create_agency():
	source_json = open("data/agency.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	agency_txt = open("out/agency.txt","w",encoding="utf8")
	agency_txt.write("agency_id,agency_name,agency_url,agency_timezone,agency_lang,agency_phone\n")
	for item_key, item in data.items():
		agency_txt.write(",".join([item_key, item["agency_name"], item["agency_url"], item["agency_timezone"],
									item["agency_lang"], item["agency_phone"]])+"\n")
	agency_txt.close()

def create_calendar():
	source_json = open("data/calendar.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	calendar_txt = open("out/calendar.txt","w",encoding="utf8")
	calendar_txt.write("service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n")
	for item_key, item in data.items():
		calendar_txt.write(",".join([item_key, str(item["monday"]), str(item["tuesday"]), str(item["wednesday"]),
									str(item["thursday"]), str(item["friday"]), str(item["saturday"]), str(item["sunday"]),
									str(item["start_date"]), str(item["end_date"])])+"\n")
	calendar_txt.close()

def create_calendar_dates():
	source_json = open("data/calendar_dates.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	calendar_dates_txt = open("out/calendar_dates.txt","w",encoding="utf8")
	calendar_dates_txt.write("service_id,date,exception_type\n")
	for item_key, item in data.items():
		for service_id in item["add"]:
			calendar_dates_txt.write(",".join([service_id, item_key, "1"])+"\n")
		for service_id in item["remove"]:
			calendar_dates_txt.write(",".join([service_id, item_key, "2"])+"\n")
	calendar_dates_txt.close()

def create_routes():
	source_json = open("data/routes.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	routes_txt = open("out/routes.txt","w",encoding="utf8")
	routes_txt.write("agency_id,route_id,route_short_name,route_long_name,route_type\n")
	for item_key, item in data.items():
		routes_txt.write(",".join([item["agency"], item_key, str(item["route_short_name"]), "\""+item["route_long_name"]+"\"",
									str(item["route_type"])])+"\n")
	routes_txt.close()

def create_shapes():
	source_json = open("data/shapes.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	shapes_txt = open("out/shapes.txt","w",encoding="utf8")
	shapes_txt.write("shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n")
	for item_key, item in data.items():
		seq = 0
		for coord in item:
			shapes_txt.write(",".join([item_key, str(coord[0]), str(coord[1]), str(seq)])+"\n")
			seq += 1
	shapes_txt.close()

def create_stops():
	source_json = open("data/stops.json","r",encoding="utf8")
	data = json.load(source_json)
	source_json.close()
	stops_txt = open("out/stops.txt","w",encoding="utf8")
	stops_txt.write("stop_id,stop_name,stop_lat,stop_lon\n")
	for item_key, item in data.items():
		stops_txt.write(",".join([item_key, "\""+item["stop_name"]+"\"", str(item["stop_lat"]), str(item["stop_lon"])])+"\n")
	stops_txt.close()

def create_stop_times_trips():
	old_version_include = False
	old_version_date = "20201121"
	
	travel_times_json = open("data/travel_times.json","r",encoding="utf8")
	start_times_json = open("data/start_times.json","r",encoding="utf8")
	stops_json = open("data/route_OSM_stops_mapping.json","r",encoding="utf8")
	
	travel_times_dict = json.load(travel_times_json)
	start_times_dict = json.load(start_times_json)
	stops_dict = json.load(stops_json)
	
	travel_times_json.close()
	start_times_json.close()
	stops_json.close()
	
	if old_version_include:
		travel_times_old_json = open("data/travel_times_"+old_version_date+".json","r",encoding="utf8")
		start_times_old_json = open("data/start_times_"+old_version_date+".json","r",encoding="utf8")
		travel_times_old_dict = json.load(travel_times_old_json)
		start_times_old_dict = json.load(start_times_old_json)
		travel_times_old_json.close()
		start_times_old_json.close()
	
	trips_txt = open("out/trips.txt","w",encoding="utf8")
	trips_txt.write("route_id,service_id,trip_id,trip_headsign,direction_id,shape_id\n")
	stop_times_txt = open("out/stop_times.txt","w",encoding="utf8")
	stop_times_txt.write("trip_id,arrival_time,departure_time,stop_id,stop_sequence,stop_headsign\n")
	
	route_id = "0000"
	for route, route_data in start_times_dict.items():
		if "v" in route:
			direction_id = "1"
		else:
			direction_id = "0"
		if old_version_include:
			keys = ["MN", "SZ_MSZ"]
			if route in start_times_old_dict:
				for k in keys:
					if k in start_times_old_dict[route]:
						route_data[k+"_"+old_version_date] = start_times_old_dict[route][k]
				if "EXTRA_20201205" in start_times_old_dict[route]:
					route_data["EXTRA_20201205"] = start_times_old_dict[route]["EXTRA_20201205"]
		route_id_prev = route_id
		route_id = stops_dict[route]["route_id"]
		shape_id = str(stops_dict[route]["OSM"])
		trip_headsign = stops_dict[route]["headsign"]
		if route_id != route_id_prev:
			trip_seq = 1
		if len(stops_dict[route]["stops"]) != len(travel_times_dict[route]):
			print(route, "missing or extra stop in route, skipping...")
			continue
		for service_id, service_start_times in route_data.items():
			for start_time in service_start_times:
				trip_id = route_id + format(trip_seq, "04d")
				trips_txt.write(",".join([route_id, service_id, trip_id, trip_headsign, direction_id, shape_id])+"\n")
				start_time = datetime.datetime.strptime(start_time, "%H:%M")
				stop_seq = 0
				stop_headsign = ""
				for stop in stops_dict[route]["stops"]:
					if old_version_include and old_version_date in service_id:
						stop_time = start_time + datetime.timedelta(minutes=int(travel_times_old_dict[route][stop_seq]))
					else:
						stop_time = start_time + datetime.timedelta(minutes=int(travel_times_dict[route][stop_seq]))
					if "alt_headsign" in stops_dict[route] and stop == stops_dict[route]["alt_headsign"]["from_stop"]:
						stop_headsign = stops_dict[route]["alt_headsign"]["headsign"]
					stop_time = datetime.datetime.strftime(stop_time, "%H:%M:%S")
					stop_times_txt.write(",".join([trip_id, stop_time, stop_time, str(stop), str(stop_seq), stop_headsign])+"\n")
					stop_seq += 1
				trip_seq += 1
	trips_txt.close()
	stop_times_txt.close()

def main():
	# check OSM data available
	if not(os.path.exists("data/shapes.json") and os.path.exists("data/stops.json")):
		print("ERROR: OSM data not found\nPlease run get_data_from_OSM script")
		return
	# create out dir if not exists
	if not(os.path.exists("out")):
		os.mkdir("out")
	# create text files
	print("creating agency.txt...")
	create_agency()
	print("creating calendar.txt...")
	create_calendar()
	print("creating calendar_dates.txt...")
	create_calendar_dates()
	print("creating routes.txt...")
	create_routes()
	print("creating shapes.txt...")
	create_shapes()
	print("creating stops.txt...")
	create_stops()
	print("creating stop_times.txt and trips.txt...")
	create_stop_times_trips()
	# change dir to out
	os.chdir("out")
	# create GTFS zip
	print("creating GTFS zip...")
	gtfs_zip = zipfile.ZipFile("gtfs_kecskemet.zip","w",zipfile.ZIP_DEFLATED)
	gtfs_zip.write("agency.txt")
	gtfs_zip.write("calendar.txt")
	gtfs_zip.write("calendar_dates.txt")
	gtfs_zip.write("routes.txt")
	gtfs_zip.write("shapes.txt")
	gtfs_zip.write("stops.txt")
	gtfs_zip.write("stop_times.txt")
	gtfs_zip.write("trips.txt")
	gtfs_zip.close()

if __name__ == "__main__":
	main()
