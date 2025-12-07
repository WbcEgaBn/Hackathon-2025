from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from db.models import GeocodeCache

geolocator = Nominatim(user_agent="civic-digest-app")

safe_geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.2,
    max_retries=3,
    error_wait_seconds=2.0
)

def geocode(db, address: str):

    if not address or not address.strip():
        return None

    address_norm = address.strip().lower()

    cached = db.query(GeocodeCache).filter_by(address=address_norm).first()

    if cached:
        return {
            "lat": float(cached.lat),
            "lon": float(cached.lon),
            "normalized": cached.address  # best we have
        }

    try:
        result = safe_geocode(address)
    except Exception as e:
        print(f"⚠ Geocoder error for '{address}': {e}")
        return None

    if not result:
        print(f"⚠ Geocode failed for: {address}")
        return None

    lat = float(result.latitude)
    lon = float(result.longitude)
    normalized_out = getattr(result, "address", address) 

    entry = GeocodeCache(
        address=address_norm,
        lat=str(lat),
        lon=str(lon)
    )

    db.add(entry)
    db.commit()

    return {
        "lat": lat,
        "lon": lon,
        "normalized": normalized_out
    }
