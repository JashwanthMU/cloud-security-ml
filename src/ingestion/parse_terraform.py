import hcl2
import json

def parse_terraform_file(file_path):
    """
    Reads a Terraform file and extracts information
    
    Args:
        file_path: Path to .tf file
        
    Returns:
        Dictionary with extracted information
    """
    
    # Read the file
    with open(file_path, 'r') as file:
        terraform_code = file.read()
    
    # Parse with HCL2 library
    try:
        parsed = hcl2.loads(terraform_code)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return None
    
    # Extract resources
    resources = []
    
    if 'resource' in parsed:
        for resource_list in parsed['resource']:
            for resource_type, resource_configs in resource_list.items():
                for resource_name, resource_config in resource_configs.items():
                    
                    resource_info = {
                        'type': resource_type,
                        'name': resource_name,
                        'properties': resource_config
                    }
                    
                    resources.append(resource_info)
    
    return {
        'file': file_path,
        'resources': resources
    }

# Test it
if __name__ == '__main__':
    # Parse example file
    result = parse_terraform_file('data/raw/safe/example_001.tf')
    
    # Print nicely
    print(json.dumps(result, indent=2))