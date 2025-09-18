
# AI-Powered Fraud Detection and Document Verification

This innovative insurance platform transforms fraud detection for verified document retrieval using advanced AI-powered mechanisms. By reducing the reliance on manual verification, the system enhances efficiency while delivering real-time fraud analysis through multiple layers of security checks.

This project was created for the Hackathon **Hack-AI-Thon** conducted by **SBI**.

## Demo Video

https://github.com/user-attachments/assets/fe1478f6-ee3b-4267-9498-aa783a4aa61f

## Architecture

<img width="1245" height="701" alt="image" src="https://github.com/user-attachments/assets/5d6c436a-933e-4938-b483-9f1d24cec44c" />

## Technology Stack

This project leverages the following technologies:
- **TypeScript** 
- **Flask** 
- **Neo4J**
- **XGBoost**
- **CNN**
- **Mistral OCR**
- **Isolation Forest**

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

## Contributors

- [Parth Petkar](https://github.com/parthpetkar)
- [Parth Kalani](https://github.com/parth1899)
- [Aditya Deore](https://github.com/adideo03)
- [Arya Alurkar](https://github.com/arya911)
