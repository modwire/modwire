def parse_inputs(items: tuple[str, ...]) -> dict[str, str]:
    data = {}
    for item in items:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise ValueError(f"Invalid data item {item!r}. Expected key=value.")
        data[key] = value
    return data
