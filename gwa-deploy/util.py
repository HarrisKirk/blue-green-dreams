"""
Misc utility functions
"""

def tags_as_dict(tags: list[str]) -> dict[str, str]:
"""
Convert a list of strings assumed to be in key_value format to a dict.
"""
    tag_dict: dict[str, str] = {}
    for tag in tags:
        parts = tag.split("_")
        if len(parts) == 2:  # Ignore any tag not in xxx_yyy format
            key = parts[0]
            value = parts[1]
            if key in tag_dict:  # Duplicate key should be considered fatal
                raise ValueError(f"duplicate key '{key}' found in the {tag}")
            tag_dict[key] = value
    return tag_dict
