'''
import sys
import os
import uvicorn

if __name__ == "__main__":
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.insert(0, project_root)
    
    # Now that the path is set, we can import the app
    from src.gateway.main import app
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
