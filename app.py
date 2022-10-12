import re

from flask import render_template, request, url_for, flash, redirect, jsonify, session
from sqlalchemy import desc

from forms import Form
from models import State, Student, City, Country, app, db, Users


@app.route('/get_state_list/<country_id>')
def get_state_list(country_id):
    result = State.query.filter_by(country_id=country_id).all()
    state_list = []
    for state in result:
        state_obj = {
            'id': state.id,
            'name': state.name
        }
        state_list.append(state_obj)
    return jsonify({'state_list': state_list})


@app.route('/get_city_list/<state_id>')
def get_city_list(state_id):
    city_data = City.query.filter_by(state_id=state_id).all()
    city_list = []
    for city in city_data:
        city_obj = {
            'id': city.id,
            'name': city.name
        }
        city_list.append(city_obj)
    return jsonify({'city_list': city_list})


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        if username == 'admin' and password == 'admin':
            session['username'] = username
            flash(f'Logged in as {username}', category='success')
            return redirect(url_for('index'))
        else:
            flash('Username or Password does not match', category='error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        add_user = Users(username=request.form["username"], password=request.form["password"],
                         confirm_password=request.form["confirm_password"])

        exists = db.session.query(db.exists().where(
            Users.username == request.form["username"])).scalar()
        if exists:
            flash("User with same username already exists", category='error')
            return render_template('register.html')
        if request.form["username"] != request.form["confirm_password"]:
            flash("Password does not match", category='error')
            return render_template('register.html')
        else:
            db.session.add(add_user)
            db.session.commit()
            flash('User Created', category='success')
            return redirect(url_for('login'))
    return render_template('register.html')


# Index
@app.route('/index')
def index():
    students = Student.query.order_by(desc(Student.id))
    return render_template('show_student_list.html', students=students)


# Show all students records
@app.route('/show_all_students')
def show_all_students():
    students = Student.query.order_by(desc(Student.id))

    return render_template('show_student_list.html', students=students)


# add student
@app.route('/add_students', methods=['GET', 'POST'])
def add_students():
    form = Form()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]

    if request.method == "POST":
        city = City.query.filter_by(id=form.city.data).first()
        country = Country.query.filter_by(id=form.country.data).first()
        state = State.query.filter_by(id=form.state.data).first()

        message = ""

        if len(request.form['name']) < 2:
            message = '''Minimum name length should be 2 
                        and cannot contain numbers 
                        or any special characters'''
            flash(message, category='error')

        if not request.form['pin'].isnumeric() and len(request.form['pin']) < 6:
            message = "Pin should be in numbers (Max./Min. length: 6)/ No special characters/Alphabets allowed"
            flash(message, category='error')

        if not request.form['roll_no'].isnumeric():
            message = "Roll No. should be in numbers (Max./Min. length: 6/ No special characters/Alphabets allowed)"
            flash(message, category='error')

        email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(email_reg, request.form['email']):
            pass
        else:
            message = "Enter a Valid Email"
            flash(message, category='error')
        if message:
            return redirect(url_for('add_students'))
        else:
            student = Student(name=request.form['name'], addr=request.form['addr'], country_id=country.id,
                              state_id=state.id, city_id=city.id, pin=request.form['pin'],
                              standard=request.form["standard"],
                              roll_no=request.form['roll_no'],
                              email=request.form['email'])

        exists = db.session.query(db.exists().where(
            Student.email == request.form["email"] or Student.roll_no == request.form["roll_no"])).scalar()
        if exists:

            flash("User with same Email or Roll No. already exists", category='error')
            return render_template('add_student.html', form=form)
        else:
            db.session.add(student)
            db.session.commit()
            flash("Record added!", category='success')
            return redirect(url_for('show_all_students'))
    return render_template('add_student.html', form=form)


# delete student record
@app.route('/redirect_to_del_record/<int:student_id>')
def redirect_to_del_record(student_id):
    user_to_del = Student.query.filter_by(id=student_id).first()
    if user_to_del:
        db.session.delete(user_to_del)
        db.session.commit()
        flash("Record Deleted", category='success')
    return redirect(url_for('show_all_students'))


