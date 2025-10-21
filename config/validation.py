import re
from django.core.exceptions import ValidationError

def validate_map_url(value):
    """
    Validate that the URL is a valid map link
    (supports Google Maps, Apple Maps, etc.)
    """
    pattern = re.compile(
        r"^(https?://)?(www\.)?"
        r"(google\.com/maps|goo\.gl/maps|maps\.apple\.com\.org)"
    )
    if not pattern.search(value):
        raise ValidationError("Invalid map URL. Please provide a valid map link.")
