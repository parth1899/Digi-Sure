from werkzeug.security import generate_password_hash, check_password_hash
from database.connection import Neo4jConnection

class User:
    def __init__(self, email, name, surname, password_hash):
        self.email = email
        self.name = name
        self.surname = surname
        self.password_hash = password_hash

    @staticmethod
    def create_user(email, name, surname, password):
        db = Neo4jConnection()
        with db.get_session() as session:
            # Check if user already exists
            result = session.run(
                "MATCH (u:User {email: $email}) RETURN u",
                email=email
            )
            if result.single():
                return None

            password_hash = generate_password_hash(password)
            session.run(
                """
                CREATE (u:User {
                    email: $email,
                    name: $name,
                    surname: $surname,
                    password_hash: $password_hash
                })
                """,
                email=email,
                name=name,
                surname=surname,
                password_hash=password_hash
            )
            return User(email, name, surname, password_hash)

    @staticmethod
    def get_user_by_email(email):
        db = Neo4jConnection()
        with db.get_session() as session:
            result = session.run(
                "MATCH (u:User {email: $email}) RETURN u",
                email=email
            )
            user = result.single()
            if user:
                user = user['u']
                return User(
                    user['email'],
                    user['name'],
                    user['surname'],
                    user['password_hash']
                )
            return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)