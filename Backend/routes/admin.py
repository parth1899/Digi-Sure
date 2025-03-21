from flask import Blueprint, jsonify, request
from database.connection import Neo4jConnection
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
neo4j = Neo4jConnection()

def calculate_forgery_score(claim):
    """
    Calculate a forgery score based on fraud metrics provided by the ClaimManagement node.
    Lower scores indicate lower risk.
    """
    fraud_prediction = claim.get('fraudPrediction', 0)
    fraud_probability = claim.get('fraudProbability', 0.0)
    print(fraud_probability)
    fraud_reason = claim.get('fraudReason', "")

    # Base score: scale fraud probability to percentage
    score = fraud_probability * 100

    # Add penalty if fraud prediction flag is raised
    if fraud_prediction:
        score += 20

    # Reduce score if the fraud reason indicates the claim appears legitimate
    if "legitimate" in fraud_reason.lower():
        score *= 0.8

    return round(score, 2)

def get_fraud_color_code(claim):
    """
    Determines a color code for the frontend based on the claim's fraud assessment.
    Returns red ("#FF0000") if the claim is fraudulent; otherwise, green ("#00FF00").
    """
    score = calculate_forgery_score(claim)
    # Define threshold; if fraudPrediction is active or the score is high, flag as fraud.
    if claim.get('fraudPrediction', 0) == 1 or score >= 20:
        return "#FF0000"  # Red for fraudulent claim
    else:
        return "#00FF00"  # Green for non-fraudulent claim

@admin_bp.route('/dashboard', methods=['GET'])
def get_dashboard_stats():
    # Query to get total policies count
    policies_query = """
    MATCH (u:User)-[:INSURANCE]->(a:Application)
    RETURN count(a) as total_policies,
           count(CASE WHEN a.status = 'PENDING' THEN 1 END) as pending_policies,
           count(CASE WHEN a.status = 'ACTIVE' THEN 1 END) as active_policies
    """
    
    # Query to get claims statistics
    claims_query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN count(cm) as total_claims,
           count(CASE WHEN cm.status = 'In Progress' THEN 1 END) as in_progress_claims,
           count(CASE WHEN cm.status = 'Approved' THEN 1 END) as approved_claims,
           count(CASE WHEN cm.status = 'Rejected' THEN 1 END) as rejected_claims
    """
    
    # Query to get total users
    users_query = """
    MATCH (u:User)
    RETURN count(u) as total_users
    """
    
    policy_stats = neo4j.execute_query(policies_query)[0]
    claim_stats = neo4j.execute_query(claims_query)[0]
    user_stats = neo4j.execute_query(users_query)[0]
    
    # New query to fetch fraud details for all ClaimManagement nodes
    fraud_query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN cm.fraudPrediction as fraudPrediction,
           cm.fraudProbability as fraudProbability,
           cm.fraudReason as fraudReason
    """
    fraud_data = neo4j.execute_query(fraud_query)
    
    total_claims_fraud = len(fraud_data)
    fraudulent_count = sum(1 for claim in fraud_data if get_fraud_color_code(claim) == "#FF0000")
    fraud_detection_rate = round((fraudulent_count / total_claims_fraud * 100) if total_claims_fraud > 0 else 0, 2)
    
    return jsonify({
        'total_policies': policy_stats['total_policies'],
        'policy_distribution': {
            'active': policy_stats['active_policies'],
            'pending': policy_stats['pending_policies']
        },
        'claims_distribution': {
            'in_progress': claim_stats.get('in_progress_claims', 0),
            'approved': claim_stats.get('approved_claims', 0),
            'rejected': claim_stats.get('rejected_claims', 0)
        },
        'total_users': user_stats['total_users'],
        'fraud_detection_rate': fraud_detection_rate
    })

