def convert_units_liters(value, from_unit, to_unit):
    conversion_factors = {
        'l': 1,
        'ml': 0.001,
        'μl': 1e-6,
        'ul': 1e-6,
        'nl': 1e-9
    }
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit not in conversion_factors or to_unit not in conversion_factors:
        raise ValueError("Unsupported unit")

    # Convert the value to milliliters
    value_in_ml = value * conversion_factors[from_unit]

    # Convert from milliliters to the target unit
    return value_in_ml / conversion_factors[to_unit]

def convert_units_grams(value, from_unit, to_unit):
    conversion_factors = {
        'kg': 1000,
        'g': 1,
        'mg': 0.001,
        'μg': 1e-6,
        'ug': 1e-6,
        'ng': 1e-9
    }

    if from_unit not in conversion_factors or to_unit not in conversion_factors:
        raise ValueError("Unsupported unit")

    # Convert the value to grams (or milliliters)
    value_in_grams = value * conversion_factors[from_unit]

    # Convert from grams (or milliliters) to the target unit
    return value_in_grams / conversion_factors[to_unit]