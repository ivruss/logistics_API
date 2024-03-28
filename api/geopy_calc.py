from geopy.distance import geodesic

def distance_calc(point1, point2):
    
    distance = geodesic(point1, point2).miles

    return distance