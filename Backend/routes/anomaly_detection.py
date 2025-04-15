from flask import Blueprint, jsonify, request, current_app
import joblib
import pandas as pd
import numpy as np
import pickle
import os
import json
from datetime import datetime, timedelta

log_bp = Blueprint('log', __name__)
# Load artifacts
# model = joblib.load('routes/iso_forest_model.pkl')
# artifacts = joblib.load('routes/preprocessing_artifacts.pkl')

try:
    # with open('routes/iso_forest_model.pkl', 'rb') as f:
    #     iso_forest = pickle.load(f)
    # with open('routes/preprocessing_artifacts.pkl', 'rb') as f:
    #     scaler = pickle.load(f)
    iso_forest = joblib.load('routes/iso_forest_model.pkl')
    scaler = joblib.load('routes/preprocessing_artifacts.pkl')
except Exception as e:
    print(f"Warning: Could not load anomaly detection model: {str(e)}")
    iso_forest = None
    scaler = None

def predict_anomaly(sample, model, scaler):
    """Predict if a behavior sample is anomalous"""
    if model is None or scaler is None:
        return "Model not loaded", 0.5
    
    # Scale the sample
    sample_scaled = scaler.transform([sample])
    
    # Get anomaly score (-1 for anomalies, 1 for normal)
    score = model.decision_function(sample_scaled)[0]
    
    # Convert to a probability-like score (0 to 1)
    # Lower score = more anomalous
    normalized_score = (score + 0.5) / 1.5
    
    # Classify as anomaly if below threshold
    is_anomaly = normalized_score < 0.5
    
    return "Anomaly" if is_anomaly else "Normal", normalized_score


@log_bp.route('/behavior', methods=['GET'])
def get_behavior_logs():
    """Get recent behavior logs"""
    logs_dir = os.path.join(current_app.root_path, 'logs')
    if not os.path.exists(logs_dir):
        return jsonify({'message': 'No logs found'}), 404
    
    # Get log files and sort by most recent
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
    log_files.sort(reverse=True)
    
    logs = []
    for file in log_files[:50]:  # Get the 50 most recent logs
        try:
            with open(os.path.join(logs_dir, file), 'r') as f:
                log_data = json.load(f)
                
                # Add prediction if model is loaded
                if iso_forest and scaler:
                    prediction, score = predict_anomaly(log_data['sample'], iso_forest, scaler)
                    log_data['prediction'] = prediction
                    log_data['anomaly_score'] = score
                
                logs.append(log_data)
        except Exception as e:
            print(f"Error reading log file {file}: {str(e)}")
    
    return jsonify({'logs': logs})

@log_bp.route('/anomalies', methods=['GET'])
def get_anomalies():
    """Get detected anomalies"""
    logs_dir = os.path.join(current_app.root_path, 'logs')
    if not os.path.exists(logs_dir):
        return jsonify({'message': 'No logs found'}), 404
    
    # Get all log files
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
    
    anomalies = []
    for file in log_files:
        try:
            with open(os.path.join(logs_dir, file), 'r') as f:
                log_data = json.load(f)
                
                # Check if it's an anomaly
                if iso_forest and scaler:
                    prediction, score = predict_anomaly(log_data['sample'], iso_forest, scaler)
                    if prediction == "Anomaly":
                        log_data['prediction'] = prediction
                        log_data['anomaly_score'] = score
                        anomalies.append(log_data)
        except Exception as e:
            print(f"Error reading log file {file}: {str(e)}")
    
    # Sort by most anomalous (lowest score)
    anomalies.sort(key=lambda x: x.get('anomaly_score', 1.0))
    
    return jsonify({'anomalies': anomalies})

@log_bp.route('/stats', methods=['GET'])
def get_behavior_stats():
    """Get behavior statistics"""
    logs_dir = os.path.join(current_app.root_path, 'logs')
    if not os.path.exists(logs_dir):
        return jsonify({'message': 'No logs found'}), 404
    
    # Get all log files from the past week
    log_files = [f for f in os.listdir(logs_dir) if f.endswith('.json')]
    one_week_ago = datetime.now() - timedelta(days=7)
    
    # Extract metrics for analysis
    metrics = {
        'inter_api_access_duration': [],
        'api_access_uniqueness': [],
        'sequence_length': [],
        'vsession_duration': [],
        'num_users': [],
        'num_unique_apis': []
    }
    
    anomaly_count = 0
    total_count = 0
    
    for file in log_files:
        try:
            with open(os.path.join(logs_dir, file), 'r') as f:
                log_data = json.load(f)
                
                # Skip files older than a week
                log_time = datetime.strptime(log_data['timestamp'], "%Y%m%d-%H%M%S")
                if log_time < one_week_ago:
                    continue
                    
                total_count += 1
                log_metrics = log_data['metrics']
                
                # Add metrics for stat calculation
                for key in metrics.keys():
                    if key in log_metrics:
                        metrics[key].append(log_metrics[key])
                
                # Check if anomalous
                if iso_forest and scaler:
                    prediction, _ = predict_anomaly(log_data['sample'], iso_forest, scaler)
                    if prediction == "Anomaly":
                        anomaly_count += 1
        except Exception as e:
            print(f"Error reading log file {file}: {str(e)}")
    
    # Calculate statistics
    stats = {}
    for key, values in metrics.items():
        if values:
            stats[key] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'p95': np.percentile(values, 95) if len(values) > 5 else max(values)
            }
    
    # Add anomaly rate
    stats['anomaly_rate'] = anomaly_count / total_count if total_count > 0 else 0
    stats['total_sessions'] = total_count
    stats['anomaly_count'] = anomaly_count
    
    return jsonify({'stats': stats})


@log_bp.route('/detect-anomaly', methods=['POST'])
def detect_anomaly():
    try:
        # 1. Get data from request
        data = request.json
        
        # 2. Create DataFrame
        input_df = pd.DataFrame([data])
        
        # 3. Preprocessing
        # Handle behavior
        input_df['behavior'] = input_df['behavior'].apply(
            lambda x: x if x in artifacts['common_behaviors'] else 'Other'
        )
        input_df['behavior_encoded'] = input_df['behavior'].map(
            artifacts['freq_map']
        ).fillna(artifacts['freq_map']['Other'])
        
        # Handle behavior_type
        input_df['behavior_type'] = input_df['behavior_type'].map(
            artifacts['behavior_type_map']
        )
        
        # Handle numerical features scaling
        num_features = ['inter_api_access_duration(sec)', 'sequence_length(count)',
                       'vsession_duration(min)', 'num_sessions', 'num_users',
                       'num_unique_apis']
        input_df[num_features] = artifacts['scaler'].transform(input_df[num_features])
        
        # 4. Create final feature set
        final_features = pd.DataFrame(columns=artifacts['feature_columns'])
        for col in final_features.columns:
            if col in input_df.columns:
                final_features[col] = input_df[col]
            else:
                final_features[col] = 0  # For one-hot encoded columns not present
        
        # 5. Predict anomaly score
        score = model.decision_function(final_features.values)[0]
        is_anomaly = score < -0.43  # Use your calculated threshold
        
        return jsonify({
            'anomaly': bool(is_anomaly),
            'score': float(score),
            'threshold': -0.43
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400