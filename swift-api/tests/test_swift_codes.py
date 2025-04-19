# import pytest
# from fastapi.testclient import TestClient
# from sqlmodel import Session, select

# from app.models import SwiftCode

# # Real-world SWIFT codes for testing
# REAL_HQ_CODES = [
#     "CITIUS33XXX",  # Citibank N.A., New York (HQ)
#     "DEUTDEFFXXX",  # Deutsche Bank AG, Frankfurt (HQ)
#     "BNPAFRPPXXX",  # BNP Paribas, Paris (HQ)
# ]

# REAL_BRANCH_CODES = [
#     "CITIUS33MIA",  # Citibank N.A., Miami Branch
#     "DEUTDEFF500",  # Deutsche Bank AG, Berlin Branch
#     "BNPAFRPPPAR",  # BNP Paribas, Paris Branch
# ]

# INVALID_CODES = [
#     "CITIUS33",      # Too short (8 chars, but not a valid HQ code)
#     "DEUTDEFFXX",    # Invalid length (10 chars)
#     "BNP@FRPPXXX",   # Invalid character
#     "12345678XXX",   # Numeric in first 6 chars
#     "DEUTDEFFXXX ",  # Trailing space
#     " DEUTDEFFXXX",  # Leading space
#     "",              # Empty string
# ]

# @pytest.fixture
# def setup_test_data(session: Session):
#     """Fixture to set up test data with real-world SWIFT codes"""
#     # Headquarters
#     hq_data = [
#         SwiftCode(
#             swiftCode="CITIUS33XXX",
#             bankName="Citibank N.A.",
#             address="388 Greenwich Street, New York, NY 10013, USA",
#             countryISO2="US",
#             countryName="UNITED STATES",
#             isHeadquarter=True
#         ),
#         SwiftCode(
#             swiftCode="DEUTDEFFXXX",
#             bankName="Deutsche Bank AG",
#             address="Taunusanlage 12, 60325 Frankfurt am Main, Germany",
#             countryISO2="DE",
#             countryName="GERMANY",
#             isHeadquarter=True
#         ),
#     ]
    
#     # Branches
#     branch_data = [
#         SwiftCode(
#             swiftCode="CITIUS33MIA",
#             bankName="Citibank N.A. Miami Branch",
#             address="201 South Biscayne Boulevard, Miami, FL 33131, USA",
#             countryISO2="US",
#             countryName="UNITED STATES",
#             isHeadquarter=False
#         ),
#         SwiftCode(
#             swiftCode="DEUTDEFF500",
#             bankName="Deutsche Bank AG Berlin Branch",
#             address="Unter den Linden 13-15, 10117 Berlin, Germany",
#             countryISO2="DE",
#             countryName="GERMANY",
#             isHeadquarter=False
#         ),
#     ]
    
#     for item in hq_data + branch_data:
#         session.add(item)
#     session.commit()

# class TestGetSwiftCodeEndpoint:
#     """Comprehensive tests for GET /v1/swift-codes/{swift-code} endpoint"""
    
#     @pytest.mark.parametrize("swift_code", REAL_HQ_CODES)
#     def test_get_real_hq_swift_code(self, client: TestClient, setup_test_data, swift_code):
#         response = client.get(f"/v1/swift-codes/{swift_code}")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["swiftCode"] == swift_code
#         assert data["isHeadquarter"] is True
#         assert "branches" in data
        
#         # Verify branches belong to the same bank (first 4 characters match)
#         if data.get("branches"):
#             for branch in data["branches"]:
#                 assert branch["swiftCode"][:4] == swift_code[:4]

#     @pytest.mark.parametrize("swift_code", REAL_BRANCH_CODES)
#     def test_get_real_branch_swift_code(self, client: TestClient, setup_test_data, swift_code):
#         response = client.get(f"/v1/swift-codes/{swift_code}")
#         assert response.status_code == 200
#         data = response.json()
#         assert data["swiftCode"] == swift_code
#         assert data["isHeadquarter"] is False
#         assert "branches" not in data

