import os
from datetime import datetime
import json
from flask import Blueprint, jsonify
from utils.auth import token_required, get_user_from_token
from database.connection import Neo4jConnection

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/policies', methods=['GET'])
@token_required
def get_user_policies(current_user):
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
            policies = session.execute_read(get_policies, current_user.email)
            return jsonify({
                "status": "success",
                "data": policies
            })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
