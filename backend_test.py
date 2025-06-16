import requests
import json
import sys
from datetime import datetime

class CaseManagementTester:
    def __init__(self, base_url="https://75515fa7-d2e8-447e-baf6-1de305c31f86.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_info = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_case_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_login(self, username, password):
        """Test login and get token"""
        print(f"\n🔐 Testing login with {username}...")
        success, response = self.run_test(
            "Login",
            "POST",
            "/api/auth/login",
            200,
            data={"username": username, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_info = response.get('user', {})
            print(f"✅ Login successful as {self.user_info.get('role', 'unknown role')}")
            return True
        print("❌ Login failed")
        return False

    def test_submit_case(self, case_type="birth_registration"):
        """Test case submission"""
        print(f"\n📝 Testing case submission for {case_type}...")
        
        # Create sample data based on case type
        submitter_data = {}
        if case_type == "birth_registration":
            submitter_data = {
                "child_name": "Test Child",
                "date_of_birth": "2025-01-15",
                "place_of_birth": "Test Hospital",
                "mother_name": "Test Mother",
                "father_name": "Test Father",
                "contact_email": "test@example.com"
            }
        elif case_type == "business_registration":
            submitter_data = {
                "business_name": "Test Business",
                "business_type": "LLC",
                "owner_name": "Test Owner",
                "business_address": "123 Test St",
                "contact_email": "business@example.com"
            }
        elif case_type == "land_registration":
            submitter_data = {
                "property_address": "456 Land St",
                "property_size": "1000 sqm",
                "owner_name": "Test Land Owner",
                "previous_owner": "Previous Owner",
                "contact_email": "land@example.com"
            }
        
        case_data = {
            "case_type": case_type,
            "submitter_data": submitter_data,
            "documents": [],
            "submitted_by": self.user_info.get('id', 'test_user')
        }
        
        success, response = self.run_test(
            f"Submit {case_type} case",
            "POST",
            "/api/cases/submit",
            200,
            data=case_data
        )
        
        if success and response.get('success') and 'case_id' in response:
            self.test_case_id = response['case_id']
            print(f"✅ Case submitted successfully with ID: {self.test_case_id}")
            print(f"   Case Number: {response.get('case_number', 'N/A')}")
            return True
        
        print("❌ Case submission failed")
        return False

    def test_get_cases(self):
        """Test getting list of cases"""
        print("\n📋 Testing get cases list...")
        success, response = self.run_test(
            "Get cases",
            "GET",
            "/api/cases",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} cases")
            return True
        
        print("❌ Failed to retrieve cases")
        return False

    def test_get_case_details(self, case_id=None):
        """Test getting case details"""
        if case_id is None:
            case_id = self.test_case_id
            
        if not case_id:
            print("❌ No case ID available for testing details")
            return False
            
        print(f"\n🔍 Testing get case details for ID: {case_id}...")
        success, response = self.run_test(
            "Get case details",
            "GET",
            f"/api/cases/{case_id}",
            200
        )
        
        if success and 'id' in response:
            print(f"✅ Retrieved case details for {response.get('case_number', 'unknown')}")
            return True
        
        print("❌ Failed to retrieve case details")
        return False

    def test_workflow_action(self, case_id=None, action="assign", assigned_to=None, comment="Test comment"):
        """Test workflow action"""
        if case_id is None:
            case_id = self.test_case_id
            
        if not case_id:
            print("❌ No case ID available for workflow testing")
            return False
            
        print(f"\n⚙️ Testing workflow action '{action}' for case ID: {case_id}...")
        
        data = {
            "case_id": case_id,
            "action": action,
            "comment": comment
        }
        
        if assigned_to:
            data["assigned_to"] = assigned_to
            
        success, response = self.run_test(
            f"Workflow action: {action}",
            "POST",
            f"/api/cases/{case_id}/workflow",
            200,
            data=data
        )
        
        if success and response.get('success'):
            print(f"✅ Workflow action '{action}' successful")
            return True
        
        print(f"❌ Workflow action '{action}' failed")
        return False

    def test_get_users(self):
        """Test getting users list"""
        print("\n👥 Testing get users list...")
        success, response = self.run_test(
            "Get users",
            "GET",
            "/api/users",
            200
        )
        
        if success and isinstance(response, list):
            print(f"✅ Retrieved {len(response)} users")
            # Return a user ID for assignment testing
            for user in response:
                if user.get('role') == 'registrar_assistant':
                    return user.get('id')
            return True
        
        print("❌ Failed to retrieve users")
        return False

    def test_get_dashboard_stats(self):
        """Test getting dashboard stats"""
        print("\n📊 Testing dashboard stats...")
        success, response = self.run_test(
            "Get dashboard stats",
            "GET",
            "/api/dashboard/stats",
            200
        )
        
        if success and isinstance(response, dict):
            print(f"✅ Retrieved dashboard stats")
            return True
        
        print("❌ Failed to retrieve dashboard stats")
        return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("\n🚀 Starting Case Management System API Tests\n")
        
        # Test authentication with different roles
        roles = [
            ("admin", "admin123", "supervisor"),
            ("registrar1", "reg123", "registrar"),
            ("assistant1", "ass123", "registrar_assistant"),
            ("lawyer1", "law123", "lawyer")
        ]
        
        for username, password, role in roles:
            print(f"\n==== Testing as {role} ({username}) ====")
            if not self.test_login(username, password):
                print(f"❌ Login failed for {role}, skipping related tests")
                continue
                
            # Test dashboard stats
            self.test_get_dashboard_stats()
            
            # Test case listing
            self.test_get_cases()
            
            # For registrar, test user listing and case submission
            if role == "registrar":
                assistant_id = self.test_get_users()
                
                # Test case submission
                if self.test_submit_case("birth_registration"):
                    # Test case details
                    self.test_get_case_details()
                    
                    # Test workflow - assign to assistant
                    if isinstance(assistant_id, str):
                        self.test_workflow_action(action="assign", assigned_to=assistant_id)
            
            # For assistant, test workflow actions
            elif role == "registrar_assistant":
                # Get cases to find one assigned to this assistant
                success, cases = self.run_test("Get assigned cases", "GET", "/api/cases", 200)
                if success and isinstance(cases, list) and cases:
                    for case in cases:
                        if case.get('assigned_to') == self.user_info.get('id'):
                            # Test review action
                            self.test_workflow_action(case_id=case.get('id'), action="review")
                            
                            # Test approve action
                            self.test_workflow_action(case_id=case.get('id'), action="approve")
                            break
        
        # Print test summary
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = CaseManagementTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)