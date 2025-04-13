from flask import Blueprint, jsonify, request, send_from_directory, current_app
from database.connection import Neo4jConnection
from datetime import datetime
from config import Config
from neo4j.time import Date, DateTime

admin_bp = Blueprint('admin', __name__)
neo4j = Neo4jConnection()

def serialize_neo4j_value(value):
    """Helper function to serialize Neo4j values to JSON-compatible format"""
    if isinstance(value, (Date, DateTime)):
        return value.isoformat()
    return value

def calculate_forgery_score(claim):
    """
    Calculate a forgery score based on fraud metrics with None type handling.
    """
    fraud_prediction = claim.get('fraudPrediction', 0) or 0
    fraud_probability = claim.get('fraudProbability', 0.0) or 0.0
    fraud_reason = claim.get('fraudReason', "") or ""

    # Base score
    score = fraud_probability * 100

    # Add penalty for fraudulent claims
    if fraud_prediction:
        score += 20

    # Reduce score if claim seems legitimate
    if "legitimate" in fraud_reason.lower():
        score *= 0.8

    return round(score, 2)


def get_fraud_color_code(claim):
    """
    Determines a color code with None type handling.
    """
    score = calculate_forgery_score(claim)
    fraud_prediction = claim.get('fraudPrediction', 0) or 0
    
    # Use thresholds for color coding
    if fraud_prediction == 1 or score >= 20:
        return "#FF0000"  # Red for fraud
    else:
        return "#00FF00"  # Green for legit


@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    """
    Dashboard endpoint with None type handling.
    """
    policies_query = """
    MATCH (u:User)-[:INSURANCE]->(a:Application)
    RETURN count(a) as total_policies,
           count(CASE WHEN a.status = 'PENDING' THEN 1 END) as pending_policies,
           count(CASE WHEN a.status = 'ACTIVE' THEN 1 END) as active_policies
    """

    claims_query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN count(cm) as total_claims,
           count(CASE WHEN cm.status = 'In Progress' THEN 1 END) as in_progress_claims,
           count(CASE WHEN cm.status = 'Approved' THEN 1 END) as approved_claims,
           count(CASE WHEN cm.status = 'Rejected' THEN 1 END) as rejected_claims
    """

    users_query = """
    MATCH (u:User)
    RETURN count(u) as total_users
    """

    fraud_query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN cm.fraudPrediction as fraudPrediction,
           cm.fraudProbability as fraudProbability,
           cm.fraudReason as fraudReason
    """

    policy_stats = neo4j.execute_query(policies_query)[0] if neo4j.execute_query(policies_query) else {}
    claim_stats = neo4j.execute_query(claims_query)[0] if neo4j.execute_query(claims_query) else {}
    user_stats = neo4j.execute_query(users_query)[0] if neo4j.execute_query(users_query) else {}

    fraud_data = neo4j.execute_query(fraud_query) or []
    
    total_claims_fraud = len(fraud_data)
    fraudulent_count = sum(1 for claim in fraud_data if get_fraud_color_code(claim) == "#FF0000")
    
    fraud_detection_rate = round((fraudulent_count / total_claims_fraud * 100) if total_claims_fraud > 0 else 0, 2)

    return jsonify({
        'total_policies': policy_stats.get('total_policies', 0),
        'policy_distribution': {
            'active': policy_stats.get('active_policies', 0),
            'pending': policy_stats.get('pending_policies', 0)
        },
        'claims_distribution': {
            'in_progress': claim_stats.get('in_progress_claims', 0),
            'approved': claim_stats.get('approved_claims', 0),
            'rejected': claim_stats.get('rejected_claims', 0)
        },
        'total_users': user_stats.get('total_users', 0),
        'fraud_detection_rate': fraud_detection_rate
    })


