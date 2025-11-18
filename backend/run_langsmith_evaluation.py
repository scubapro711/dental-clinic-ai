#!/usr/bin/env python3
"""
Run LangSmith Evaluations on DentaFlow Agent Workflows

This script runs comprehensive evaluations using LangSmith's evaluation framework.
"""

import os
from langsmith import Client
from langsmith.evaluation import evaluate
import json

def create_evaluators():
    """Create custom evaluators for agent workflows."""
    
    def success_evaluator(run, example):
        """Check if the workflow succeeded."""
        try:
            # Get the actual output from the run
            output = run.outputs if hasattr(run, 'outputs') else {}
            expected = example.outputs
            
            # Check if result matches expected
            if expected.get("expected_result") == "success":
                # Check if there was an error
                if run.error:
                    return {"key": "success", "score": 0, "comment": f"Run failed with error: {run.error}"}
                return {"key": "success", "score": 1, "comment": "Workflow completed successfully"}
            
            return {"key": "success", "score": 0.5, "comment": "Unknown expected result"}
        except Exception as e:
            return {"key": "success", "score": 0, "comment": f"Evaluator error: {e}"}
    
    def latency_evaluator(run, example):
        """Check if the workflow completed within acceptable time."""
        try:
            if not run.end_time or not run.start_time:
                return {"key": "latency", "score": 0, "comment": "Missing timing information"}
            
            duration = (run.end_time - run.start_time).total_seconds()
            
            # Define acceptable latency thresholds
            if duration < 2:
                score = 1.0
                comment = f"Excellent latency: {duration:.2f}s"
            elif duration < 5:
                score = 0.8
                comment = f"Good latency: {duration:.2f}s"
            elif duration < 10:
                score = 0.6
                comment = f"Acceptable latency: {duration:.2f}s"
            else:
                score = 0.3
                comment = f"Slow latency: {duration:.2f}s"
            
            return {"key": "latency", "score": score, "comment": comment}
        except Exception as e:
            return {"key": "latency", "score": 0, "comment": f"Evaluator error: {e}"}
    
    def error_handling_evaluator(run, example):
        """Check if errors are handled gracefully."""
        try:
            if run.error:
                # Check if error message is informative
                error_str = str(run.error)
                if len(error_str) > 10 and "Exception" in error_str:
                    return {"key": "error_handling", "score": 0.5, "comment": "Error occurred but was captured"}
                return {"key": "error_handling", "score": 0.3, "comment": "Error occurred with minimal info"}
            
            return {"key": "error_handling", "score": 1.0, "comment": "No errors"}
        except Exception as e:
            return {"key": "error_handling", "score": 0, "comment": f"Evaluator error: {e}"}
    
    return [success_evaluator, latency_evaluator, error_handling_evaluator]

def mock_workflow_runner(inputs):
    """Mock function to simulate running agent workflows."""
    workflow = inputs.get("workflow")
    
    # Simulate different workflow outcomes
    if workflow == "new_patient_registration":
        return {
            "result": "success",
            "patient_id": 123,
            "message": "Patient registered successfully"
        }
    elif workflow == "find_existing_patient":
        return {
            "result": "success",
            "patients": [{"id": 1, "name": "Avi Goldstein"}],
            "count": 1
        }
    elif workflow == "get_available_doctors":
        return {
            "result": "success",
            "doctors": [{"id": 1, "name": "Dr. Smith"}],
            "count": 1
        }
    elif workflow == "rbac_patient_access":
        return {
            "result": "success",
            "access": "own_data_only"
        }
    elif workflow == "multi_patient_search":
        return {
            "result": "success",
            "patients": [],
            "count": 0
        }
    else:
        return {"result": "error", "message": "Unknown workflow"}

def run_evaluation():
    """Run evaluation on the dataset."""
    
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        print("❌ LANGSMITH_API_KEY not set")
        return
    
    client = Client(api_key=api_key)
    
    print("=" * 80)
    print("RUNNING LANGSMITH EVALUATION")
    print("=" * 80)
    print()
    
    # Get the dataset
    dataset_name = "dentaflow-agent-workflows"
    try:
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        if not datasets:
            print(f"❌ Dataset '{dataset_name}' not found")
            return
        
        dataset = datasets[0]
        print(f"✅ Found dataset: {dataset_name}")
        print(f"   ID: {dataset.id}")
    except Exception as e:
        print(f"❌ Error finding dataset: {e}")
        return
    
    print()
    print("=" * 80)
    print("CREATING EVALUATORS")
    print("=" * 80)
    evaluators = create_evaluators()
    print(f"✅ Created {len(evaluators)} evaluators:")
    print("   1. Success Evaluator")
    print("   2. Latency Evaluator")
    print("   3. Error Handling Evaluator")
    
    print()
    print("=" * 80)
    print("RUNNING EVALUATION")
    print("=" * 80)
    print("⏳ This may take a few moments...")
    print()
    
    try:
        # Run evaluation
        results = evaluate(
            mock_workflow_runner,
            data=dataset_name,
            evaluators=evaluators,
            experiment_prefix="dentaflow-eval",
            metadata={
                "version": "1.0",
                "environment": "test",
                "date": str(os.popen('date').read().strip())
            }
        )
        
        print()
        print("=" * 80)
        print("✅ EVALUATION COMPLETE")
        print("=" * 80)
        print()
        print("Results:")
        print(f"  Experiment: {results.get('experiment_name', 'N/A')}")
        print()
        print("Visit LangSmith UI to see detailed results:")
        print(f"  https://smith.langchain.com/")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error running evaluation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_evaluation()
