from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from db.models import GeocodeCache

geolocator = Nominatim(user_agent="civic-digest-app")

# Rate limit: ~1 request every 1.2s, 3 retries, wait between retries
safe_geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1.2,
    max_retries=3,
    error_wait_seconds=2.0
)

def geocode(db, address: str):
    """
    Cached geocoding lookup.

    Returns dict format:
    {
        "lat": float,
        "lon": float,
        "normalized": str  # Nominatim normalized address
    }

    Steps:
    1. Normalize the input string
    2. Check DB cache
    3. If missing → call Nominatim (slow)
    4. Store in cache
    """

    if not address or not address.strip():
        return None

    address_norm = address.strip().lower()

    # -------------------------------------------------------
    # 1. Check DB cache
    # -------------------------------------------------------
    cached = db.query(GeocodeCache).filter_by(address=address_norm).first()

    if cached:
        return {
            "lat": float(cached.lat),
            "lon": float(cached.lon),
            "normalized": cached.address  # best we have
        }

    # -------------------------------------------------------
    # 2. Geocode using Nominatim
    # -------------------------------------------------------
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
    normalized_out = getattr(result, "address", address)  # Nominatim normalized address

    # -------------------------------------------------------
    # 3. Save to DB cache
    # -------------------------------------------------------
    entry = GeocodeCache(
        address=address_norm,
        lat=str(lat),
        lon=str(lon)
    )

    db.add(entry)
    db.commit()

    # -------------------------------------------------------
    # 4. Return consistent response
    # -------------------------------------------------------
    return {
        "lat": lat,
        "lon": lon,
        "normalized": normalized_out
    }
