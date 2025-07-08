"""
Configuration for barcode module.
"""

# Reader configuration
READER_CONFIG = {
    'openfoodfacts': {
        'enabled': True,
        'priority': 10,
        'timeout': 10,
        'user_agent': 'MyFoodBudget/0.1 (https://github.com/user/myfoodbudget)'
    },
    'nutrifinder': {
        'enabled': True,
        'priority': 20,
        'timeout': 10,
        'base_url': 'https://api.mtbonde.dev/api/nutrition'
    }
}

# Danish product preferences
DANISH_PREFERENCES = {
    'prioritize_danish_products': True,
    'danish_country_codes': ['570', '571', '572', '573', '574', '575', '576', '577', '578', '579']
}

# Validation settings
VALIDATION_CONFIG = {
    'strict_barcode_validation': True,
    'allow_invalid_barcodes': False,
    'max_name_length': 32,
    'min_name_length': 1
}

# Caching settings
CACHE_CONFIG = {
    'enable_caching': True,
    'cache_ttl_seconds': 3600,  # 1 hour
    'max_cache_size': 1000
}