from database.connection import Neo4jConnection
from datetime import datetime
import json

class Profile:
    def __init__(self, email, name, phone, customer_id, address, banking_details):
        self.email = email
        self.name = name
        self.phone = phone
        self.customer_id = customer_id
        self.address = address
        self.banking_details = banking_details

    @staticmethod
    def update_profile(email, data):
        db = Neo4jConnection()
        with db.get_session() as session:
            # First, match or create the profile node and set all properties
            result = session.run("""
                MATCH (u:User {email: $email})
                MERGE (p:Profile {email: $email})
                SET p.name = $name,
                    p.phone = $phone,
                    p.customer_id = $customer_id,
                    p.address = $address,
                    p.aadhar_number = $aadhar_number,
                    p.pan_number = $pan_number,
                    p.account_number = $account_number,
                    p.ifsc_code = $ifsc_code,
                    p.updated_at = $updated_at
                MERGE (u)-[r:HAS_PROFILE_DETAILS]->(p)
                RETURN p
                """,
                email=email,
                name=data["name"],
                phone=data["phone"],
                customer_id=data["customerId"],
                address=data["address"],
                aadhar_number=data["bankingDetails"]["aadharNumber"],
                pan_number=data["bankingDetails"]["panNumber"],
                account_number=data["bankingDetails"]["accountNumber"],
                ifsc_code=data["bankingDetails"]["ifscCode"],
                updated_at=datetime.now().isoformat()
            )
            
            profile_data = result.single()
            if profile_data:
                profile = profile_data['p']
                # Reconstruct the banking details
                banking_details = {
                    "aadharNumber": profile["aadhar_number"],
                    "panNumber": profile["pan_number"],
                    "accountNumber": profile["account_number"],
                    "ifscCode": profile["ifsc_code"]
                }
                return Profile(
                    email,
                    profile["name"],
                    profile["phone"],
                    profile["customer_id"],
                    profile["address"],
                    banking_details
                )
            return None

    @staticmethod
    def get_profile(email):
        db = Neo4jConnection()
        with db.get_session() as session:
            result = session.run("""
                MATCH (u:User {email: $email})-[:HAS_PROFILE_DETAILS]->(p:Profile)
                RETURN p
                """,
                email=email
            )
            profile_data = result.single()
            if profile_data:
                profile = profile_data['p']
                # Reconstruct the banking details
                banking_details = {
                    "aadharNumber": profile.get("aadhar_number", ""),
                    "panNumber": profile.get("pan_number", ""),
                    "accountNumber": profile.get("account_number", ""),
                    "ifscCode": profile.get("ifsc_code", "")
                }
                return Profile(
                    profile["email"],
                    profile.get("name", ""),
                    profile.get("phone", ""),
                    profile.get("customer_id", ""),
                    profile.get("address", ""),
                    banking_details
                )
            return None