@admin_bp.route('/policies', methods=['GET'])
def get_all_policies():
    """
    Policies endpoint with None type handling and proper serialization
    """
    query = """
    MATCH (u:User)-[:INSURANCE]->(a:Application)
    OPTIONAL MATCH (u)-[:HAS_BANKING_DETAILS]->(b:BankingDetails)
    OPTIONAL MATCH (u)-[:HAS_DETAILS]->(o:OtherDetails)
    OPTIONAL MATCH (u)-[:HAS_DOC]->(d:Document)
    RETURN u.name as applicant_name,
           u.email as email,
           u.mobile as mobile,
           u.address as address,
           u.customerId as customer_id,
           a.application_id as policy_id,
           a.vehicle_type as vehicle_type,
           a.make as make,
           a.model as model,
           a.registration_number as registration_number,
           a.year as year,
           a.status as status,
           a.policy_annual_premium as premium,
           a.policy_csl as csl,
           a.umbrella_limit as umbrella_limit,
           a.total_insurance_amount as total_amount,
           a.idv as idv,
           a.ncb as ncb,
           a.addons as addons,
           a.city as city,
           a.state as state,
           a.created_at as created_at,
           a.updated_at as updated_at,
           b.panNumber as pan_number,
           o.occupation as occupation,
           o.education_level as education,
           o.dob as date_of_birth,
           d.predicted_label as predicted_label,
           d.confidence as confidence
    ORDER BY a.created_at DESC
    """

    policies = neo4j.execute_query(query) or []
    formatted_policies = []

    def parse_addons(addons_value):
        """Safely parse addons from Neo4j value"""
        if isinstance(addons_value, str):
            try:
                import json
                return json.loads(addons_value)
            except json.JSONDecodeError:
                return []
        elif isinstance(addons_value, (list, tuple)):
            return list(addons_value)
        return []

    for policy in policies:
        # Serialize all values to handle Neo4j specific types
        serialized_policy = {k: serialize_neo4j_value(v) for k, v in policy.items()}
        
        formatted_policy = {
            'id': serialized_policy.get('policy_id', 'N/A'),
            'vehicleDetails': {
                'type': serialized_policy.get('vehicle_type', 'N/A'),
                'registrationNumber': serialized_policy.get('registration_number', 'N/A'),
                'make': serialized_policy.get('make', 'N/A'),
                'model': serialized_policy.get('model', 'N/A'),
                'year': int(serialized_policy.get('year', 0))
            },
            'personalInfo': {
                'fullName': serialized_policy.get('applicant_name', 'N/A'),
                'mobile': serialized_policy.get('mobile', 'N/A'),
                'email': serialized_policy.get('email', 'N/A'),
                'address': serialized_policy.get('address', 'N/A'),
                'city': serialized_policy.get('city', 'N/A'),
                'state': serialized_policy.get('state', 'N/A'),
                'customerId': serialized_policy.get('customer_id', 'N/A'),
                'panNumber': serialized_policy.get('pan_number', 'N/A'),
                'occupation': serialized_policy.get('occupation', 'N/A'),
                'education': serialized_policy.get('education', 'N/A'),
                'dateOfBirth': serialized_policy.get('date_of_birth', 'N/A')
            },
            'policyDetails': {
                'idv': float(serialized_policy.get('idv', 0.0)),
                'ncb': float(serialized_policy.get('ncb', 0.0)),
                'csl': float(serialized_policy.get('csl', 0.0)),
                'umbrellaLimit': float(serialized_policy.get('umbrella_limit', 0.0)),
                'totalInsuranceAmount': float(serialized_policy.get('total_amount', 0.0)),
                'addOns': parse_addons(serialized_policy.get('addons')),
                'premium': float(serialized_policy.get('premium', 0.0))
            },
            'status': serialized_policy.get('status', 'N/A'),
            'timestamps': {
                'created': serialized_policy.get('created_at', 'N/A'),
                'updated': serialized_policy.get('updated_at', 'N/A')
            },
            'predicted_label': serialized_policy.get('predicted_label', 'N/A'),
            'confidence': float(serialized_policy.get('confidence') or 0.0)
        }
        formatted_policies.append(formatted_policy)

    return jsonify(formatted_policies)

