
# Hack-AI-Thon-Project

## About The Project

This innovative insurance platform transforms fraud detection for verified document retrieval using advanced AI-powered mechanisms. By reducing the reliance on manual verification, the system enhances efficiency while delivering real-time fraud analysis through multiple layers of security checks.

This project was created for the Hackathon **Hack-AI-Thon** conducted by **SBI**.

## Demo Video

<video width="640" height="360" controls>
  <source src="[https://drive.google.com/uc?export=download&id=YOUR_FILE_ID](https://drive.google.com/uc?export=download&id=1T1TcV0jpimszssDMS5zSuSDQGqfihxVI" type="video/quicktime">
  Your browser does not support the video tag.
</video>


## Technology Stack

This project leverages the following technologies:
- **TypeScript** (77.7%)
- **Python** (20.9%)
- **Other** (1.4%)

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

## Installation & Setup

Follow these steps to set up the project:

1. **Clone the repository:**
   ```sh
   git clone https://github.com/parthpetkar/Hack-AI-Thon-Project.git
   ```
2. **Navigate to the project directory:**
   ```sh
   cd Hack-AI-Thon-Project
   ```
3. **Install dependencies:**
   ```sh
   npm install
   ```

## Usage

(Explain how to use your project.)

## Frontend Setup

The frontend uses React + TypeScript + Vite. This setup provides a minimal configuration to get React working with Vite, HMR, and some ESLint rules.

For more information, refer to the [Frontend README](https://github.com/parthpetkar/Hack-AI-Thon-Project/blob/ceccbf25d606490d50b1d2bcc8276fb779015ed4/Frontend/README.md).

## Contributors

We would like to thank the following contributors for their hard work:

- [parthpetkar](https://github.com/parthpetkar) - 12 contributions
- [parth1899](https://github.com/parth1899) - 9 contributions
- [adideo03](https://github.com/adideo03) - 8 contributions
- [aryaalukar](https://github.com/arya911) - 7 contributions

## Contributing

We welcome contributions from the community. Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add a feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Feel free to customize the sections as per your project's specifics.
