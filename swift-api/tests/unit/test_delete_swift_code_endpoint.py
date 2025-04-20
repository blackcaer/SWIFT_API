# import pytest
# from unittest.mock import MagicMock, patch
# from app.routers.swift_codes import router
# from fastapi import HTTPException
# from fastapi.testclient import TestClient
# from app.main import app

# class TestDeleteResponseStructure:
#     """Tests for verifying delete endpoint response structure"""
    
#     @pytest.fixture
#     def client(self):
#         return TestClient(app)

#     @pytest.mark.asyncio
#     @patch("app.routers.swift_codes.db.get")
#     @patch("app.routers.swift_codes.db.delete")
#     @patch("app.routers.swift_codes.db.commit")
#     async def test_delete_response_structure(self, mock_commit, mock_delete, mock_get, client):
#         """Verify delete response contains exactly the required fields"""
#         # Mock existing code
#         mock_get.return_value = MagicMock(swiftCode="DELETECODE")

#         response = client.delete("/v1/swift-codes/DELETECODE")

#         # Verify response has exactly these fields
#         assert response.status_code == 200
#         assert set(response.json().keys()) == {"message"}