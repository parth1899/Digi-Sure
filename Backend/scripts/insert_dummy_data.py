import pandas as pd
from datetime import datetime
from pathlib import Path
import uuid
import sys
from os.path import dirname
import secrets
import string
import bcrypt

# Add the Backend directory to Python path so we can import from database package
backend_dir = dirname(dirname(__file__))
sys.path.append(backend_dir)

from database.connection import Neo4jConnection

def generate_strong_password():
    # Define character sets for password
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "!@#$%^&*"
    all_chars = letters + digits + special_chars

    # Generate a strong password of length 12
    password = ''.join(secrets.choice(letters) for _ in range(2))  # At least 2 letters
    password += ''.join(secrets.choice(digits) for _ in range(2))  # At least 2 digits
    password += ''.join(secrets.choice(special_chars) for _ in range(2))  # At least 2 special chars
    password += ''.join(secrets.choice(all_chars) for _ in range(6))  # 6 more random chars

    # Shuffle the password to make it more random
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    return ''.join(password_list)

def encrypt_password(password):
    # Generate a salt and hash the password using bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def convert_date_format(date_str):
    try:
        # Convert from DD-MM-YYYY to YYYY-MM-DD
        date_obj = datetime.strptime(date_str, '%d-%m-%Y')
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # If already in YYYY-MM-DD format
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            raise ValueError(f"Date {date_str} is not in either DD-MM-YYYY or YYYY-MM-DD format")

def serialize_neo4j_data(data):
    """Convert Neo4j data types to JSON serializable formats"""
    from neo4j.time import DateTime
    if isinstance(data, DateTime):
        return data.isoformat()
    return data

def fetch_data_from_neo4j(driver, query, params=None):
    """Execute Neo4j query with proper date serialization"""
    data = []
    with driver.session() as session:
        results = session.run(query, params or {})
        records = results.data()
        for record in records:
            datapoint = {}
            for key in record:
                node = record.get(key)
                if node:
                    props = node._properties if hasattr(node, "_properties") else node
                    # Serialize each value
                    datapoint.update({k: serialize_neo4j_data(v) for k, v in props.items()})
            data.append(datapoint)
    return pd.DataFrame(data)

def load_data():
    csv_path = Path(__file__).resolve().parent / 'Data.csv'
    return pd.read_csv(csv_path)