# update student record
@app.route('/redirect_to_update_record/<int:student_id>', methods=['GET', 'POST'])
def redirect_to_update_record(student_id):
    form = Form()

    user_to_update = Student.query.filter_by(id=student_id).first()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]

    if request.method == "POST":

        message = ""

        if len(request.form['name']) < 2:
            message = "Minimum name length should be 2 and cannot contain numbers or any special characters"
            flash(message, category='error')
        else:
            user_to_update.name = request.form['name']

        if not request.form['pin'].isnumeric() or len(request.form['pin']) < 6:
            message = "Pin should be in numbers (Max./Min. length: 6)/ No special characters/Alphabets allowed"
            flash(message, category='error')
        else:
            user_to_update.pin = request.form['pin']

        if not request.form['roll_no'].isnumeric():
            message = "Roll No. should be in numbers (Max./Min. length: 6/ No special characters/Alphabets allowed)"
            flash(message, category='error')
        else:
            user_to_update.roll_no = request.form['roll_no']

        if not request.form['standard'].isnumeric():
            message = "Class should be in numbers (special characters/Alphabets allowed)"
            flash(message, category='error')
        else:
            user_to_update.standard = request.form['standard']

        email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(email_reg, request.form['email']):
            user_to_update.email = request.form['email']
        else:
            message = "Enter a Valid Email"
            flash(message, category='error')

        students = Student.query.all()
        for stu in students:
            print(stu.country_id, stu.city_id, stu.state_id)

        search_res = Student.query.filter(
            Student.email == user_to_update.email or Student.roll_no == user_to_update.roll_no)
        for res in search_res:
            print(res.id, res.name, res.roll_no, res.email)
            if res.id == user_to_update.id:
                continue
            flash("User with same Email or Roll No. already exists", category='error')

            return render_template('update_student.html', user_to_update=user_to_update, form=form)
        # exists = Student.query.filter(
        #     Student.id == user_to_update.id or Student.email == user_to_update.email or Student.roll_no == user_to_update.roll_no).all()

        # exists = db.session.query(db.exists().where(Student.id != user_to_update.id and (
        #         Student.email == user_to_update.email or Student.roll_no == user_to_update.roll_no))).scalar()
        # if exists:
        #     flash("User with same Email or Roll No. already exists", category='error')

        if message:
            return render_template('update_student.html', user_to_update=user_to_update, form=form)
        else:

            db.session.commit()
            flash("Record Updated!", category='success')
            return redirect(url_for('show_all_students'))
    return render_template('update_student.html', user_to_update=user_to_update, form=form)


# show all countries record
@app.route('/show_all_country')
def show_all_country():
    return render_template('show_country_list.html', countries=Country.query.all())


# redirect to add country
@app.route('/redirect_to_add_country')
def redirect_to_add_country():
    return redirect('show_all_country')


# add country
@app.route('/add_country', methods=['GET', 'POST'])
def add_country():
    if request.method == "POST":

        if not request.form['name']:
            flash('Field required!', category='error')

        if not request.form['name']:
            message = '''Country cannot contain numbers 
                        or any special characters'''
            flash(message, category='error')

        else:
            country_to_be_added = Country(name=request.form['name'])
            db.session.add(country_to_be_added)
            db.session.commit()
            flash('Record Added', category='success')
            return redirect(url_for('show_all_country'))
    return redirect(url_for('show_all_country'))


# delete country
@app.route('/redirect_to_del_country/<int:country_id>')
def redirect_to_del_country(country_id):
    country_to_del = Country.query.filter_by(id=country_id).first()
    if country_to_del:
        db.session.delete(country_to_del)
        db.session.commit()
        flash("Record Deleted", category='success')
    return redirect(url_for('show_all_country'))


# update country
@app.route('/redirect_to_update_country/<int:country_id>', methods=['GET', 'POST'])
def redirect_to_update_country(country_id):
    country_to_update = Country.query.filter_by(id=country_id).first()
    if request.method == "POST":
        message = ""
        if not request.form["name"]:
            message = "Field cannot be empty"
            flash(message, category='error')
        else:
            country_to_update.name = request.form['name']

        if not request.form['name'].isalpha():
            message = "State cannot contain numbers or any special characters"
            flash(message, category='error')
        else:
            country_to_update.name = request.form['name']

        if message:
            return render_template('update_country.html', country_to_update=country_to_update)
        else:
            db.session.commit()
            flash("Record Updated!", category='success')
            return redirect(url_for('show_all_country'))
    return render_template('update_country.html', country_to_update=country_to_update)


# show all states record
@app.route('/show_all_states')
def show_all_states():
    return render_template('show_state_list.html', states=State.query.all())


# redirect to add states
@app.route('/redirect_to_add_state')
def redirect_to_add_state():
    return redirect('show_all_states')


# add state
@app.route('/add_state', methods=['GET', 'POST'])
def add_state():
    if request.method == "POST":

        if not request.form['name']:
            flash('Field required!', category='error')

        if not request.form['name'].isalpha():
            message = '''State cannot contain numbers 
                        or any special characters'''
            flash(message, category='error')

        else:
            state_to_be_added = State(name=request.form['name'])
            db.session.add(state_to_be_added)
            db.session.commit()
            flash('Record Added', category='success')
            return redirect(url_for('show_all_states'))
    return redirect(url_for('show_all_states'))