@admin_bp.route('/policies', methods=['GET'])
def get_all_policies():
    query = """
    MATCH (u:User)-[:INSURANCE]->(a:Application)
    OPTIONAL MATCH (u)-[:HAS_BANKING_DETAILS]->(b:BankingDetails)
    OPTIONAL MATCH (u)-[:HAS_DETAILS]->(d:OtherDetails)
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
           d.occupation as occupation,
           d.education_level as education,
           d.dob as date_of_birth
    ORDER BY a.created_at DESC
    """
    
    policies = neo4j.execute_query(query)
    formatted_policies = []
    
    for policy in policies:
        formatted_policy = {
            'id': policy['policy_id'],
            'vehicleDetails': {
                'type': policy['vehicle_type'],
                'registrationNumber': policy['registration_number'],
                'make': policy['make'],
                'model': policy['model'],
                'year': int(policy['year'])
            },
            'personalInfo': {
                'fullName': policy['applicant_name'],
                'mobile': policy['mobile'],
                'email': policy['email'],
                'address': policy['address'],
                'city': policy['city'],
                'state': policy['state'],
                'customerId': policy['customer_id'],
                'panNumber': policy.get('pan_number'),
                'occupation': policy.get('occupation'),
                'education': policy.get('education'),
                'dateOfBirth': policy.get('date_of_birth')
            },
            'policyDetails': {
                'idv': float(policy['idv']),
                'ncb': float(policy['ncb']),
                'csl': float(policy['csl']),
                'umbrellaLimit': float(policy['umbrella_limit']),
                'totalInsuranceAmount': float(policy['total_amount']),
                'addOns': eval(policy['addons']) if policy['addons'] else [],
                'premium': float(policy['premium'])
            },
            'status': policy['status'],
            'timestamps': {
                'created': policy['created_at'],
                'updated': policy['updated_at']
            }
        }
        
        formatted_policies.append(formatted_policy)
    
    return jsonify(formatted_policies)

@admin_bp.route('/claims', methods=['GET'])
def get_all_claims():
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
    
    claims = neo4j.execute_query(query)
    formatted_claims = []
    
    for claim in claims:
        color_code = get_fraud_color_code(claim)
        
        claim_details = {
            'claimManagementId': claim.get('claim_management_id'),
            'claimType': claim.get('claim_type'),
            'status': claim.get('status'),
            'lastUpdated': claim.get('submission_date'),
            'fraudProbability': claim.get('fraudProbability'),
            'fraudPrediction': claim.get('fraudPrediction'),
            'fraudReason': claim.get('fraudReason'),
            'claimId': claim.get('claim_id'),
            'severity': claim.get('severity'),
            'vehicleAmount': claim.get('vehicle_amount'),
            'totalAmount': claim.get('total_amount'),
            'propertyAmount': claim.get('property_amount'),
            'injuryAmount': claim.get('injury_amount'),
            'claimDetailType': claim.get('claim_detail_type'),
            'incident': {
                'date': claim.get('incident_date'),
                'city': claim.get('incident_city'),
                'location': claim.get('incident_location')
            },
            'customerId': claim.get('customer_id'),
            'colorCode': color_code
        }
        
        formatted_claims.append({
            'userName': claim.get('user_name'),
            'claimDetails': claim_details
        })
    
    return jsonify(formatted_claims)

def get_policy_documents(policy_id):
    """
    Fetches file documents associated with a given policy from the Neo4j database.
    Returns a list of documents with confidence, predicted label, file path, file name, and upload date.
    """
    query = """
    MATCH (a:Application {application_id: $policy_id})-[:HAS_DOCUMENT]->(f:File)
    RETURN f.confidence AS confidence,
           f.predicted_label AS predicted_label,
           f.file_path AS file_path,
           f.file_name AS file_name,
           f.upload_date AS upload_date
    """
    documents = neo4j.execute_query(query, parameters={"policy_id": policy_id})
    formatted_docs = []
    for doc in documents:
        formatted_docs.append({
            "confidence": doc.get("confidence"),
            "label": doc.get("predicted_label"),
            "filePath": doc.get("file_path"),
            "fileName": doc.get("file_name"),
            "uploadDate": doc.get("upload_date")
        })
    return formatted_docs

@admin_bp.route('/documents/<policy_id>', methods=['GET'])
def get_documents(policy_id):
    """
    Endpoint to fetch and return file documents for a given policy.
    """
    documents = get_policy_documents(policy_id)
    return jsonify(documents)
