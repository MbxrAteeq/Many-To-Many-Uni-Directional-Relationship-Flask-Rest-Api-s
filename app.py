from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///manytomany.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Associate Table
subs = db.Table('subs',
    db.Column('user_id',db.Integer, db.ForeignKey('user.user_id')),
    db.Column('channel_id',db.Integer, db.ForeignKey('channel.channel_id')),
    )


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    subscription = db.relationship('Channel', secondary=subs, backref=db.backref('subscribers', lazy = 'dynamic'))


class Channel(db.Model):
    channel_id = db.Column(db.Integer, primary_key=True)
    channel_name = db.Column(db.String(20))


# Add New User
@app.route('/user', methods=['POST'])
def add_user():

    data = request.get_json()
    new_user = User(name = data['name'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message':'New User Created'}), 200


# Add new Channel
@app.route('/channel', methods=['POST'])
def add_channel():

    data = request.get_json()
    new_channel = Channel(channel_name = data['channel_name'])
    
    user = db.session.query(User).filter_by(user_id="1").first()

    db.session.add(new_channel)
    new_channel.subscribers.append(user)
    
    db.session.commit()
    return jsonify({'message':'New Channel Created'}), 200


#Get One Channel
@app.route("/channel/<id>", methods=['GET'])
def get_one_channel(id):
    data = Channel.query.filter_by(channel_id=id).first()

    if not data:
        return jsonify({'message':'No Data found'}), 404

    channel_data = {}
    channel_data['id'] = data.channel_id
    channel_data['name'] = data.channel_name
    channel_data['user'] = get_one_user(data)
    return jsonify({'data':channel_data})


# Get All Channel
@app.route('/channel', methods=['GET'])
def get_all_channel():

    alldata = Channel.query.all()

    if not alldata:
        return jsonify({'message':'No Data found'}), 404

    output = []
    for data in alldata:
        channel = {}
        channel['id'] = data.channel_id
        channel['name'] = data.channel_name
        channel['User'] = get_one_user(data)
        output.append(channel)

    return jsonify({'data':output}), 200



def get_one_user(data):

    if not data:
        return None
    try:
        user = data.subscribers[0]
    except:
        return None

    user_data = {}
    user_data['User id'] = user.user_id
    user_data['User name'] = user.name

    return user_data


if __name__ == '__main__':

    app.run(debug=True)

