from flask import request, g, current_app
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
    write_lock = threading.Lock()  # Lock for thread-safe logging

    def __init__(self, app=None):
        self.app = app
        self.session_data = defaultdict(dict)
        self.session_apis = defaultdict(set)
        self.session_timestamps = defaultdict(list)
        self.session_start_times = {}
        self.session_ips = defaultdict(set)
        self.active_users = defaultdict(set)

        # Set up logs directory and file
        self.logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        self.log_file = os.path.join(self.logs_dir, 'behavior_logs.jsonl')

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        app.before_request(self.start_timer)
        app.after_request(self.log_request)

        # Start cleanup thread
        cleanup_thread = threading.Thread(target=self.cleanup_expired_sessions)
        cleanup_thread.daemon = True
        cleanup_thread.start()

    def start_timer(self):
        """Start timing the request"""
        g.start_time = time.time()

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            g.session_id = token

            if token not in self.session_start_times:
                self.session_start_times[token] = time.time()

            user_ip = request.remote_addr
            self.session_ips[token].add(user_ip)

            user_email = getattr(g, 'current_user_email', None)
            if not user_email and request.endpoint:
                view_func = current_app.view_functions.get(request.endpoint)
                if view_func and hasattr(view_func, '__wrapped__'):
                    from utils.auth import get_user_from_token
                    user_email = get_user_from_token(token)

            if user_email:
                self.active_users[token].add(user_email)
        else:
            g.session_id = f"temp-{uuid.uuid4()}"
            self.session_start_times[g.session_id] = time.time()

    def log_request(self, response):
        """Log request details"""
        if not hasattr(g, 'start_time'):
            return response

        duration = time.time() - g.start_time
        session_id = getattr(g, 'session_id', None)
        if not session_id:
            return response

        path = request.path
        self.session_apis[session_id].add(path)
        self.session_timestamps[session_id].append(time.time())

        if len(self.session_timestamps[session_id]) >= 5:
            self.calculate_and_log_metrics(session_id)

        return response

    def calculate_and_log_metrics(self, session_id):
        """Calculate and log behavior metrics"""
        timestamps = self.session_timestamps[session_id]
        apis = self.session_apis[session_id]

        if len(timestamps) < 2:
            return

        seq_length = len(timestamps)
        unique_apis = len(apis)

        time_diffs = [timestamps[i] - timestamps[i-1] for i in range(1, len(timestamps))]
        inter_api_duration = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        session_duration = (timestamps[-1] - self.session_start_times[session_id]) / 60
        api_uniqueness = unique_apis / seq_length if seq_length else 0
        num_users = len(self.active_users[session_id]) if session_id in self.active_users else 1

        ip_type_default = 1
        ip_type_google_bot = 0
        ip_type_private_ip = 0

        if self.session_ips[session_id]:
            ip = list(self.session_ips[session_id])[0]
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.is_private:
                    ip_type_default = 0
                    ip_type_private_ip = 1
            except:
                pass

        source_f = 0

        behavior_encoded = 0.7
        if inter_api_duration > 10 or seq_length > 100 or unique_apis > 15:
            behavior_encoded = 0.3
        if num_users > 1 or session_duration > 1000:
            behavior_encoded = 0.1

        sample = [
            inter_api_duration,
            api_uniqueness,
            seq_length,
            session_duration,
            1,
            num_users,
            unique_apis,
            ip_type_default, ip_type_google_bot, ip_type_private_ip,
            source_f,
            behavior_encoded
        ]

        log_data = {
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
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

        # Thread-safe append to file
        with self.write_lock:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_data) + '\n')

        self.session_timestamps[session_id] = []

    def cleanup_expired_sessions(self, check_interval=300):
        """Clean up expired sessions periodically"""
        while True:
            time.sleep(check_interval)
            current_time = time.time()
            for session_id in list(self.session_start_times.keys()):
                if current_time - self.session_start_times[session_id] > 3600:
                    if self.session_timestamps[session_id]:
                        self.calculate_and_log_metrics(session_id)

                    for d in [
                        self.session_data,
                        self.session_apis,
                        self.session_timestamps,
                        self.session_start_times,
                        self.session_ips,
                        self.active_users
                    ]:
                        d.pop(session_id, None)