# del state
@app.route('/redirect_to_del_state/<int:state_id>')
def redirect_to_del_state(state_id):
    state_to_del = State.query.filter_by(id=state_id).first()
    if state_to_del:
        db.session.delete(state_to_del)
        db.session.commit()
        flash("Record Deleted", category='success')
    return redirect(url_for('show_all_states'))


# update state
@app.route('/redirect_to_update_state/<int:state_id>', methods=['GET', 'POST'])
def redirect_to_update_state(state_id):
    form = Form()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]
    state_to_update = State.query.filter_by(id=state_id).first()
    if request.method == "POST":
        message = ""

        state_to_update.country_id = request.form['country']

        if not request.form['name'].isalpha():
            message = "State cannot contain numbers or any special characters"
            flash(message, category='error')
        else:
            state_to_update.name = request.form['name']

        if message:
            return render_template('update_state.html', state_to_update=state_to_update, form=form)
        else:
            db.session.commit()
            flash("Record Updated!", category='success')
            return redirect(url_for('show_all_states'))
    return render_template('update_state.html', state_to_update=state_to_update, form=form)


# show all cities record
@app.route('/show_all_cities')
def show_all_cities():
    return render_template('show_city_list.html', cities=City.query.all())


# redirect to add city
@app.route('/redirect_to_add_city')
def redirect_to_add_city():
    return redirect('show_all_cities')


# add city
@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    if request.method == "POST":

        if not request.form['name']:
            flash('Field required!', category='error')

        if not request.form['name'].isalpha():
            message = '''City cannot contain numbers 
                        or any special characters'''
            flash(message, category='error')

        else:
            city_to_be_added = City(name=request.form['name'])
            db.session.add(city_to_be_added)
            db.session.commit()
            flash('Record Added', category='success')
            return redirect(url_for('show_all_cities'))
    return redirect(url_for('show_all_cities'))


# delete city
@app.route('/redirect_to_del_city/<int:city_id>')
def redirect_to_del_city(city_id):
    city_to_del = City.query.filter_by(id=city_id).first()
    if city_to_del:
        db.session.delete(city_to_del)
        db.session.commit()
        flash("Record Deleted", category='success')
    return redirect(url_for('show_all_cities'))


# update city
@app.route('/redirect_to_update_city/<int:city_id>', methods=['GET', 'POST'])
def redirect_to_update_city(city_id):
    form = Form()
    form.state.choices = [(state.id, state.name) for state in State.query.all()]

    form.country.choices = [(country.id, country.name) for country in Country.query.all()]

    city_to_update = City.query.filter_by(id=city_id).first()

    if request.method == "POST":
        message = ""
        if request.form["name"].isnumeric():
            message = "Numbers or special characters not allowed"
            flash(message, category='error')
        else:
            city_to_update.name = request.form['name']
        if not request.form["state"]:
            message = 'Field required'
            flash(message, category='error')
        else:
            city_to_update.state_id = request.form['state']
        if not request.form["country"]:
            message = 'Field required'
            flash(message, category='error')
        else:
            city_to_update.country_id = request.form['country']

        if message:
            return render_template('update_city.html', city_to_update=city_to_update, form=form)
        else:
            db.session.commit()
            flash("Record Updated!", category='success')
            return redirect(url_for('show_all_cities'))
    return render_template('update_city.html', city_to_update=city_to_update, form=form)


@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    stu_ids = request.form['stu_ids']
    for ids in stu_ids.split(','):
        delete_student = Student.query.filter_by(id=ids).first()
        db.session.delete(delete_student)
        db.session.commit()
        flash(f"Deleted {delete_student.name}'s Record", category='success')
    return redirect('show_all_students')


@app.route('/send_class_id', methods=['GET', 'POST'])
def send_class_id():
    class_ids = request.form["class_ids"]
    if request.method == "POST":
        return render_template('update_class.html', stu_ids=class_ids)


@app.route('/update_class', methods=['GET', 'POST'])
def update_class():
    student_ids = request.form["standard_id"]
    for ids in student_ids.split(','):
        if request.method == "POST":
            student_class_to_update = Student.query.filter_by(id=ids).first()
            student_class_to_update.standard = request.form["standard"]
            db.session.commit()
            flash(f"Updated {student_class_to_update.name}'s Record", category='success')
    return redirect('show_all_students')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
