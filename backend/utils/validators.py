"""Input validation utilities."""


def validate_required_fields(data, fields):
    """Check that all required fields are present and non-empty in data.

    Args:
        data: The request JSON dict.
        fields: List of required field names.

    Returns:
        A list of missing/empty field names, or empty list if all present.
    """
    if data is None:
        return fields
    missing = []
    for field in fields:
        value = data.get(field)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            missing.append(field)
    return missing


def validate_positive_integer(value, field_name):
    """Validate that a value is a non-negative integer.

    Args:
        value: The value to check.
        field_name: The field name for error messages.

    Returns:
        (int_value, None) on success, or (None, error_message) on failure.
    """
    try:
        int_val = int(value)
        if int_val < 0:
            return None, f"{field_name} must be a non-negative integer"
        return int_val, None
    except (TypeError, ValueError):
        return None, f"{field_name} must be a valid integer"


def validate_status(value, allowed_values, field_name="status"):
    """Validate that a status value is in the allowed set.

    Args:
        value: The status string.
        allowed_values: Iterable of valid status strings.
        field_name: The field name for error messages.

    Returns:
        None on success, or error_message string on failure.
    """
    if value not in allowed_values:
        return f"{field_name} must be one of: {', '.join(allowed_values)}"
    return None


def validate_email(email):
    """Basic email format validation.

    Args:
        email: The email string.

    Returns:
        True if valid format, False otherwise.
    """
    if not email or not isinstance(email, str):
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if "." not in domain:
        return False
    return True
