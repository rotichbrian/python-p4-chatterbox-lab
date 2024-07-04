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

@app.route('/messages', methods = ['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        messages_serialize = [message.to_dict() for message in messages]
        return jsonify(messages_serialize), 200
    elif request.method == 'POST':
        message_data = request.get_json()
        new_message = Message(
            body = message_data.get('body'),
            username = message_data.get('username')
        )
        db.session.add(new_message)
        db.session.commit()
        response_dict = new_message.to_dict()
        return jsonify(response_dict), 201

@app.route('/messages/<int:id>', methods = ['PATCH', 'DELETE'])
def messages_by_id(id):
    message = Message.query.filter_by(id = id).first()
    if not message:
        return jsonify({'error': 'Message not found'}), 404

    if request.method == 'PATCH':
        new_message = request.get_json()
        for attr in new_message:
            setattr(message, attr, new_message[attr])
            db.session.add(message)
            db.session.commit()
            response = make_response(jsonify(message.to_dict()), 202)
            return response
    elif request.method == 'DELETE':
          db.session.delete(message)
          db.session.commit()
          return make_response(jsonify({'message': 'Message deleted'}), 204)

if __name__ == '__main__':
    app.run(port=5555)
