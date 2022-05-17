import inspect
import sys
from datetime import datetime

from flask import Flask, render_template, request, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

#from db_classes import dev_types
from werkzeug.utils import redirect

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crsched.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class cable_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    connector_a_id = db.Column(db.Integer, db.ForeignKey('connectors.id'), nullable=False)
    connector_b_id = db.Column(db.Integer, db.ForeignKey('connectors.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class cables(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    port_a_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    port_b_id = db.Column(db.Integer, db.ForeignKey('ports.id'), nullable=False)
    cable_type_id = db.Column(db.Integer, db.ForeignKey('cable_types.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class connector_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_of_pins = db.Column(db.Integer, nullable=False)
    is_male = db.Column(db.Boolean, nullable=True)
    connectors = db.relationship('connectors', backref='connector_type', lazy=True)
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


class dev_card_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class dev_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class patch_panels(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    num_of_ports = db.Column(db.Integer, nullable=False)
    container_id = db.Column(db.Integer, db.ForeignKey('containers.id'), nullable=True)
    pp_type_id = db.Column(db.Integer, db.ForeignKey('pp_types.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class port_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class ports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    port_type_id = db.Column(db.Integer, db.ForeignKey('port_types.id'), nullable=False)
    pp_side_id = db.Column(db.Integer, db.ForeignKey('pp_sides.id'), nullable=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class pp_types(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


class pp_sides(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_line_side = db.Column(db.Boolean, nullable=True)
    patch_panel_id = db.Column(db.Integer, db.ForeignKey('patch_panels.id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create')
def create():
    return render_template('create.html')


@app.route('/adm/tables')
def tables():
    """
    Admin page. List of all tables.
    """
#    print(all_tables.keys())
    return render_template('adm/tables.html', all_tables=list(all_tables.keys()))


@app.route('/adm/add/<string:table_name>', methods=['POST', 'GET'])
def add_any_row(table_name):
    """
    Admin page for maintenance any table by hand
    """
    table_rows = globals()[table_name].query.order_by(globals()[table_name].title).all()
    table_columns = all_tables[table_name]
    if request.method == 'POST':
        title = request.form['title']
        if not title:
            return render_template('adm/add/row.html', table_rows=table_rows, table_columns=table_columns,
                                   table_name=table_name, message='Название не может быть пустым')
        is_present = False
        for el in table_rows:
            if title == str(el.title):
                # is_present = True
                return render_template('adm/add/row.html', table_rows=table_rows, table_columns=table_columns,
                                table_name=table_name, message='Такая запись уже есть!')
        if not is_present:
            new_els = {key: request.form[key] for key in table_columns}
            new_row = globals()[table_name](**new_els)
            try:
                db.session.add(new_row)
                db.session.commit()
                return redirect(f'/adm/add/{table_name}')
            except Exception as e:
                return "Ошибка записи в БД: " + str(e)
    return render_template('adm/add/row.html', table_rows=table_rows, table_columns=table_columns, table_name=table_name)


@app.route('/add/port', methods=['POST', 'GET'])
def add_port():
    """
    User page for creating ports
    """
    port_types_list = port_types.query.order_by(port_types.title).all()
    print(type(port_types_list), port_types_list[1].title)
    patch_panels_list = patch_panels.query.order_by(patch_panels.title).all()

    if request.method == 'POST':
        port_type_id = request.form['port_type']
        pp = request.form['pp']
        print(port_type_id, pp)
        title = request.form['title']
        if not title:
            return render_template('add/port.html', port_types_list=port_types_list,
                                   patch_panels_list=patch_panels_list, message='Название не может быть пустым')

        is_present = False
        for el in ports.query.all():
            if title == str(el.title):
                # is_present = True
                return render_template('add/port.html', port_types_list=port_types_list,
                                   patch_panels_list=patch_panels_list, message='Такой порт уже есть!')
        if not is_present:
            # TODO: Add check PP exists
            # TODO: Add choose of PP side
            new_row = ports(title=title, port_type_id=port_type_id)
            try:
                db.session.add(new_row)
                db.session.commit()
                return redirect('/add/port')
            except Exception as e:
                return "Ошибка записи в БД: " + str(e)

    return render_template('add/port.html', port_types_list=port_types_list, patch_panels_list=patch_panels_list)


@app.route('/add/pp', methods=['POST', 'GET'])
def add_pp():
    """
    User page for creating patch panels
    """
    param_dict = {'pp_types_list': pp_types.query.order_by(pp_types.title).all(),
                  'containers_list': containers.query.order_by(containers.title).all(),
                  'port_types_list': port_types.query.order_by(port_types.title).all(),
                  'message':''
                  }
    if request.method == 'POST':
        title = request.form['title']
        pp_type_id = request.form['pp_type']
        container_id = request.form['container']
        num_of_ports = request.form['num_of_ports']
        port_type_id = request.form['port_type']
        if not title:
            param_dict['message'] = 'Название не может быть пустым.'
            return render_template('add/pp.html', **param_dict)
        is_present = False
        for el in patch_panels.query.all():
            if title == str(el.title):
                if patch_panels.query.filter_by(container_id=container_id, title=title):
                    param_dict['message'] = f'Такaя пач панель уже есть в контейнере ' \
                                            f'{containers.query.filter_by(container_id=container_id).first().title}!'
                    return render_template('add/pp.html', **param_dict)
        new_row = patch_panels(title=title, container_id=container_id, num_of_ports=num_of_ports, pp_type_id=pp_type_id)
        try:
            db.session.add(new_row)
            db.session.commit()
        except Exception as e:
            return "Ошибка записи в БД: " + str(e)

        # Создаем стороны пачпанели. Линейную и Аббонентскую.
        # Линейная
        patch_panel_id = patch_panels.query.filter_by(title=title, container_id=container_id,
                                                      num_of_ports=num_of_ports, pp_type_id=pp_type_id).first().id
        add_pp_side(patch_panel_id=patch_panel_id, num_of_ports=patch_panel_id, is_line_side=True, port_type_id=port_type_id)
        add_pp_side(patch_panel_id=patch_panel_id, num_of_ports=patch_panel_id, is_line_side=False, port_type_id=port_type_id)

    return render_template('add/pp.html',  **param_dict)


@app.route('/delete/<string:table_name>/<int:row_id>')
def row_delete(table_name, row_id):
    row = globals()[table_name].query.get_or_404(row_id)
    print(row)
    try:
        db.session.delete(row)
        db.session.commit()
        return redirect(url_for('add_any_row', table_name=table_name))
    except Exception as e:
        return "Ошибка удаления из БД: " + str(e)


def add_pp_side(patch_panel_id, num_of_ports, is_line_side, port_type_id):
    new_row = pp_sides(patch_panel_id=patch_panel_id, is_line_side=is_line_side)
    try:
        db.session.add(new_row)
        db.session.commit()
    except Exception as e:
        return "Ошибка записи в БД: " + str(e)

    pp_side_id = pp_sides.query.filter_by(patch_panel_id=patch_panel_id, is_line_side=is_line_side).first().id
    add_ports(pp_side_id, port_type_id=port_type_id, num_of_ports=num_of_ports)

def add_ports(pp_side_id, port_type_id, num_of_ports):
    for p in range(num_of_ports):
        new_row = ports(title=str(p), port_type_id=port_type_id, pp_side_id=pp_side_id)
        db.session.add(new_row)
    try:
        db.session.commit()
    except Exception as e:
        return "Ошибка записи в БД: " + str(e)



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
