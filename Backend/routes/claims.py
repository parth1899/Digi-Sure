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

    # Query to check if ClaimManagement node exists
    check_query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN cm
    """

    # Query to create a new ClaimManagement node and attach the claim
    create_query = """
    MATCH (u:User {email: $email})
    CREATE 
        (cm:ClaimManagement {
            id: $management_id,
            status: 'In Progress',
            last_updated: $created_date,
            incident_type: $incident_type
        }),
        (c:Claim {
            id: $claim_id,
            collision_type: $collision_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim,
            authorities_contacted: $authorities_contacted,
            description: $description
        }),
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
        (c)-[:OCCURRED_ON]->(i)
    RETURN c.id as claim_id, cm.id as management_id
    """

    # Query to attach a claim to an existing ClaimManagement node
    attach_query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    CREATE 
        (c:Claim {
            id: $claim_id,
            collision_type: $collision_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim,
            authorities_contacted: $authorities_contacted,
            description: $description
        }),
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
        (cm)-[:MANAGES]->(c),
        (c)-[:OCCURRED_ON]->(i)
    RETURN c.id as claim_id, cm.id as management_id
    """

    params = {
        'created_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': current_user_email,
        'management_id': management_id,
        'claim_id': claim_id,
        'incident_id': f"incident_{claim_id}",
        'incident_type': data['incident_type'],
        'collision_type': data['collision_type'],
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
        'police_report': data['police_report_available'],
        'authorities_contacted': data['authorities_contacted'],
        'description': data['description'],
    }

    try:
        # Check if ClaimManagement node exists
        existing_cm = neo4j.execute_query(check_query, {'email': current_user_email})

        if existing_cm:
            # Attach claim to existing ClaimManagement node
            result = neo4j.execute_query(attach_query, params)
        else:
            # Create new ClaimManagement node and attach claim
            result = neo4j.execute_query(create_query, params)

        # Call fraud detection and analysis functions
        predict_from_neo4j(customer_id=current_user_email)
        analyze_fraud_and_save(result[0]['management_id'])

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
    RETURN cm, c, i
    """

    try:
        result = neo4j.execute_query(query, {'email': current_user_email})
        claims = []

        for record in result:
            claim_management = record['cm']
            claim = record['c']
            incident = record['i']

            claims.append({
                'claim_management_id': claim_management['id'],
                'claim_management_status': claim_management['status'],
                'claim_management_last_updated': claim_management['last_updated'],
                'claim_id': claim['id'],
                'collision_type': claim['collision_type'],
                'severity': claim['severity'],
                'total_amount': claim['total_amount'],
                'injury_amount': claim['injury_amount'],
                'property_amount': claim['property_amount'],
                'vehicle_amount': claim['vehicle_amount'],
                'authorities_contacted': claim['authorities_contacted'],
                'description': claim['description'],
                'incident_id': incident['id'],
                'incident_date': incident['date'],
                'incident_time': incident['time'],
                'incident_location': incident['location'],
                'incident_city': incident['city'],
                'vehicles_involved': incident['vehicles_involved'],
                'witnesses': incident['witnesses'],
                'property_damage': incident['property_damage'],
                'bodily_injuries': incident['bodily_injuries'],
                'police_report': incident['police_report']
            })

        return jsonify(claims), 200
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'Failed to fetch claims.'}), 500


@claims_bp.route('/update_claim', methods=['POST'])
def update_claim():
    """Update claim and link to ClaimManagement node"""

    data = request.json
    claim_id = str(uuid.uuid4())
    email = data.get('email')

    # Generate a unique management ID
    management_id = f"management_{email}_{uuid.uuid4()}"

    # Query to check if ClaimManagement node exists
    check_query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    RETURN cm
    """

    # Query to create a new ClaimManagement node and attach the claim
    create_query = """
    MATCH (u:User {email: $email})
    CREATE 
        (cm:ClaimManagement {
            id: $management_id,
            status: 'In Progress',
            last_updated: $created_date,
            incident_type: $incident_type
        }),
        (c:Claim {
            id: $claim_id,
            collision_type: $collision_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim,
            authorities_contacted: $authorities_contacted,
            description: $description
        }),
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
        (c)-[:OCCURRED_ON]->(i)
    RETURN c.id as claim_id, cm.id as management_id
    """

    # Query to attach a claim to an existing ClaimManagement node
    attach_query = """
    MATCH (u:User {email: $email})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    CREATE 
        (c:Claim {
            id: $claim_id,
            collision_type: $collision_type,
            severity: $incident_severity,
            total_amount: $total_claim_amount,
            injury_amount: $injury_claim,
            property_amount: $property_claim,
            vehicle_amount: $vehicle_claim,
            authorities_contacted: $authorities_contacted,
            description: $description
        }),
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
        (cm)-[:MANAGES]->(c),
        (c)-[:OCCURRED_ON]->(i)
    RETURN c.id as claim_id, cm.id as management_id
    """

    params = {
        'created_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'email': email,
        'management_id': management_id,
        'claim_id': claim_id,
        'incident_id': f"incident_{claim_id}",
        'incident_type': data['incident_type'],
        'collision_type': data['collision_type'],
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
        'police_report': data['police_report_available'],
        'authorities_contacted': data['authorities_contacted'],
        'description': data['description'],
    }

    try:
        # Check if ClaimManagement node exists
        existing_cm = neo4j.execute_query(check_query, {'email': email})

        if existing_cm:
            # Attach claim to existing ClaimManagement node
            result = neo4j.execute_query(attach_query, params)
        else:
            # Create new ClaimManagement node and attach claim
            result = neo4j.execute_query(create_query, params)

        # Call fraud detection and analysis functions
        predict_from_neo4j(customer_id=email)
        analyze_fraud_and_save(result[0]['management_id'])

        return jsonify({'claim_id': result[0]['claim_id']}), 201
    except Exception as e:
        print(f"Error occurred: {e}")
        return jsonify({'error': 'Failed to process the claim.'}), 500