@admin_bp.route('/claims', methods=['GET'])
def get_all_claims():
    """
    Fetches all claims with safe None type handling.
    """
    query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(cm:ClaimManagement)
    OPTIONAL MATCH (cm)-[:MANAGES]->(c:Claim)
    OPTIONAL MATCH (c)-[:FILED_BY]->(cust:Customer)
    OPTIONAL MATCH (c)-[:OCCURRED_ON]->(i:Incident)
    RETURN u.name as user_name,
           cm.id as claim_management_id,
           cm.claim_type as claim_type,
           cm.status as status,
           cm.last_updated as submission_date,
           cm.fraudProbability as fraudProbability,
           cm.fraudPrediction as fraudPrediction,
           cm.fraudReason as fraudReason,
           c.id as claim_id,
           c.severity as severity,
           c.vehicle_amount as vehicle_amount,
           c.total_amount as total_amount,
           c.property_amount as property_amount,
           c.injury_amount as injury_amount,
           c.type as claim_detail_type,
           cust.id as customer_id,
           i.date as incident_date,
           i.city as incident_city,
           i.location as incident_location
    """

    claims = neo4j.execute_query(query) or []
    formatted_claims = []

    for claim in claims:
        # Serialize all values to handle Neo4j specific types
        serialized_claim = {k: serialize_neo4j_value(v) for k, v in claim.items()}
        color_code = get_fraud_color_code(serialized_claim)

        claim_details = {
            'claimManagementId': serialized_claim.get('claim_management_id', 'N/A'),
            'claimType': serialized_claim.get('claim_type', 'N/A'),
            'status': serialized_claim.get('status', 'Unknown'),
            'lastUpdated': serialized_claim.get('submission_date', 'N/A'),
            'probability': float(0.0 if serialized_claim.get('fraudProbability') is None else serialized_claim.get('fraudProbability')) * 100,
            'fraudPrediction': serialized_claim.get('fraudPrediction', 0),
            'fraudReason': serialized_claim.get('fraudReason', 'Not specified'),
            'claimId': serialized_claim.get('claim_id', 'N/A'),
            'severity': serialized_claim.get('severity', 'Unknown'),
            'vehicleAmount': float(serialized_claim.get('vehicle_amount', 0.0)),
            'totalAmount': float(serialized_claim.get('total_amount', 0.0)),
            'propertyAmount': float(serialized_claim.get('property_amount', 0.0)),
            'injuryAmount': float(serialized_claim.get('injury_amount', 0.0)),
            'claimDetailType': serialized_claim.get('claim_detail_type', 'N/A'),
            'incident': {
                'date': serialized_claim.get('incident_date', 'N/A'),
                'city': serialized_claim.get('incident_city', 'Unknown'),
                'location': serialized_claim.get('incident_location', 'Unknown')
            },
            'customerId': serialized_claim.get('customer_id', 'N/A'),
            'colorCode': color_code
        }

        formatted_claims.append({
            'userName': serialized_claim.get('user_name', 'Unknown'),
            'claimDetails': claim_details
        })

    return jsonify(formatted_claims)

@admin_bp.route('/documents/<policy_id>', methods=['GET'])
def get_documents(policy_id):
    """
    Endpoint to fetch and return file documents for a given policy.
    """
    print(policy_id)
    documents = get_policy_documents(policy_id)
    return jsonify(documents)

def get_policy_documents(policy_id):
    """
    Fetches file documents associated with a given policy from the Neo4j database.
    Includes safe handling of None values.
    """
    query = """
    MATCH (a:Application {application_id: $policy_id})<-[:INSURANCE]-(u:User)-[:HAS_DOC]->(d:Document)
    RETURN d.confidence AS confidence,
           d.predicted_label AS predicted_label,
           d.file_path AS file_path,
           d.file_name AS file_name,
           d.upload_date AS upload_date
    """

    documents = neo4j.execute_query(query, parameters={"policy_id": policy_id}) or []
    print(documents)
    formatted_docs = []

    for doc in documents:
        # Convert upload_date to string if it's not already
        upload_date = doc.get("upload_date", "N/A")
        if upload_date != "N/A":
            upload_date = str(upload_date)

        formatted_docs.append({
            "confidence": float(doc.get("confidence", 0.0)),
            "label": doc.get("predicted_label", "Unknown"),
            "filePath": doc.get("file_path", "N/A"),
            "fileName": doc.get("file_name", "Unknown"),
            "uploadDate": upload_date
        })

    return formatted_docs

@admin_bp.route('/documents/uploads/<path:filename>')
def serve_uploads(filename):
    # Ensure your app’s configuration points to the correct uploads folder
    uploads_folder = Config.UPLOAD_FOLDER
    return send_from_directory(uploads_folder, filename)

@admin_bp.route('/policies/<policy_id>/status', methods=['PUT'])
def update_policy_status(policy_id):
    """Update policy status endpoint"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        query = """
        MATCH (a:Application {application_id: $policy_id})
        SET a.status = $status,
            a.updated_at = datetime()
        RETURN a
        """
        
        result = neo4j.execute_query(query, parameters={
            "policy_id": policy_id,
            "status": new_status
        })
        
        if not result:
            return jsonify({'error': 'Policy not found'}), 404
            
        return jsonify({'message': 'Policy status updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/claims/<claim_id>/status', methods=['PUT'])
def update_claim_status(claim_id):
    """Update claim status endpoint"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
            
        query = """
        MATCH (cm:ClaimManagement {id: $claim_id})
        SET cm.status = $status
        RETURN cm
        """
        
        result = neo4j.execute_query(query, parameters={
            "claim_id": claim_id,
            "status": new_status
        })
        
        if not result:
            return jsonify({'error': 'Claim not found'}), 404
            
        return jsonify({'message': 'Claim status updated successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500