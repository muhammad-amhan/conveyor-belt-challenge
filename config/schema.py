BELT_SCHEMA = {
    "type": "object",
    "properties": {
        "debug": {"type": "boolean"},
        "belt": {
            "type": "object",
            "properties": {
                "belt_length": {"type": "integer"},
                "belt_delay": {"type": "integer"},
                "belt_iterations": {"type": "integer"},
            },
            "required": ["belt_length", "belt_delay", "belt_iterations"],
        },
        "workers_per_slot": {"type": "integer"},
        "assembly_time": {"type": "integer"},
        "finished_product": {"type": "string"},
    },
    "required": ["belt", "workers_per_slot", "assembly_time", "finished_product"],
}
