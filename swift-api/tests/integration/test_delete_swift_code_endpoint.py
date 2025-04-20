# from fastapi.testclient import TestClient


# class TestDeleteResponseStructures:
#     """Response structure validation for DELETE endpoint"""

#     def test_success_response_structure(self, client: TestClient):
#         response = client.delete("/v1/swift-codes/TODELETE")
#         assert set(response.json().keys()) == {"message"}

#     def test_error_response_structure(self, client: TestClient):
#         response = client.delete("/v1/swift-codes/INVALID")
#         assert set(response.json().keys()) == {"detail"}