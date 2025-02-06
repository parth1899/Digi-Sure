# Hack-AI-Thon-Project

This project was created for the Hackathon **Hack-AI-Thon** conducted by **SBI**.

## Database Setup

To set up the **Neo4j** database, run the following Cypher queries:

```cypher
// 1. Create a unique constraint on the email field
CREATE CONSTRAINT user_email IF NOT EXISTS
ON (u:User) ASSERT u.email IS UNIQUE;

// 2. Create indexes for better query performance
CREATE INDEX user_name IF NOT EXISTS
FOR (u:User) ON (u.name);

CREATE INDEX user_surname IF NOT EXISTS
FOR (u:User) ON (u.surname);
```

### Project Overview

(Add a brief description of what your project does and its key features.)

### Installation & Setup

(Include instructions for setting up the project, including dependencies.)

### Usage

(Explain how to use your project.)
