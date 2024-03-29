from website import create_app
from flask import Flask, request
import bcrypt
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)

app.config['JWT_SECRET_KEY'] = 'secret-secret'  
jwt = JWTManager(app)

@app.route('/register', methods=['POST'])
def register():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        
        if not email:
            return 'Missing email', 400
        if not password:
            return 'Missing password', 400
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        user = User(email=email, hash=hashed)
        db.session.add(user)
        db.session.commit()

        access_token = create_access_token(identity={"email": email})
        return {"access_token": access_token}, 200
    except IntegrityError:
        
        db.session.rollback()
        return 'User Already Exists', 400
    except AttributeError:
        return 'Provide an Email and Password in JSON format in the request body', 400


@app.route('/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        
        if not email:
            return 'Missing email', 400
        if not password:
            return 'Missing password', 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return 'User Not Found!', 404
        

        if bcrypt.checkpw(password.encode('utf-8'), user.hash):
            access_token = create_access_token(identity={"email": email})
            return {"access_token": access_token,'expiration': str(datetime.utcnow() + timedelta(minutes=5))}, 200
        else:
            return 'Invalid Login Info!', 400
    except AttributeError:
        return 'Provide an Email and Password in JSON format in the request body', 400

@app.route('/test', methods=['GET'])
@jwt_required
def test():
    user = get_jwt_identity()
    email = user['email']
    return f'Welcome to the protected route {email}!', 200

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
