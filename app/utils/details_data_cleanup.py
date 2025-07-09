import requests 
from datetime import datetime, UTC
from typing import Dict, Any, List, Tuple
from utils.location_mapping import get_country_from_aws_region_code, get_country_from_azure_region_code, get_country_from_gcp_region_code
from services.cloud_comparison_service import CloudComparisonFilterService, CloudMultipleDataService
from models.pydentic_model import CloudMultipleDataResponse

# Source data Structure Format 
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
            "cost": data.get("details", {}).get("cost"),
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

# Monitoring data Structure Format
def structure_metrics(raw: Dict[str, Any]) -> Dict[str, Any]:
   
    # Build lookup tables
    cpu_map    = {d["date"]: d["value"] for d in raw["cpu"]}
    in_map     = {d["date"]: d["value"] for d in raw["network_in_io"]}
    out_map    = {d["date"]: d["value"] for d in raw["network_out_io"]}
    
    # Assemble unified list
    metrics = []
    for ts in sorted(cpu_map):
        metrics.append({
            "timestamp": datetime.fromtimestamp(ts, UTC).isoformat() + "Z",
            "cpu":           cpu_map[ts],
            "network_in_io": in_map[ts],
            "network_out_io": out_map[ts],
        })
    
    return {"metrics": metrics}


def structured_data (content: Dict[str, Any], monitoring: Dict[str, Any]):
    items = list(content.items())
    idx = next(
        i for i, (k, _) in enumerate(items)
        if k == "applied_rules"
    )
    items.insert(
        idx + 1,
        ("metrics", monitoring["metrics"])
    )

    return dict(items)


def extract_basic_info(data: dict) -> dict:
    meta = data.get("meta", {})
    os_raw = meta.get("os")
    # if os is None or the string "NA" (case-insensitive), default to "Linux"
    if os_raw is None or (isinstance(os_raw, str) and os_raw.strip().upper() == "NA"):
        os_value = "Linux"
    else:
        os_value = os_raw

    return {
        "cloud_resource_id": data.get("cloud_resource_id"),
        "name":              data.get("name"),
        "service_name":      data.get("service_name"),
        "resource_type":     data.get("resource_type"),
        "region":            data.get("region"),
        "flavor":            meta.get("flavor"),
        "os":                os_value,
    }


def update_service_name(basic_info):
    service_name = basic_info.get("service_name")

    if "Amazon" in service_name or "AWS" in service_name:
        service_name = "AWS"
    elif "microsoft.compute" in service_name or "microsoft" in service_name or "Azure" in service_name or "azure" in service_name:
        service_name = "Azure"
    else:
        service_name = "GCP"  # Set to GCP if neither AWS nor Azure

    return service_name


def get_cloud_comparison(basic_info):
    region = basic_info.get("region")
    flavor = basic_info.get("flavor")
    os = basic_info.get("os")
    service_name = update_service_name(basic_info)
    if service_name == "Azure" and region:
        region = region.replace(" ", "").lower()
    print(f"Service Name: {service_name}, Region: {region}, Flavor: {flavor}, OS: {os}")
    
    cloud_comparison_service = CloudMultipleDataService()

    filtered_results = cloud_comparison_service.get_filtered_cloud_comparisons_multiple(
            location=[],
            instance_families=[], 
            clouds=[service_name] if service_name else [], 
            regions=[region] if region else [],
            instance_type=[flavor] if flavor else [],
            os=[os] if os else []
        )
    
    results = CloudMultipleDataResponse(cloud_multiple_data=filtered_results)
    return results.dict()
    


def get_cloud_comparison_filter(comparison, basic_info):
    region = basic_info.get("region")
    os = basic_info.get("os")
    os = [os] if os else []
    service_name = update_service_name(basic_info)
    country = []
    if service_name == "AWS":
        country = [get_country_from_aws_region_code(region)] if region else []

    if service_name == "Azure":
        country = [get_country_from_azure_region_code(region)] if region else []

    if service_name == "GCP":
        country = [get_country_from_gcp_region_code(region)] if region else []

    if not comparison or not isinstance(comparison, dict):
        return None
        
    data_list = comparison.get("cloud_multiple_data", [])  
    vcpus = list({item.get("vcpus") for item in data_list if item.get("vcpus") is not None})
    memory_gb = list({item.get("memory_gb") for item in data_list if item.get("memory_gb") is not None})
    cost_per_hour = list({item.get("cost_per_hour") for item in data_list if item.get("cost_per_hour") is not None})
    instance_families = list({item.get("instance_family") 
                              for item in data_list 
                              if item.get("instance_family")})
    cloud_comparison_filter_service = CloudComparisonFilterService()
    filtered_results = cloud_comparison_filter_service.get_filtered_by_specs(
            vcpus=vcpus,
            memory_gb=memory_gb,
            cost_per_hour=cost_per_hour,
            instance_families=instance_families,
            country=country,
            os =os,
        )
        
    results = CloudMultipleDataResponse(cloud_multiple_data=filtered_results)
    return results.dict()
    

def structured_data_with_cloud_migration(
    content: Dict[str, Any],
    monitoring: Dict[str, Any],
    filtered: Dict[str, Any]
) -> Dict[str, Any]:
    items: List[Tuple[str, Any]] = list(content.items())

    idx = next(
        i for i, (k, _) in enumerate(items)
        if k == "applied_rules"
    )
    items.insert(idx + 1, ("metrics", monitoring["metrics"]))
    items.insert(idx + 2, ("comparison", filtered))
    return dict(items)