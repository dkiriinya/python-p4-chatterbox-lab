# app.py
from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET','POST'])
def messages():
    if request.method == 'GET':
        messages = []
        for message in Message.query.all():
           message_dict = message.to_dict()
           messages.append(message_dict)
        
        response = make_response(
            jsonify(messages),
            200
        )
        
        return response
    
    elif request.method == 'POST':
        body = request.json.get("body")
        username = request.json.get("username")
        
        if not body or not username:
            return jsonify({"error": "Body and Username are required"}), 400

        new_message = Message(
            body=body,
            username=username,
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        message_dict = new_message.to_dict()
        
        response = make_response(
            jsonify(message_dict),
            201
        )
        
        return response

@app.route('/messages/<int:id>', methods=['GET','DELETE','PATCH'])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()
    
    if not message:
         return jsonify({"error": "Message not found"}), 404
     
    if request.method == 'GET':
        return jsonify(message.to_dict()), 200
    
    elif request.method == 'PATCH':
        data = request.json
        if 'body' in data:
            message.body = data['body']
        if 'username' in data:
            message.username = data['username']
        
        db.session.commit()
        
        return jsonify(message.to_dict()), 200
    
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()

        response_body = {
            "delete_successful": True,
            "message": "Message deleted."
        }

        response = make_response(
            jsonify(response_body),
            200
        )

        return response
     

if __name__ == '__main__':
    app.run(port=5555)
