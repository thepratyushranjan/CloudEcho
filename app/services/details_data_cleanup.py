def transform_data(data: dict) -> dict:
    """
    Transforms a raw cloud resource JSON into the simplified schema.
    """
    output = {
        "cloud_resource_id": data.get("cloud_resource_id"),
        "name": data.get("name"),
        "active": data.get("active"),
        "service_name": data.get("service_name"),
        "resource_type": data.get("resource_type"),
        "region": data.get("region"),
        "meta": {
            "flavor": data.get("meta", {}).get("flavor"),
            "vpc_id": data.get("meta", {}).get("vpc_id"),
            "vpc_name": data.get("meta", {}).get("vpc_name"),
            "security_groups": data.get("meta", {}).get("security_groups", [])
        },
        "total_cost": data.get("total_cost"),
        "last_expense": {
            "cost": data.get("last_expense", {}).get("cost"),
            "date": data.get("last_expense", {}).get("date")
        },
        "recommendations": {},
        "tags": data.get("tags", {}),
        "cloud_account_id": data.get("cloud_account_id"),
        "pool_id": data.get("pool_id"),
        "details": {
            "pool_name": data.get("details", {}).get("pool_name"),
            "pool_purpose": data.get("details", {}).get("pool_purpose"),
            "forecast": data.get("details", {}).get("forecast"),
            "total_traffic_expenses": data.get("details", {}).get("total_traffic_expenses"),
            "total_traffic_usage": data.get("details", {}).get("total_traffic_usage")
        },
        "employee_id": data.get("employee_id"),
        "owner_name": data.get("details", {}).get("owner_name"),
        "first_seen": data.get("first_seen"),
        "last_seen": data.get("last_seen"),
        "cloud_created_at": data.get("cloud_created_at"),
        "meta_os": data.get("meta", {}).get("os"),
        "meta_image_id": data.get("meta", {}).get("image_id"),
        "meta_spotted": data.get("meta", {}).get("spotted"),
        "has_metrics": data.get("has_metrics"),
        "applied_rules": data.get("applied_rules")
    }

    for module in data.get("recommendations", {}).get("modules", []):
        name = module.get("name")
        if name == "insecure_security_groups":
            output["recommendations"]["insecure_security_groups"] = {
                "security_group_id": module.get("security_group_id"),
                "security_group_name": module.get("security_group_name"),
                "insecure_ports": module.get("insecure_ports", [])
            }
        elif name == "instances_for_shutdown":
            output["recommendations"]["instances_for_shutdown"] = {
                "inactivity_periods": module.get("inactivity_periods"),
                "saving": module.get("saving")
            }

    return output
