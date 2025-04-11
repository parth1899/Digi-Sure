import os
from datetime import datetime
import json
from flask import Blueprint, jsonify
from utils.auth import token_required, get_user_from_token
from database.connection import Neo4jConnection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/policies', methods=['GET'])
@token_required
def get_user_policies(current_user_email):
    def get_policies(tx, email):
        query = """
        MATCH (a:Application)
        WHERE a.email = $email
        RETURN a
        ORDER BY a.created_at DESC
        """
        result = tx.run(query, email=email)
        policies = []

        for record in result:
            app = record["a"]
            policy = {
                "type": "Vehicle",
                "policyNumber": app.get("application_id", ""),
                "sumInsured": float(app.get("idv", 0)),
                "premium": calculate_premium(app),
                "status": app.get("status", ""),
                "renewalDate": calculate_renewal_date(app.get("created_at", "")),
                "vehicle": {
                    "make": app.get("make", ""),
                    "model": app.get("model", ""),
                    "year": app.get("year", ""),
                    "registration": app.get("registration_number", ""),
                    "type": app.get("vehicle_type", "")
                },
                "applicant": {
                    "name": app.get("applicant_name", ""),
                    "email": app.get("email", ""),
                    "mobile": app.get("mobile", ""),
                    "address": app.get("address", ""),
                    "city": app.get("city", ""),
                    "state": app.get("state", "")
                },
                "addons": parse_addons(app.get("addons", "[]")),
                "ncb": app.get("ncb", 0)
            }
            policies.append(policy)
        
        return policies

    def calculate_premium(app):
        base_premium = float(app.get("idv", 0)) * 0.04
        ncb_discount = float(app.get("ncb", 0)) / 100
        premium_after_ncb = base_premium * (1 - ncb_discount)
        addons = parse_addons(app.get("addons", "[]"))
        addon_premium = calculate_addon_premium(base_premium, addons)
        return round(premium_after_ncb + addon_premium, 2)

    def calculate_addon_premium(base_premium, addons):
        addon_rates = {
            "Zero Depreciation": 0.15,
            "Roadside Assistance": 0.05,
            "Engine Protection": 0.10,
            "Personal Accident Cover": 0.08
        }
        total_addon_premium = sum(base_premium * addon_rates.get(addon, 0) for addon in addons)
        return total_addon_premium

    def parse_addons(addons_str):
        try:
            return json.loads(addons_str) if addons_str else []
        except (json.JSONDecodeError, TypeError):
            return []

    def calculate_renewal_date(created_at):
        try:
            created_date = datetime.fromisoformat(created_at)
            renewal_date = created_date.replace(year=created_date.year + 1)
            return renewal_date.strftime("%d %b %Y")
        except (ValueError, TypeError):
            return "Invalid Date"

    try:
        db = Neo4jConnection()
        with db.get_session() as session:
            policies = session.execute_read(get_policies, current_user_email)
            return jsonify({
                "status": "success",
                "data": policies
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@dashboard_bp.route('/user', methods=['GET'])
@token_required
def get_current_user_details(current_user_email):
    def get_user(tx, email):
        query = """
            MATCH (u:User {email: $email})
            RETURN u { .name, .customerId, .email, .mobile, .address, .education_level, .occupation, .hobbies, .relationship } AS user
        """
        result = tx.run(query, email=email)
        record = result.single()
        if record:
            return record["user"]
        return None

    try:
        db = Neo4jConnection()
        with db.get_session() as session:
            user_data = session.execute_read(get_user, current_user_email)
            if user_data:
                return jsonify({"success": True, "user": user_data}), 200
            else:
                return jsonify({"success": False, "message": "User not found"}), 404

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
@dashboard_bp.route('/user/is-complete', methods=['GET'])
@token_required
def check_user_profile_completeness(current_user_email):
    def get_user_profile(tx, email):
        query = """
            MATCH (u:User {email: $email})
            OPTIONAL MATCH (u)-[:HAS_DETAILS]->(od:OtherDetails)
            OPTIONAL MATCH (u)-[:HAS_BANKING_DETAILS]->(bd:BankingDetails)
            OPTIONAL MATCH (u)-[:INSURANCE]->(a:Application)
            RETURN {
                dob: od.dob,
                education_level: od.education_level,
                hobbies: od.hobbies,
                occupation: od.occupation,
                relationship: od.relationship,
                sex: od.sex,
                aadharNumber: bd.aadharNumber,
                accountNumber: bd.accountNumber,
                ifscCode: bd.ifscCode,
                panNumber: bd.panNumber,
                address: u.address,
                applications: a.application_id
            } AS profile
        """
        result = tx.run(query, email=email)
        record = result.single()
        if record:
            return record["profile"]
        return None

    try:
        db = Neo4jConnection()
        with db.get_session() as session:
            profile = session.execute_read(get_user_profile, current_user_email)

            if not profile:
                return jsonify({"success": False, "message": "User not found"}), 404

            required_fields = [
                "dob", "education_level", "hobbies", "occupation",
                "relationship", "sex", "aadharNumber", "accountNumber",
                "ifscCode", "panNumber", "address"
            ]

            missing_fields = [field for field in required_fields 
                            if profile.get(field) in [None, "", []]]

            is_complete = len(missing_fields) == 0
            has_applications = bool(profile.get("applications") and any(profile["applications"]))

            return jsonify({
                "success": True,
                "isComplete": is_complete,
                "missingFields": missing_fields,
                "hasApplications": has_applications
            }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500