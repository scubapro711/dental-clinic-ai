#!/usr/bin/env python3
"""
Create LangSmith Dataset for DentaFlow Agent Workflows

This creates a comprehensive test dataset with examples for all agent workflows.
"""

import os
from langsmith import Client
from datetime import datetime

def create_agent_workflow_dataset():
    """Create a dataset with test cases for agent workflows."""
    
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not set")
        return
    
    client = Client(api_key=api_key)
    
    print("=" * 80)
    print("CREATING LANGSMITH DATASET FOR AGENT WORKFLOWS")
    print("=" * 80)
    print()
    
    # Create dataset
    dataset_name = "dentaflow-agent-workflows"
    dataset_description = "Test cases for DentaFlow agent workflows including patient registration, appointment booking, and RBAC"
    
    try:
        # Check if dataset already exists
        existing_datasets = list(client.list_datasets(dataset_name=dataset_name))
        if existing_datasets:
            print(f"⚠️  Dataset '{dataset_name}' already exists")
            dataset = existing_datasets[0]
            print(f"   Using existing dataset ID: {dataset.id}")
        else:
            dataset = client.create_dataset(
                dataset_name=dataset_name,
                description=dataset_description
            )
            print(f"✅ Created dataset: {dataset_name}")
            print(f"   ID: {dataset.id}")
    except Exception as e:
        print(f"❌ Error creating dataset: {e}")
        return
    
    print()
    print("=" * 80)
    print("ADDING TEST EXAMPLES")
    print("=" * 80)
    print()
    
    # Define test examples
    examples = [
        {
            "inputs": {
                "workflow": "new_patient_registration",
                "user_role": "receptionist",
                "patient_data": {
                    "name": "John Doe",
                    "phone": "+1234567890",
                    "email": "john.doe@example.com"
                }
            },
            "outputs": {
                "expected_result": "success",
                "expected_patient_id": "any_integer",
                "expected_message": "Patient registered successfully"
            },
            "metadata": {
                "test_type": "integration",
                "agent": "Alex",
                "priority": "high"
            }
        },
        {
            "inputs": {
                "workflow": "find_existing_patient",
                "user_role": "receptionist",
                "search_query": {
                    "name": "Avi Goldstein"
                }
            },
            "outputs": {
                "expected_result": "success",
                "expected_patient_count": 1
            },
            "metadata": {
                "test_type": "integration",
                "agent": "Alex",
                "priority": "high"
            }
        },
        {
            "inputs": {
                "workflow": "get_available_doctors",
                "user_role": "receptionist"
            },
            "outputs": {
                "expected_result": "success",
                "expected_doctor_count": ">=1"
            },
            "metadata": {
                "test_type": "integration",
                "agent": "Alex",
                "priority": "medium"
            }
        },
        {
            "inputs": {
                "workflow": "rbac_patient_access",
                "user_role": "patient",
                "patient_id": 1
            },
            "outputs": {
                "expected_result": "success",
                "expected_access": "own_data_only"
            },
            "metadata": {
                "test_type": "security",
                "agent": "System",
                "priority": "critical"
            }
        },
        {
            "inputs": {
                "workflow": "multi_patient_search",
                "user_role": "receptionist",
                "search_criteria": {
                    "name_pattern": "Smith"
                }
            },
            "outputs": {
                "expected_result": "success",
                "expected_patient_count": ">=0"
            },
            "metadata": {
                "test_type": "integration",
                "agent": "Alex",
                "priority": "medium"
            }
        }
    ]
    
    # Add examples to dataset
    try:
        for i, example in enumerate(examples, 1):
            client.create_example(
                dataset_id=dataset.id,
                inputs=example["inputs"],
                outputs=example["outputs"],
                metadata=example["metadata"]
            )
            print(f"✅ Added example {i}: {example['inputs']['workflow']}")
    except Exception as e:
        print(f"❌ Error adding examples: {e}")
        return
    
    print()
    print("=" * 80)
    print(f"✅ DATASET CREATED SUCCESSFULLY")
    print("=" * 80)
    print(f"Dataset Name: {dataset_name}")
    print(f"Dataset ID: {dataset.id}")
    print(f"Total Examples: {len(examples)}")
    print()
    print("Next steps:")
    print("1. Run evaluations on this dataset")
    print("2. Compare different agent versions")
    print("3. Monitor performance over time")
    print("=" * 80)

if __name__ == "__main__":
    create_agent_workflow_dataset()
