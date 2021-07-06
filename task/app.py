from flask import Flask, Response
from flask_restful import Api, Resource, inputs, reqparse, fields, marshal_with
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_
import datetime

import sys

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///webCalendar.db'
app.config["SQLALCHEMY_ECHO"] = True
# write your code here
api = Api(app)

parser = reqparse.RequestParser()
parser2 = reqparse.RequestParser()

parser.add_argument(
    'event',
    type=str,
    help="The event name is required!",
    required=True
)
parser.add_argument(
    'date',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=True
)
parser2.add_argument(
    'start_time',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=False
)
parser2.add_argument(
    'end_time',
    type=inputs.date,
    help="The event date with the correct format is required! The correct format is YYYY-MM-DD!",
    required=False
)


class EventData(db.Model):
    __tablename__ = 'Events'
    id = db.Column(db.INTEGER, primary_key=True)
    event = db.Column(db.VARCHAR(100), nullable=False)
    date = db.Column(db.DATE, nullable=False)


event_fields = {
    'id':   fields.Integer,
    'event':    fields.String,
    'date':    fields.DateTime(dt_format='iso8601')
}


class EventByID(Resource):

    @marshal_with(event_fields)
    def get(self, event_id):
        event = EventData.query.filter(EventData.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        return event

    def delete(self, event_id):
        event = EventData.query.filter(EventData.id == event_id).first()
        if event is None:
            abort(404, "The event doesn't exist!")
        else:
            db.session.delete(event)
            db.session.commit()
            return {"message": "The event has been deleted!"}


class Today(Resource):
    @marshal_with(event_fields)
    def get(self):
        event = EventData()

        return event.query.filter(EventData.date == datetime.date.today()).all()


class Event(Resource):
    def post(self):
        args = parser.parse_args()
        event = EventData(event=args.event, date=args.date)
        db.session.add(event)
        db.session.commit()
        return {"message": "The event has been added!", "event" : args.event, "date": args.date.strftime("%Y-%m-%d")}
        #return Response.status

    @marshal_with(event_fields)
    def get(self):
        args = parser2.parse_args()
        event = EventData()
        print(args.start_time)
        print(args.end_time)
        if args.start_time is None or args.end_time is None:
            return event.query.all()
        else:
            return event.query.filter(EventData.date >= args.start_time , EventData.date <= args.end_time).all()

api.add_resource(Event, '/event')
api.add_resource(Today, '/event/today')
api.add_resource(EventByID, '/event/<int:event_id>')

db.create_all()
# do not change the way you run the program
if __name__ == '__main__':
    if len(sys.argv) <= 1:
        app.run()
    else:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
