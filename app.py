import inspect
import sys
from datetime import datetime

from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

#from db_classes import dev_types
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crsched.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class connector_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_of_pins = db.Column(db.Integer, nullable=False)
    is_male = db.Column(db.Boolean, nullable=True)
#    connectors = db.relationship('connectors', backref='connector_type', lazy=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class connectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    connector_type_id = db.Column(db.Integer, db.ForeignKey('connector_types.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class container_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class containers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    cont_type_id = db.Column(db.Integer, db.ForeignKey('container_types.id'), nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class dev_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class pp_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/adm/tables')
def tables():
    """
    Admin page. List of all tables.
    """
    print(all_tables.keys())
    return render_template('adm/tables.html', all_tables=list(all_tables.keys()))


@app.route('/add/<string:table_name>', methods=['POST', 'GET'])
def add_any_row(table_name):
    """
    Admin page for maintenance any table by hand
    """
    table_rows = globals()[table_name].query.order_by(globals()[table_name].title).all()
    table_columns = all_tables[table_name]
    if request.method == 'POST':
        title = request.form['title']
        if not title:
            return 'Название не может быть пустым'
        is_present = False
        for el in table_rows:
            if title == str(el.title):
                # is_present = True
                return 'Такая запись уже есть!'
        if not is_present:
            new_els = {key: request.form[key] for key in table_columns}
            new_row = globals()[table_name](**new_els)  # Как сюда запихать список полей?
            try:
                db.session.add(new_row)
                db.session.commit()
                return redirect(f'/add/{table_name}')
            except Exception as e:
                return "Ошибка записи в БД: " + str(e)

#    return render_template(f'add/{table_name}.html', cont_types=cont_types)
    return render_template('add/row.html', table_rows=table_rows, table_columns=table_columns, table_name=table_name)


@app.route('/delete/<string:table_name>/<int:row_id>')
def post_delete(table_name, row_id):
    row = globals()[table_name].query.get_or_404(row_id)
    print(row)
    try:
        db.session.delete(row)
        db.session.commit()
        return redirect(f'/add/{table_name}')
    except Exception as e:
        return "Ошибка удаления из БД: " + str(e)


def make_table_list():
    """
    Make list of useful columns in dict of tables.
    Some unuseful columns, such as 'id' and 'creation_date', excluded.
    """

    unuseful = ('id', 'creation_date')  # Tuple of unuseful columns
    result = {}
    classes = [(cls_name, cls_obj) for cls_name, cls_obj in inspect.getmembers(sys.modules['__main__'])
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
    all_tables = make_table_list()
    app.run(debug=True)
