import pytest
from fastapi import status
from app.models import SwiftCode


class TestDeleteSwiftCodeIntegration:
    def test_delete_branch_success(self, client, session):
        test_branch = SwiftCode(
            swiftCode="CITIPLPP123",
            bankName="CITIBANK POLAND",
            countryISO2="PL",
            countryName="POLAND",
            address="UL. TESTOWA 1, WARSAW",
            isHeadquarter=False,
        )
        session.add(test_branch)
        session.commit()

        response = client.delete("/v1/swift-codes/CITIPLPP123")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["message"] == "SWIFT code CITIPLPP123 deleted successfully"

    def test_delete_hq_success(self, client, session):
        test_hq = SwiftCode(
            swiftCode="CITIPLPPXXX",
            bankName="CITIBANK POLAND HQ",
            countryISO2="PL",
            countryName="POLAND",
            address="UL. CENTRALNA 1, WARSAW",
            isHeadquarter=True,
        )
        session.add(test_hq)
        session.commit()

        response = client.delete("/v1/swift-codes/CITIPLPPXXX")

        assert response.status_code == status.HTTP_200_OK
        assert "CITIPLPPXXX" in response.json()["message"]

class TestDeleteResponseStructuresIntegration:
    def test_success_response_structure(self, client, session):
        test_branch = SwiftCode(
            swiftCode="MILLPLPW123",
            bankName="BANK MILLENNIUM",
            countryISO2="PL",
            countryName="POLAND",
            isHeadquarter=False,
        )
        session.add(test_branch)
        session.commit()

        response = client.delete("/v1/swift-codes/MILLPLPW123")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "SWIFT code MILLPLPW123 deleted successfully"}
