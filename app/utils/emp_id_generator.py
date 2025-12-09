def generate_employee_id(last_id: int) -> str:
    # Example: last_id = 1 → "AW001"
    return f"AW{str(last_id + 1).zfill(3)}"
