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
model = joblib.load('routes/models/iso_forest_model.pkl')
artifacts = joblib.load('routes/models/preprocessing_artifacts.pkl')

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