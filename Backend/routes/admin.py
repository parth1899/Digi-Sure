from flask import Blueprint, jsonify
from database.connection import Neo4jConnection
from datetime import datetime

admin_bp = Blueprint('admin', __name__)
neo4j = Neo4jConnection()

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
    MATCH (u:User)-[:HAS_CLAIMS]->(c:ClaimManagement)
    RETURN count(c) as total_claims,
           count(CASE WHEN c.status = 'Pending' THEN 1 END) as pending_claims,
           count(CASE WHEN c.status = 'Approved' THEN 1 END) as approved_claims,
           count(CASE WHEN c.status = 'Rejected' THEN 1 END) as rejected_claims
    """
    
    # Query to get total users
    users_query = """
    MATCH (u:User)
    RETURN count(u) as total_users
    """
    
    policy_stats = neo4j.execute_query(policies_query)[0]
    claim_stats = neo4j.execute_query(claims_query)[0]
    user_stats = neo4j.execute_query(users_query)[0]
    
    return jsonify({
        'total_policies': policy_stats['total_policies'],
        'policy_distribution': {
            'active': policy_stats['active_policies'],
            'pending': policy_stats['pending_policies']
        },
        'claims_distribution': {
            'approved': claim_stats['approved_claims'],
            'pending': claim_stats['pending_claims'],
            'rejected': claim_stats['rejected_claims']
        },
        'total_users': user_stats['total_users'],
        'fraud_detection_rate': 15  # This would come from your ML model in production
    })

@admin_bp.route('/policies', methods=['GET'])
def get_all_policies():
    # Simplified query to fetch only stored data without calculations
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
                'panNumber': policy['pan_number'],
                'occupation': policy['occupation'],
                'education': policy['education'],
                'dateOfBirth': policy['date_of_birth']
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

def calculate_forgery_score(policy):
    # Placeholder for ML model integration
    # In production, this would use your actual ML model
    return 15

def calculate_risk_level(policy):
    # Implement risk level calculation based on various factors
    # This is a placeholder implementation
    risk_factors = {
        'vehicle_age': 2025 - int(policy['year']),
        'premium_size': float(policy['premium']),
        'umbrella_limit': float(policy['umbrella_limit'])
    }
    
    # Simple risk calculation example
    risk_score = 0
    if risk_factors['vehicle_age'] > 10:
        risk_score += 20
    if risk_factors['premium_size'] > 1000:
        risk_score += 15
    if risk_factors['umbrella_limit'] > 1000000:
        risk_score += 25
        
    return 'HIGH' if risk_score > 50 else 'MEDIUM' if risk_score > 25 else 'LOW'

def get_risk_flags(policy):
    # Implement logic to identify any risk flags
    flags = []
    
    # Example flag checks
    if float(policy['premium']) > 1000:
        flags.append('High Premium Amount')
    if 2025 - int(policy['year']) > 10:
        flags.append('Old Vehicle')
    if float(policy['umbrella_limit']) > 1000000:
        flags.append('High Umbrella Coverage')
        
    return flags

def get_policy_documents(policy_id):
    # This would typically fetch documents from your database
    # Returning placeholder data for now
    return [
        {
            'name': 'Registration Certificate',
            'type': 'Vehicle',
            'status': 'Verified',
            'forgeryScore': 12
        },
        {
            'name': 'Insurance Declaration',
            'type': 'Policy',
            'status': 'Pending',
            'forgeryScore': 8
        },
        {
            'name': 'Identity Proof',
            'type': 'ID',
            'status': 'Verified',
            'forgeryScore': 15
        }
    ]

@admin_bp.route('/claims', methods=['GET'])
def get_all_claims():
    query = """
    MATCH (u:User)-[:HAS_CLAIMS]->(c:ClaimManagement)
    RETURN u.name as user_name,
           c.id as claim_id,
           c.claim_type as claim_type,
           c.status as status,
           c.last_updated as submission_date
    """
    
    claims = neo4j.execute_query(query)
    formatted_claims = []
    
    for claim in claims:
        formatted_claims.append({
            'id': claim['claim_id'],
            'userName': claim['user_name'],
            'claimType': claim['claim_type'],
            'amount': 5000,  # This would come from your actual data
            'submissionDate': claim['submission_date'],
            'isFraudulent': False,  # This would come from your ML model
            'status': claim['status'],
            'details': 'Claim details would go here'  # This would come from your actual data
        })
    
    return jsonify(formatted_claims)