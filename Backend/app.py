# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS  # To handle CORS for React integration
from neo4j import GraphDatabase  # Neo4j Python driver
import os
from dotenv import load_dotenv  # To load environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Neo4j Aura connection setup
NEO4J_URI = os.getenv("NEO4J_URL")  # Bolt URI from Aura dashboard
NEO4J_USER = os.getenv("NEO4J_USER")  # Username from Aura dashboard
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")  # Password from Aura dashboard

# Initialize the Neo4j driver
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Test route to check if the app is running
@app.route('/')
def home():
    return "Flask app is running and connected to Neo4j Aura!"

# Example API route to fetch data from Neo4j Aura
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 10")
            nodes = [record["n"] for record in result]
        return jsonify(nodes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Example API route to add data to Neo4j Aura
@app.route('/api/data', methods=['POST'])
def add_data():
    try:
        data = request.json
        name = data.get("name")
        with driver.session() as session:
            session.run("CREATE (n:Node {name: $name})", name=name)
        return jsonify({"message": "Node created successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)