def insert_data(neo4j_connection, data):
    for _, row in data.iterrows():
        # Generate and encrypt password for each user
        password = generate_strong_password()
        password_hash = encrypt_password(password)
        
        # Print the generated password (in real system, would be sent to user securely)
        print(f"Generated password for {row['email']}: {password}")
        
        # Format dates for Neo4j using ISO format strings
        created_at = datetime.strptime(row['created_at'], '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
        dob = convert_date_format(row['dob'])
        
        # Handle incident date and time
        if pd.notna(row['incident_date']):
            incident_date = convert_date_format(row['incident_date'])
            incident_time = row['incident_time']
            incident_datetime = datetime.strptime(f"{incident_date} {incident_time}", '%Y-%m-%d %H:%M')
            last_updated = incident_datetime.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            incident_date = None
            incident_time = None
            last_updated = created_at
        vehicle_insurance_ids = {}
        vehicle_type = row['vehicle_type'].lower()
        if vehicle_type not in vehicle_insurance_ids:
            vehicle_insurance_ids[vehicle_type] = str(uuid.uuid4())

        # Create User node with basic information
        create_user = """
        MERGE (u:User {email: $email})
        SET u.name = $name,
            u.mobile = $mobile,
            u.customerId = $customer_id,
            u.address = $address,
            u.created_at = datetime($created_at),
            u.password_hash = $password_hash
        """
        
        # Create OtherDetails node and link to User
        create_other_details = """
        MATCH (u:User {email: $email})
        CREATE (od:OtherDetails)
        SET od.dob = date($dob),
            od.education_level = $education_level,
            od.hobbies = $hobbies,
            od.occupation = $occupation,
            od.relationship = $relationship,
            od.sex = $sex
        CREATE (u)-[:HAS_DETAILS]->(od)
        """

        # Parse addons from CSV
        try:
            import json
            addons_list = json.loads(row['addons']) if pd.notna(row['addons']) else []
        except (json.JSONDecodeError, TypeError):
            addons_list = []

        # Create Application node and link to User
        create_application = """
        MATCH (u:User {email: $email})
        CREATE (a:Application {
            addons: $addons,
            address: $app_address,
            applicant_name: $applicant_name,
            application_id: $application_id,
            city: $app_city,
            created_at: datetime($app_created_at),
            email: $email,
            idv: $idv,
            mobile: $app_mobile,
            make: $make,
            model: $model,
            ncb: $ncb,
            policy_annual_premium: $policy_annual_premium,
            policy_csl: $policy_csl,
            registration_number: $registration_number,
            state: $app_state,
            status: $status,
            total_insurance_amount: $total_insurance_amount,
            umbrella_limit: $umbrella_limit,
            updated_at: datetime($app_updated_at),
            year: $year
        })
        WITH a, u
        MERGE (vt:VehicleType { type: $vehicle_type })
        ON CREATE SET vt.created_at = datetime($app_created_at)
        CREATE (a)-[:FOR_VEHICLE_TYPE]->(vt)
        MERGE (vi:VehicleInsurance { id: $vehicle_insurance_id })
        ON CREATE SET vi.type = $vehicle_type
        CREATE (vt)-[:HAS_INSURANCE]->(vi)
        CREATE (u)-[:INSURANCE]->(a)
        """

        # Create BankingDetails node and link to User
        create_banking_details = """
        MATCH (u:User {email: $email})
        CREATE (bd:BankingDetails {
            aadharNumber: $aadhar_number,
            accountNumber: $account_number,
            ifscCode: $ifsc_code,
            panNumber: $pan_number
        })
        CREATE (u)-[:HAS_BANKING_DETAILS]->(bd)
        """
        
        # Create ClaimManagement node and link to User
        create_claim_management = """
        MATCH (u:User {email: $email})
        CREATE (cm:ClaimManagement {
            id: $management_id,
            claim_type: $claim_type,
            status: 'Pending',
            last_updated: datetime($last_updated),
            fraudPrediction: $fraud_prediction,
            fraudProbability: $fraud_probability,
            fraudReason: $fraud_reason
        })
        CREATE (u)-[:HAS_CLAIMS]->(cm)
        """
        
        # Create Claim node and link to ClaimManagement
        create_claim = """
        MATCH (cm:ClaimManagement {id: $management_id})
        CREATE (c:Claim {
            id: $claim_id,
            type: $claim_type,
            severity: $claim_severity,
            total_amount: $total_amount,
            vehicle_amount: $vehicle_amount,
            property_amount: $property_amount,
            injury_amount: $injury_amount
        })
        CREATE (cm)-[:MANAGES]->(c)
        """
        
        # Create Customer node and link to Claim
        create_customer = """
        MATCH (c:Claim {id: $claim_id})
        CREATE (cust:Customer {id: $customer_node_id})
        CREATE (c)-[:FILED_BY]->(cust)
        """
        
        # Create Incident node and link to Claim and Customer
        create_incident = """
        MATCH (c:Claim {id: $claim_id})
        MATCH (cust:Customer {id: $customer_node_id})
        CREATE (i:Incident {
            id: $incident_id,
            city: $incident_city,
            location: $incident_location,
            date: date($incident_date),
            time: $incident_time,
            vehicles_involved: $vehicles_involved,
            witnesses: $witnesses,
            police_report: $police_report,
            bodily_injuries: CASE WHEN $injury_amount > 0 THEN 'Yes' ELSE 'No' END,
            property_damage: CASE WHEN $property_amount > 0 THEN 'Yes' ELSE 'No' END
        })
        CREATE (c)-[:OCCURRED_ON]->(i)
        CREATE (cust)-[:INVOLVED_IN]->(i)
        """

        # Generate IDs
        claim_id = str(uuid.uuid4())
        management_id = f"management_{row['email']}"
        customer_node_id = f"customer_{row['email']}"
        incident_id = f"incident_{claim_id}"
        
        # Execute the Cypher queries using execute_query method
        neo4j_connection.execute_query(create_user, {
            'email': row['email'],
            'name': row['name'],
            'mobile': row['mobile'],
            'customer_id': row['customer_id'],
            'address': row['address'],
            'created_at': created_at,
            'password_hash': password_hash
        })

        # Execute OtherDetails creation
        neo4j_connection.execute_query(create_other_details, {
            'email': row['email'],
            'dob': dob,
            'education_level': row['education_level'],
            'hobbies': row['hobbies'],
            'occupation': row['occupation'],
            'relationship': row['relationship'],
            'sex': row['sex']
        })

        # Execute Application creation
        neo4j_connection.execute_query(create_application, {
            'email': row['email'],
            'addons': addons_list,
            'app_address': row['address'],
            'applicant_name': row['name'],
            'application_id': f"APP{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'app_city': row['insurance_city'],
            'app_created_at': created_at,
            'idv': float(row['idv']),
            'app_mobile': row['mobile'],
            'make': row['vehicle_make'],
            'model': row['vehicle_model'],
            'ncb': float(row['ncb']),
            'policy_annual_premium': float(row['policy_annual_premium']),
            'policy_csl': float(row['policy_csl']),
            'registration_number': f"MH12{uuid.uuid4().hex[:4].upper()}",
            'app_state': row['insurance_state'],
            'status': 'PENDING',
            'total_insurance_amount': float(row['total_insurance_amount']),
            'umbrella_limit': float(row['umbrella_limit']),
            'app_updated_at': created_at,
            'vehicle_type': row['vehicle_type'].lower(),
            'year': int(row['year']),
            'vehicle_type': vehicle_type,
            'vehicle_insurance_id': vehicle_insurance_ids[vehicle_type]
        })

        # Execute BankingDetails creation
        neo4j_connection.execute_query(create_banking_details, {
            'email': row['email'],
            'aadhar_number': str(row['aadhar_number']),
            'account_number': str(row['account_number']),
            'ifsc_code': row['ifsc_code'],
            'pan_number': str(row['pan_number'])
        })

        # Execute ClaimManagement creation with fraud_probability
        if pd.notna(row['claim_type']):
            neo4j_connection.execute_query(create_claim_management, {
                'email': row['email'],
                'management_id': management_id,
                'claim_type': row['claim_type'],
                'last_updated': last_updated,
                'fraud_prediction': int(row['fraudPrediction']),
                'fraud_probability': float(row['fraud_probability']),
                'fraud_reason': row['fraudReason']
            })

            neo4j_connection.execute_query(create_claim, {
                'management_id': management_id,
                'claim_id': claim_id,
                'claim_type': row['claim_type'],
                'claim_severity': row['claim_severity'],
                'total_amount': float(row['total_amount']),
                'vehicle_amount': float(row['vehicle_amount']),
                'property_amount': float(row['property_amount']),
                'injury_amount': float(row['injury_amount'])
            })

            neo4j_connection.execute_query(create_customer, {
                'claim_id': claim_id,
                'customer_node_id': customer_node_id
            })

            neo4j_connection.execute_query(create_incident, {
                'claim_id': claim_id,
                'customer_node_id': customer_node_id,
                'incident_id': incident_id,
                'incident_city': row['incident_city'],
                'incident_location': row['incident_location'],
                'incident_date': incident_date,
                'incident_time': incident_time,
                'vehicles_involved': int(row['vehicles_involved']),
                'witnesses': int(row['witnesses']),
                'police_report': row['police_report'] == 'Yes',
                'injury_amount': float(row['injury_amount']),
                'property_amount': float(row['property_amount'])
            })

def main():
    print("Loading data from CSV...")
    data = load_data()
    
    print("Connecting to Neo4j database...")
    neo4j_connection = Neo4jConnection()
    
    try:
        print("Inserting data into Neo4j...")
        insert_data(neo4j_connection, data)
        print("Data insertion completed successfully!")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        neo4j_connection.close()

if __name__ == "__main__":
    main()