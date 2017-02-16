
def geojson_to_lat_lng(geojson):
    """Extract coordinates of a single-element GeometryCollection and return it in 'latitude,longitude' format"""
    geometry = geojson['features'][0]['geometry']
    return "{},{}".format(geometry['coordinates'][0], geometry['coordinates'][1])