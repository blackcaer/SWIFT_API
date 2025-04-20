
# from fastapi.testclient import TestClient


# class TestPostResponseStructures:
#     """Response structure validation for POST endpoint"""

#     def test_success_response_structure(self, client: TestClient):
#         response = client.post(
#             "/v1/swift-codes",
#             json={
#                 "swiftCode": "NEWCODEXX",
#                 "bankName": "Bank",
#                 "address": "Address",
#                 "countryISO2": "US",
#                 "countryName": "UNITED STATES",
#                 "isHeadquarter": True
#             }
#         )
#         assert set(response.json().keys()) == {"message"}

#     def test_error_response_structure(self, client: TestClient):
#         response = client.post(
#             "/v1/swift-codes",
#             json={
#                 "swiftCode": "TESTHQXXX",  # Duplicate
#                 "bankName": "Bank",
#                 "address": "Address",
#                 "countryISO2": "US",
#                 "countryName": "UNITED STATES",
#                 "isHeadquarter": True
#             }
#         )
#         assert set(response.json().keys()) == {"detail"}