#     def test_get_hq_with_multiple_branches(self, client: TestClient, session: Session):
#         """Test HQ with multiple branches from different countries"""
#         # Add HQ
#         hq = SwiftCode(
#             swiftCode="HSBCGB2LXXX",
#             bankName="HSBC Bank plc",
#             address="8 Canada Square, London E14 5HQ, UK",
#             countryISO2="GB",
#             countryName="UNITED KINGDOM",
#             isHeadquarter=True
#         )
#         session.add(hq)
        
#         # Add branches in different countries
#         branches = [
#             SwiftCode(
#                 swiftCode="HSBCHKHHXXX",
#                 bankName="The Hongkong and Shanghai Banking Corporation Limited",
#                 address="1 Queen's Road Central, Hong Kong",
#                 countryISO2="HK",
#                 countryName="HONG KONG",
#                 isHeadquarter=False
#             ),
#             SwiftCode(
#                 swiftCode="HSBCUS33MIA",
#                 bankName="HSBC Bank USA N.A. Miami Branch",
#                 address="1441 Brickell Avenue, Miami, FL 33131, USA",
#                 countryISO2="US",
#                 countryName="UNITED STATES",
#                 isHeadquarter=False
#             ),
#         ]
#         for branch in branches:
#             session.add(branch)
#         session.commit()
        
#         response = client.get("/v1/swift-codes/HSBCGB2LXXX")
#         assert response.status_code == 200
#         data = response.json()
#         assert len(data["branches"]) == 2
#         assert {b["countryISO2"] for b in data["branches"]} == {"HK", "US"}

#     @pytest.mark.parametrize("swift_code", INVALID_CODES)
#     def test_invalid_swift_codes(self, client: TestClient, swift_code):
#         response = client.get(f"/v1/swift-codes/{swift_code}")
#         assert response.status_code in (400, 404)
#         if response.status_code == 400:
#             assert "validation" in response.json()["detail"].lower()

#     def test_case_insensitivity(self, client: TestClient, setup_test_data):
#         """Test that endpoint handles case-insensitive input"""
#         mixed_case_code = "DeUtDeFfXxX"
#         response = client.get(f"/v1/swift-codes/{mixed_case_code}")
#         assert response.status_code == 200
#         assert response.json()["swiftCode"] == "DEUTDEFFXXX"

#     def test_whitespace_handling(self, client: TestClient, setup_test_data):
#         """Test that endpoint trims whitespace"""
#         response = client.get("/v1/swift-codes/  DEUTDEFFXXX  ")
#         assert response.status_code == 200
#         assert response.json()["swiftCode"] == "DEUTDEFFXXX"

#     def test_nonexistent_valid_code(self, client: TestClient):
#         """Test valid format but non-existent code"""
#         response = client.get("/v1/swift-codes/ABCDUS33XXX")
#         assert response.status_code == 404
#         assert "not found" in response.json()["detail"].lower()

#     def test_response_structure_hq(self, client: TestClient, setup_test_data):
#         """Verify complete response structure for HQ"""
#         response = client.get("/v1/swift-codes/CITIUS33XXX")
#         data = response.json()
        
#         assert all(field in data for field in [
#             "address", "bankName", "countryISO2", 
#             "countryName", "isHeadquarter", "swiftCode", "branches"
#         ])
#         assert isinstance(data["branches"], list)
        
#         if data["branches"]:
#             branch = data["branches"][0]
#             assert all(field in branch for field in [
#                 "address", "bankName", "countryISO2",
#                 "isHeadquarter", "swiftCode"
#             ])

#     def test_response_structure_branch(self, client: TestClient, setup_test_data):
#         """Verify complete response structure for branch"""
#         response = client.get("/v1/swift-codes/DEUTDEFF500")
#         data = response.json()
        
#         assert all(field in data for field in [
#             "address", "bankName", "countryISO2", 
#             "countryName", "isHeadquarter", "swiftCode"
#         ])
#         assert "branches" not in data