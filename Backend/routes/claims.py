import datetime
from flask import Blueprint, request, jsonify
from database.connection import Neo4jConnection
from utils.auth import token_required
import uuid
from utils.detector import FraudDetector

claims_bp = Blueprint('claims', __name__)
neo4j = Neo4jConnection()
fraud_detector = FraudDetector()

@claims_bp.route('/detect', methods=['POST'])
@token_required
def create_claim(current_user_email):
    data = request.json
    claim_id = str(uuid.uuid4())
    
    # Create nodes and relationships
    query = """
    MATCH (u:User {email: $email})
    CREATE 
        // Create central claim management node if not exists
        (cm:ClaimManagement {
            id: $management_id,
            status: 'In Progress',
            last_updated: $created_date,
            claim_type: $incident_type
        }),
        // Create claim node
        (c:Claim {
            id: $claim_id,
            type: $incident_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim
        }),
        // Create customer node
        (cust:Customer {id: $customer_id}),
        // Create incident node
        (i:Incident {
            id: $incident_id,
            date: $incident_date,
            time: $incident_hour,
            location: $incident_location,
            city: $incident_city,
            vehicles_involved: $vehicles_involved,
            witnesses: $witnesses,
            property_damage: $property_damage,
            bodily_injuries: $bodily_injuries,
            police_report: $police_report
        }),
        // Create relationships
        (u)-[:HAS_CLAIMS]->(cm),
        (cm)-[:MANAGES]->(c),
        (c)-[:FILED_BY]->(cust),
        (c)-[:OCCURRED_ON]->(i),
        (cust)-[:INVOLVED_IN]->(i)
    RETURN c.id as claim_id
    """
    
    params = {
        'created_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': current_user_email,
        'management_id': f"management_{current_user_email}",
        'claim_id': claim_id,
        'customer_id': f"customer_{current_user_email}",
        'incident_id': f"incident_{claim_id}",
        'incident_type': data['incident_type'],
        'incident_severity': data['incident_severity'],
        'total_claim_amount': float(data['total_claim_amount']),
        'injury_claim': float(data['injury_claim']),
        'property_claim': float(data['property_claim']),
        'vehicle_claim': float(data['vehicle_claim']),
        'incident_date': data['incident_date'],
        'incident_hour': data['incident_hour_of_the_day'],
        'incident_location': data['incident_location'],
        'incident_city': data['incident_city'],
        'vehicles_involved': int(data['number_of_vehicles_involved']),
        'witnesses': int(data['witnesses']),
        'property_damage': data['property_damage'],
        'bodily_injuries': data['bodily_injuries'],
        'police_report': data['police_report_available']
    }
    
    result = neo4j.execute_query(query, params)
    return jsonify({'claim_id': result[0]['claim_id']}), 201

@claims_bp.route('/view', methods=['GET'])
@token_required
def get_claims(current_user_email):
    query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    MATCH (cm)-[:MANAGES]->(c:Claim)-[:OCCURRED_ON]->(i:Incident)
    RETURN cm, c, i
    """
    
    result = neo4j.execute_query(query, {'email': current_user_email})
    claims = []
    
    for record in result:
        claimManagement = record['cm']
        claim = record['c']
        incident = record['i']
        
        # Include fraud prediction information
        fraud_info = {
            'prediction': claimManagement.get('fraud_prediction', 'Not evaluated'),
            'probability': claimManagement.get('fraud_probability', 0.0),
            'reasons': claimManagement.get('fraud_reasons', 'Not evaluated')
        }
        
        claims.append({
            'id': claim['id'],
            'type': claim['type'],
            'severity': claim['severity'],
            'total_amount': claim['total_amount'],
            'incident_date': incident['date'],
            'incident_location': incident['location'],
            'status': claimManagement['status'],
            'fraud_assessment': fraud_info
        })
    
    return jsonify(claims)