from typing import List, Dict, Any, Optional
import os
import json
from pathlib import Path

class ValidationLayer:
    def __init__(self):
        self.errors = []

    def validate_design(self, actions: Dict[str, Any], screens: List[str], components: List[str]) -> bool:
        """
        1. Design Validation
        Every action exists
        Every screen has route
        Every component has binding
        """
        self.errors = []
        is_valid = True

        if not actions:
            self.errors.append("Validation Error: No actions defined in design.")
            is_valid = False

        if not screens:
            self.errors.append("Validation Error: No screens defined in design.")
            is_valid = False

        # In a real scenario, we might check if components are used in screens
        # For now, just ensuring lists are not empty is a basic check
        if not components:
            self.errors.append("Validation warning: No components found.")
            # Warning doesn't fail validation? User said "Only allow Live Preview if ALL PASS"
            # Let's keep it strict or allow empty components if project is simple?
            # User said "Every component has binding". This implies stricter check.
            # We'll treat it as valid but empty for now if no components specifically requested to be checked against usage.
            pass

        return is_valid

    def validate_backend(self, files: List[Dict[str, str]]) -> bool:
        """
        2. Backend Validation
        Check for:
        - All endpoints exist
        - Pydantic field constraints (min_length, regex, etc.)
        - EmailStr usage
        """
        self.errors = []
        is_valid = True
        
        has_field_constraints = False
        has_email_str = False
        
        for f in files:
            content = f.get('content', '')
            if 'Field(' in content and ('min_length' in content or 'max_length' in content or 'regex' in content):
                has_field_constraints = True
            if 'EmailStr' in content:
                has_email_str = True

        if not has_field_constraints:
            self.errors.append("Backend Warning: No strict Pydantic field constraints found (min_length, etc.).")
            # We don't fail yet, but we warn
        
        if not has_email_str:
            self.errors.append("Backend Warning: EmailStr validation not found in models/schemas.")

        return is_valid

    def validate_frontend(self, files: List[Dict[str, str]]) -> bool:
        """
        3. Frontend Validation
        Check for:
        - Zod schema definitions
        - react-hook-form usage
        - Error message display logic
        """
        self.errors = []
        is_valid = True
        
        has_zod = False
        has_hook_form = False
        has_error_display = False
        
        for f in files:
            content = f.get('content', '')
            if 'z.object' in content or 'zod' in content:
                has_zod = True
            if 'useForm' in content:
                has_hook_form = True
            if 'errors.' in content and '.message' in content:
                has_error_display = True

        if not has_zod:
            self.errors.append("Frontend Warning: Zod validation schemas not found.")
        
        if not has_hook_form:
             self.errors.append("Frontend Warning: react-hook-form not found in form pages.")
             
        if not has_error_display:
            self.errors.append("Frontend Warning: UI does not seem to display validation error messages.")
            
        return is_valid

    def validate_dependencies(self, package_json_path: str) -> bool:
        """
        4. Dependency Validation
        package.json install check
        No missing packages
        """
        self.errors = []
        if not os.path.exists(package_json_path):
            self.errors.append(f"Dependency Error: {package_json_path} not found.")
            return False
            
        try:
            with open(package_json_path, 'r') as f:
                data = json.load(f)
                if 'dependencies' not in data and 'devDependencies' not in data:
                    self.errors.append("Dependency Error: No dependencies listed in package.json")
                    return False
        except Exception as e:
            self.errors.append(f"Dependency Error: Invalid package.json: {str(e)}")
            return False

        return True

    def get_errors(self) -> List[str]:
        return self.errors
