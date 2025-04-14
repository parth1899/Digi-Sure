import datetime
from flask import Blueprint, request, jsonify
from database.connection import Neo4jConnection
from utils.auth import token_required
import uuid
from utils.detector import predict_from_neo4j, analyze_fraud_and_save

claims_bp = Blueprint('claims', __name__)
neo4j = Neo4jConnection()

@claims_bp.route('/detect', methods=['POST'])
@token_required
def create_claim(current_user_email):
    data = request.json
    claim_id = str(uuid.uuid4())
    
    # Generate a unique management ID
    management_id = f"management_{current_user_email}_{uuid.uuid4()}"

    # Update the query to use the unique management ID
    query = """
    MATCH (u:User {email: $email})
    CREATE 
        (cm:ClaimManagement {
            id: $management_id,
            status: 'In Progress',
            last_updated: $created_date,
            claim_type: $incident_type
        }),
        (c:Claim {
            id: $claim_id,
            type: $incident_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim
        }),
        (cust:Customer {id: $customer_id}),
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
        (u)-[:HAS_CLAIMS]->(cm),
        (cm)-[:MANAGES]->(c),
        (c)-[:FILED_BY]->(cust),
        (c)-[:OCCURRED_ON]->(i),
        (cust)-[:INVOLVED_IN]->(i)
    RETURN c.id as claim_id, cust.id AS customer_id
    """
    
    params = {
        'created_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': current_user_email,
        'management_id': management_id,
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

    # Execute the query only after successful endpoint execution
    try:
        result = neo4j.execute_query(query, params)
        customer_id = result[0]['customer_id']

        # Pass the customer ID to the fraud detection function
        predict_from_neo4j(customer_id=customer_id)

        # Call the fraud analysis function
        analyze_fraud_and_save(management_id)

        return jsonify({'claim_id': result[0]['claim_id']}), 201
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'Failed to process the claim.'}), 500


@claims_bp.route('/view', methods=['GET'])
@token_required
def get_claims(current_user_email):
    # Query to fetch claim details along with customer ID and fraud assessment
    query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    MATCH (cm)-[:MANAGES]->(c:Claim)-[:OCCURRED_ON]->(i:Incident)
    OPTIONAL MATCH (c)-[:FILED_BY]->(cust:Customer)
    RETURN cm, c, i, cust
    """
    
    result = neo4j.execute_query(query, {'email': current_user_email})
    claims = []
    
    for record in result:
        claim_management = record['cm']
        claim = record['c']
        incident = record['i']
        customer = record.get('cust', {})

        # Extract customer ID and fraud assessment
        customer_id = customer.get('id', 'Unknown')
        fraud_info = {
            'customer_id': customer_id,
            'prediction': claim_management.get('fraud_prediction', 'Not evaluated'),
            'probability': claim_management.get('fraud_probability', 0.0),
            'reason': claim_management.get('fraud_reason', 'Not evaluated')
        }
        
        claims.append({
            'id': claim['id'],
            'customer_id': customer_id,
            'type': claim['type'],
            'severity': claim['severity'],
            'total_amount': claim['total_amount'],
            'incident_date': incident['date'],
            'incident_location': incident['location'],
            'status': claim_management['status'],
            'fraud_assessment': fraud_info
        })
    
    return jsonify(claims)
