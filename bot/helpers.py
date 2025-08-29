def parse_callback(query_data: str):
    if ":" in query_data:
        return query_data.split(":", 1)
    return query_data, None
