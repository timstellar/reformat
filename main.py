from flask import Flask
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api()

courses = {}

parser = reqparse.RequestParser()
parser.add_argument("name", type=str, required=True, location='form')


class Main(Resource):
    def post(self, text):
        courses[text] = parser.parse_args()
        return courses


api.add_resource(Main, "/api/courses/<string:text>")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="127.0.0.1")
