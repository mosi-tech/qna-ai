# Services package

# Import shared services  
import sys
import os
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, shared_path)
from shared.services.base_service import BaseService

# Note: Analysis services have been moved to shared.analyze
# Import them from there: from shared.analyze import AnalysisService, etc.

__all__ = [
    'BaseService'
]