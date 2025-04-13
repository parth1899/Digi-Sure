import os

from database.connection import Neo4jConnection
os.environ["CUDA_VISIBLE_DEVICES"] = ""  # Ensure GPU is disabled

import pandas as pd
import joblib
from neo4j import GraphDatabase
from datetime import datetime

# --- Expected Prediction Feature Order (as used during training) ---
PREDICTION_COLUMNS = [
    'Month', 'WeekOfMonth', 'DayOfWeek', 'Make', 'AccidentArea',
    'DayOfWeekClaimed', 'MonthClaimed', 'WeekOfMonthClaimed', 'Sex',
    'MaritalStatus', 'Age', 'Fault', 'PolicyType', 'VehiclePrice',
    'RepNumber', 'Deductible', 'DriverRating', 'Days:Policy-Accident',
    'Days:Policy-Claim', 'PastNumberOfClaims', 'AgeOfVehicle',
    'PoliceReportFiled', 'WitnessPresent', 'AgentType',
    'NumberOfSuppliments',  # Note: using the misspelled key to match training
    'AddressChange-Claim', 'NumberOfCars', 'Year'
]

MODEL_SAVE_PATH = "xgb_fraud_model_gridcv.pkl"

# --- Neo4j Data Fetching ---
def fetch_data_from_neo4j(driver, query, params=None):
    """
    Execute the provided Neo4j query with optional parameters and merge the properties 
    of all returned nodes into a single dictionary per record.
    """
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
                    datapoint.update(props)
            data.append(datapoint)
    return pd.DataFrame(data)

