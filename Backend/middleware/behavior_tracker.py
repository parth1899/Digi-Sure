# middleware/behavior_tracker.py
from flask import request, g, session, current_app
import time
import threading
import uuid
import ipaddress
from datetime import datetime
import json
import os
from functools import wraps
from collections import defaultdict

class UserBehaviorTracker:
    """
    Middleware for capturing user behavior metrics for anomaly detection
    """
    def __init__(self, app=None):
        self.app = app
        self.session_data = defaultdict(dict)
        self.session_apis = defaultdict(set)
        self.session_timestamps = defaultdict(list)
        self.session_start_times = {}
        self.session_ips = defaultdict(set)
        self.active_users = defaultdict(set)
        
        # Set up logs directory
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.before_request(self.start_timer)
        app.after_request(self.log_request)
        
        # Start cleanup thread for expired sessions
        cleanup_thread = threading.Thread(target=self.cleanup_expired_sessions)
        cleanup_thread.daemon = True
        cleanup_thread.start()
    
    def start_timer(self):
        """Start timer for request duration tracking"""
        g.start_time = time.time()
        
        # If no session ID exists in headers, this is a new session
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            # Use token as session identifier
            g.session_id = token
            
            # Record session start time if it's new
            if token not in self.session_start_times:
                self.session_start_times[token] = time.time()
                
            # Record user IP
            user_ip = request.remote_addr
            self.session_ips[token].add(user_ip)
            
            # Extract user email from request context if available
            user_email = None
            if hasattr(g, 'current_user_email'):
                user_email = g.current_user_email
            elif request.endpoint:
                view_func = current_app.view_functions.get(request.endpoint)
                if view_func and hasattr(view_func, '__wrapped__'):
                    # The function might be decorated, try to extract user from token
                    from utils.auth import get_user_from_token
                    user_email = get_user_from_token(token)
            
            if user_email:
                self.active_users[token].add(user_email)
        else:
            # For requests without auth token, generate a temporary session ID
            g.session_id = f"temp-{uuid.uuid4()}"
            self.session_start_times[g.session_id] = time.time()
    
    def log_request(self, response):
        """Log API request details after processing"""
        if not hasattr(g, 'start_time'):
            return response
        
        # Calculate request duration
        duration = time.time() - g.start_time
        
        session_id = getattr(g, 'session_id', None)
        if not session_id:
            return response
        
        # Store API endpoint
        endpoint = request.endpoint or 'unknown'
        path = request.path
        self.session_apis[session_id].add(path)
        
        # Store request timestamp
        self.session_timestamps[session_id].append(time.time())
        
        # If we have enough data, calculate metrics and log them
        if len(self.session_timestamps[session_id]) >= 5:
            self.calculate_and_log_metrics(session_id)
        
        return response
    
    def calculate_and_log_metrics(self, session_id):
        """Calculate behavior metrics and save to log file"""
        timestamps = self.session_timestamps[session_id]
        apis = self.session_apis[session_id]
        
        # Skip if not enough data points
        if len(timestamps) < 2:
            return
        
        # Calculate metrics
        seq_length = len(timestamps)
        unique_apis = len(apis)
        
        # Calculate time between API calls
        time_diffs = []
        for i in range(1, len(timestamps)):
            time_diffs.append(timestamps[i] - timestamps[i-1])
        
        inter_api_duration = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        
        # Calculate session duration in minutes
        session_duration = (timestamps[-1] - self.session_start_times[session_id]) / 60
        
        # API access uniqueness
        api_uniqueness = unique_apis / seq_length if seq_length > 0 else 0
        
        # User count
        num_users = len(self.active_users[session_id]) if session_id in self.active_users else 1
        
        # Determine IP type (simplified)
        ip_type_default = 1
        ip_type_google_bot = 0
        ip_type_private_ip = 0
        
        if session_id in self.session_ips and self.session_ips[session_id]:
            ip = list(self.session_ips[session_id])[0]
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    ip_type_default = 0
                    ip_type_private_ip = 1
                # Add Google bot detection if needed
            except:
                pass
        
        # Source F is a placeholder, would need real logic based on your app
        source_f = 0
        
        # Behavior encoded - how common this pattern is
        # This would normally come from historical data analysis
        # For now using a placeholder value based on reasonable ranges
        behavior_encoded = 0.7
        if inter_api_duration > 10 or seq_length > 100 or unique_apis > 15:
            behavior_encoded = 0.3
        if num_users > 1 or session_duration > 1000:
            behavior_encoded = 0.1
            
        # Create sample for anomaly detection
        sample = [
            inter_api_duration,  # inter_api_access_duration
            api_uniqueness,      # api_access_uniqueness
            seq_length,          # sequence_length
            session_duration,    # vsession_duration
            1,                   # num_sessions (placeholder, would need multi-session tracking)
            num_users,           # num_users
            unique_apis,         # num_unique_apis
            ip_type_default, ip_type_google_bot, ip_type_private_ip,  # ip_type dummies
            source_f,            # source_F
            behavior_encoded     # behavior_encoded
        ]
        
        # Log to file
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = os.path.join(self.logs_dir, f'session_{timestamp}.json')
        
        log_data = {
            'session_id': session_id,
            'timestamp': timestamp,
            'metrics': {
                'inter_api_access_duration': inter_api_duration,
                'api_access_uniqueness': api_uniqueness,
                'sequence_length': seq_length,
                'vsession_duration': session_duration,
                'num_sessions': 1,
                'num_users': num_users,
                'num_unique_apis': unique_apis,
                'ip_type_default': ip_type_default,
                'ip_type_google_bot': ip_type_google_bot,
                'ip_type_private_ip': ip_type_private_ip,
                'source_F': source_f,
                'behavior_encoded': behavior_encoded
            },
            'sample': sample
        }
        
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
            
        # Clear timestamps to avoid duplicate logging
        self.session_timestamps[session_id] = []
    
    def cleanup_expired_sessions(self, check_interval=300):
        """Clean up expired sessions every 5 minutes"""
        while True:
            time.sleep(check_interval)
            current_time = time.time()
            session_ids = list(self.session_start_times.keys())
            
            for session_id in session_ids:
                # If session is older than 1 hour, clean it up
                if current_time - self.session_start_times[session_id] > 3600:
                    # Calculate final metrics before removing
                    if session_id in self.session_timestamps and self.session_timestamps[session_id]:
                        self.calculate_and_log_metrics(session_id)
                    
                    # Clean up session data
                    if session_id in self.session_data:
                        del self.session_data[session_id]
                    if session_id in self.session_apis:
                        del self.session_apis[session_id]
                    if session_id in self.session_timestamps:
                        del self.session_timestamps[session_id]
                    if session_id in self.session_start_times:
                        del self.session_start_times[session_id]
                    if session_id in self.session_ips:
                        del self.session_ips[session_id]
                    if session_id in self.active_users:
                        del self.active_users[session_id]

# Enhanced token_required decorator that also sets the current user for the behavior tracker
def token_required_with_tracking(f):
    """Decorator that both authenticates and tracks user for behavior monitoring"""
    from utils.auth import token_required
    
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get the original decorator
        original_decorator = token_required(f)
        
        # Extract token before calling the original decorator
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Try to extract user email
            from utils.auth import get_user_from_token
            current_user_email = get_user_from_token(token)
            if current_user_email:
                g.current_user_email = current_user_email
        
        # Call the original decorator
        return original_decorator(*args, **kwargs)
    
    return decorated