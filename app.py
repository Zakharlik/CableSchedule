import inspect
import sys
from datetime import datetime

from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

#from db_classes import dev_types


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crsched.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class dev_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class container_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class connector_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_of_pins = db.Column(db.Integer, nullable=False)
    is_male = db.Column(db.Boolean, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class containers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cont_type_id = db.Column(db.Integer, db.ForeignKey('connector_types.id'), nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')


def make_table_list():
    """
    Make list of useful columns in dict of tables.
    Some unuseful columns, such as 'id' and 'creation_date', excluded.
    """

    unuseful = ('id', 'creation_date')  # Tuple of unuseful columns
    result = {}
    classes = [(cls_name, cls_obj) for cls_name, cls_obj in inspect.getmembers(sys.modules['db_classes'])
               if inspect.isclass(cls_obj)]  # List of all classes

    for db_class in classes:
        attributes = []
        for cl in inspect.getmembers(db_class[1]):
            if ('attributes' in str(type(cl[1]))) and (cl[0] not in unuseful):
                # 'attributes' - property of SQLAlchemy columns
                attributes.append(cl[0])
        if attributes:  # Need for exclude datetime class
            result[db_class[0]] = attributes
    return result


if __name__ == '__main__':
    tables = make_table_list()
    print(tables)
    app.run(debug=True)