# --- Data Transformation ---
def transform_neo4j_data_for_model(neo4j_data: dict) -> dict:
    """
    Map the merged Neo4j node properties into features expected by the model.
    Where data is missing, default values are used.
    """
    transformed = {}
    
    # Incident Date Features
    incident_date_str = neo4j_data.get("date")
    if incident_date_str:
        try:
            incident_date = pd.to_datetime(incident_date_str)
            transformed["Month"] = incident_date.month
            transformed["WeekOfMonth"] = ((incident_date.day - 1) // 7) + 1
            transformed["DayOfWeek"] = incident_date.weekday()
        except Exception:
            transformed["Month"] = transformed["WeekOfMonth"] = transformed["DayOfWeek"] = 0
    else:
        transformed["Month"] = transformed["WeekOfMonth"] = transformed["DayOfWeek"] = 0

    # Accident & Claim Features
    transformed["Make"] = neo4j_data.get("make", "Unknown")
    transformed["AccidentArea"] = neo4j_data.get("location", "Unknown")
    
    claim_date_str = neo4j_data.get("last_updated")
    if claim_date_str:
        try:
            claim_date = pd.to_datetime(claim_date_str)
            transformed["DayOfWeekClaimed"] = claim_date.weekday()
            transformed["MonthClaimed"] = claim_date.month
            transformed["WeekOfMonthClaimed"] = ((claim_date.day - 1) // 7) + 1
        except Exception:
            transformed["DayOfWeekClaimed"] = transformed["MonthClaimed"] = transformed["WeekOfMonthClaimed"] = 0
    else:
        transformed["DayOfWeekClaimed"] = transformed["MonthClaimed"] = transformed["WeekOfMonthClaimed"] = 0

    # User Details
    transformed["Sex"] = neo4j_data.get("sex", "Unknown")
    transformed["MaritalStatus"] = neo4j_data.get("maritalStatus", "Unknown")
    dob_str = neo4j_data.get("dob")
    if dob_str:
        try:
            birth_year = int(dob_str.split("/")[-1])
            transformed["Age"] = datetime.now().year - birth_year
        except Exception:
            transformed["Age"] = 0
    else:
        transformed["Age"] = 0
    transformed["Fault"] = neo4j_data.get("claim_type", "Unknown")
    
    # Policy & Vehicle Details
    transformed["PolicyType"] = neo4j_data.get("policyType", "Unknown")
    try:
        transformed["VehiclePrice"] = float(neo4j_data.get("idv", 0))
    except Exception:
        transformed["VehiclePrice"] = 0
    transformed["RepNumber"] = neo4j_data.get("repNumber", 0)
    try:
        total_ins_amount = float(neo4j_data.get("total_insurance_amount", 0))
        ncb = float(neo4j_data.get("ncb", 0))
        transformed["Deductible"] = total_ins_amount * ncb / 100
    except Exception:
        transformed["Deductible"] = 0
    transformed["DriverRating"] = neo4j_data.get("driverRating", 0)
    
    # Time Differences
    policy_bind_str = neo4j_data.get("created_at")
    if policy_bind_str and incident_date_str:
        try:
            policy_bind_date = pd.to_datetime(policy_bind_str)
            incident_date = pd.to_datetime(incident_date_str)
            transformed["Days:Policy-Accident"] = (incident_date - policy_bind_date).days
        except Exception:
            transformed["Days:Policy-Accident"] = 0
    else:
        transformed["Days:Policy-Accident"] = 0

    if policy_bind_str and claim_date_str:
        try:
            policy_bind_date = pd.to_datetime(policy_bind_str)
            claim_date = pd.to_datetime(claim_date_str)
            transformed["Days:Policy-Claim"] = (claim_date - policy_bind_date).days
        except Exception:
            transformed["Days:Policy-Claim"] = 0
    else:
        transformed["Days:Policy-Claim"] = 0

    # Additional Details
    transformed["PastNumberOfClaims"] = neo4j_data.get("pastClaims", 0)
    year_str = neo4j_data.get("year")
    if year_str:
        try:
            transformed["AgeOfVehicle"] = datetime.now().year - int(year_str)
        except Exception:
            transformed["AgeOfVehicle"] = 0
    else:
        transformed["AgeOfVehicle"] = 0
    police_report = neo4j_data.get("police_report", "No")
    transformed["PoliceReportFiled"] = 1 if str(police_report).strip().lower() == "yes" else 0
    try:
        transformed["WitnessPresent"] = int(neo4j_data.get("witnesses", 0))
    except Exception:
        transformed["WitnessPresent"] = 0
    transformed["AgentType"] = neo4j_data.get("agentType", "Unknown")
    transformed["NumberOfSuppliments"] = neo4j_data.get("numberOfSupplements", 0)
    transformed["AddressChange-Claim"] = neo4j_data.get("addressChangeClaim", 0)
    transformed["NumberOfCars"] = neo4j_data.get("numberOfCars", 0)
    try:
        transformed["Year"] = int(year_str) if year_str else datetime.now().year
    except Exception:
        transformed["Year"] = datetime.now().year
    
    return transformed

# --- Store Prediction in ClaimManagement Node ---
def store_prediction_in_claim_management(driver, customer_id, prediction, fraud_prob, fraud_reason):
    """
    Update the ClaimManagement node associated with the given customer with the fraud prediction,
    fraud probability, and fraud reason.
    """
    update_query = """
    MATCH (u:User {customerId: $customer_id})-[:HAS_CLAIMS]->(cm:ClaimManagement)
    SET cm.fraudPrediction = $prediction,
        cm.fraudProbability = $fraud_prob,
        cm.fraudReason = $fraud_reason
    RETURN cm
    """
    with driver.session() as session:
        session.run(update_query, {
            "customer_id": customer_id,
            "prediction": int(prediction),
            "fraud_prob": float(fraud_prob),
            "fraud_reason": fraud_reason
        })

# --- Fraud Analysis ---
def analyze_fraud_and_save(claim_management_id):
    """
    Analyze fraud using external API and save the response to the database.
    
    :param claim_management_id: ID of the ClaimManagement node to update.
    """
    # Fetch claim data from Neo4j
    neo4j_conn = Neo4jConnection()
    query = """
    MATCH (cm:ClaimManagement {id: $claim_management_id})-[:MANAGES]->(c:Claim)-[:OCCURRED_ON]->(i:Incident)
    RETURN cm, c, i
    """
    params = {"claim_management_id": claim_management_id}
    df_raw = fetch_data_from_neo4j(neo4j_conn.driver, query, params)

    if df_raw.empty:
        print(f"No data fetched for claim management ID {claim_management_id}.")
        neo4j_conn.driver.close()
        return

    neo4j_data = df_raw.iloc[0].to_dict()
    features_dict = transform_neo4j_data_for_model(neo4j_data)

    # Prepare features for the model
    df_features = pd.DataFrame([features_dict]).reindex(columns=PREDICTION_COLUMNS, fill_value=0)

    # Convert object columns to categorical for XGBoost
    for col in df_features.select_dtypes(include='object').columns:
        df_features[col] = df_features[col].astype('category')

    # Load the model and make predictions
    model = joblib.load(MODEL_SAVE_PATH)
    prediction = model.predict(df_features)
    fraud_prob = model.predict_proba(df_features)[:, 1] if hasattr(model, "predict_proba") else None

    print(f"Prediction for {claim_management_id} (0: Not Fraud, 1: Fraud):", prediction[0])
    if fraud_prob is not None:
        print(f"Fraud Probability: {fraud_prob[0]}")

    # Update the ClaimManagement node with the fraud reason
    update_query = """
    MATCH (cm:ClaimManagement {id: $claim_management_id})
    SET cm.fraudPrediction = $prediction,
        cm.fraudProbability = $fraud_prob,
        cm.fraudReason = $fraud_reason
    """

    fraud_reason = "Fraud analysis completed. Reasoning not available in this version."

    neo4j_conn.execute_query(update_query, {
        "claim_management_id": claim_management_id,
        "prediction": int(prediction[0]),
        "fraud_prob": float(fraud_prob[0]) if fraud_prob is not None else 0,
        "fraud_reason": fraud_reason
    })

    neo4j_conn.driver.close()

# --- Prediction Pipeline ---
def predict_from_neo4j(customer_id, model_path=MODEL_SAVE_PATH):
    # Initialize Neo4j driver
    neo4j_conn = Neo4jConnection()
    
    # Use customer_id in the query
    query = f"""
    MATCH (cust:Customer {{id: $customer_id}})
    OPTIONAL MATCH (cust)-[:INVOLVED_IN]->(i:Incident)
    OPTIONAL MATCH (cust)<-[:FILED_BY]-(c:Claim)
    OPTIONAL MATCH (c)<-[:MANAGES]-(cm:ClaimManagement)
    OPTIONAL MATCH (cust)-[:HAS_BANKING_DETAILS]->(b:BankingDetails)
    OPTIONAL MATCH (cust)-[:HAS_DETAILS]->(o:OtherDetails)
    RETURN cust, c, cm, i, b, o
    """
    
    params = {'customer_id': customer_id}
    
    df_raw = fetch_data_from_neo4j(neo4j_conn.driver, query, params)
    
    if df_raw.empty:
        print(f"No data fetched for customer {customer_id}.")
        neo4j_conn.driver.close()
        return
    
    neo4j_data = df_raw.iloc[0].to_dict()
    features_dict = transform_neo4j_data_for_model(neo4j_data)
    
    # Prepare features for the model
    df_features = pd.DataFrame([features_dict]).reindex(columns=PREDICTION_COLUMNS, fill_value=0)
    
    # Convert object columns to categorical for XGBoost
    for col in df_features.select_dtypes(include='object').columns:
        df_features[col] = df_features[col].astype('category')
    
    # Load the model and make predictions
    model = joblib.load(model_path)
    prediction = model.predict(df_features)
    fraud_prob = model.predict_proba(df_features)[:, 1] if hasattr(model, "predict_proba") else None
    
    print(f"Prediction for {customer_id} (0: Not Fraud, 1: Fraud):", prediction[0])
    if fraud_prob is not None:
        print(f"Fraud Probability: {fraud_prob[0]}")
    
    fraud_reason = "Fraud analysis completed. Reasoning not available in this version."
    
    # Store prediction in ClaimManagement node
    store_prediction_in_claim_management(
        neo4j_conn.driver,
        customer_id=customer_id,
        prediction=prediction[0],
        fraud_prob=fraud_prob[0] if fraud_prob is not None else 0,
        fraud_reason=fraud_reason
    )
    
    neo4j_conn.driver.close()