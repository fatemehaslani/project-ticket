import re
from datetime import datetime


def validate(data, rules):
    errors = {}

    for field, field_rules in rules.items():
        value = data.get(field)

        for rule in field_rules:
            if ":" in rule:
                rule_name, param = rule.split(":", 1)
            else:
                rule_name, param = rule, None

            # __rules__
            if rule_name == "required" and (value is None or str(value).strip() == ""):
                errors[field] = f"The {field.replace('_', ' ')} field is required."

            elif rule_name == "min" and value and len(str(value)) < int(param):
                errors[field] = f"The {field.replace('_', ' ')} must be at least {param} characters"

            elif rule_name == "max" and value and len(str(value)) > int(param):
                errors[field] = f"The {field.replace('_', ' ')} may not be greater then {param} characters"

            elif rule_name == "in" and value and value not in param.split(","):
                errors[field] = f"The {field.replace('_', ' ')} must be one of: {param}."


            elif rule_name == "between":
                min_val, max_val = map(str.strip, param.split(","))

                if isinstance(value, (int, float)):
                    if not (float(min_val) <= value <= float(max_val)):
                        errors[field] = f"The {field.replace('_', ' ')} must be between {min_val} and {max_val}."
                else:
                    str_value = str(value)
                    if not (int(min_val) <= len(str_value) <= int(max_val)):
                        errors[field] = f"The {field.replace('_', ' ')} must be between {min_val} and {max_val} characters."

            elif rule_name == "email":
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, str(value)):
                    errors[field] = f"The {field.replace('_', ' ')} must be a valid email address."


            elif rule_name == "future_date" and value:
                try:
                    dt = datetime.fromisoformat(value)
                    if dt <= datetime.now():
                        errors[field] = f"The {field.replace('_', ' ')} must be a future date."
                except Exception:
                    errors[field] = f"The {field.replace('_', ' ')} must be a valid date."



    return errors