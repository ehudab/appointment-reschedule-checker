from geopy.geocoders import Nominatim

def get_lat_lon(location_name):
    # Initialize the Nominatim geocoder with a unique user agent
    geolocator = Nominatim(user_agent="my_geocoding_script/1.0")
    
    try:
        # Fetch location details
        location = geolocator.geocode(location_name)
        
        if location:
            return {
                "location": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude
            }
        else:
            return {"error": "Location not found."}
            
    except Exception as e:
        return {"error": str(e)}

# Example usage:
if __name__ == "__main__":
    location_name = "1600 Amphitheatre Parkway, Mountain View, CA"
    result = get_lat_lon(location_name)
    print(result)