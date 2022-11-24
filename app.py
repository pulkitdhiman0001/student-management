import re
from datetime import timedelta

from flask import render_template, request, url_for, flash, redirect, jsonify, session
from sqlalchemy import desc, cast, Integer
from werkzeug.security import generate_password_hash, check_password_hash

from forms import Form
from models import State, Student, City, Country, app, db, Users, Standard, Section
from templates import HtmlTemplates

templates = HtmlTemplates()
record_added = "Record Added"
record_deleted = "Record Deleted"
record_updated = "Record Updated"
required = "Field required!"


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
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        for i in Users.query.all():
            if i.username == username and check_password_hash(i.password, password):
                session["username"] = i.username
                session.permanent = True
                app.permanent_session_lifetime = timedelta(minutes=5)
                return redirect(url_for('home'))

        flash('Username or password is incorrect', category='error')
    return render_template(templates.login)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        if request.method == 'POST':
            userpass = request.form["password"]
            confirm_userpass = request.form["confirm_password"]
            hash_pass = generate_password_hash(userpass)
            if not userpass or not request.form["password"]:
                flash("All Fields are required", category='error')
                return render_template(templates.add_user)
            add_new_user = Users(username=request.form["username"], password=hash_pass)

            exists = db.session.query(db.exists().where(
                Users.username == request.form["username"])).scalar()
            if exists:
                flash("User with same username already exists", category='error')
                return render_template('register.html')
            if userpass != confirm_userpass:
                flash("Password does not match", category='error')
                return render_template('register.html')

            pass_regex = '^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z]).{8,}$'
            if not re.fullmatch(pass_regex, userpass):
                flash("Password must contain the following \n (Upper case and lower case letter, one special symbol, "
                      "one number)", category='error')
            else:
                db.session.add(add_new_user)
                db.session.commit()
                flash('User Created', category='success')
                return redirect(url_for('login'))
        return render_template(templates.register)
    flash("Admin Credentials Required", category='error')
    return render_template(templates.login)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        users = Users.query.all()
        return render_template('users.html', users=users)
    return render_template(templates.login)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        userpass = request.form["password"]
        confirm_userpass = request.form["confirm_password"]
        hash_pass = generate_password_hash(userpass)

        if not userpass or not request.form["password"]:
            flash("All Fields are required", category='error')
            return render_template(templates.add_user)

        add_user = Users(username=request.form["username"], password=hash_pass)

        exists = db.session.query(db.exists().where(
            Users.username == request.form["username"])).scalar()
        if exists:
            flash("User with same username already exists", category='error')
            return render_template(templates.add_user)
        if userpass != confirm_userpass:
            flash("Password does not match", category='error')
            return render_template(templates.add_user)
        else:
            db.session.add(add_user)
            db.session.commit()
            flash('User Created', category='success')
            return redirect(url_for('manage_users'))
    return render_template(templates.add_user)


@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    if 'username' in session:
        user_to_del = Users.query.filter_by(id=user_id).first()
        if session["username"] == user_to_del.username:
            flash('Cannot delete a user that is logged in', category='error')
            return redirect(url_for('manage_users'))
        elif user_to_del:
            db.session.delete(user_to_del)
            db.session.commit()
            flash("User Deleted", category='success')
        return redirect(url_for('manage_users'))
    return render_template(templates.login)


@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def update_user(user_id):
    if 'username' in session:
        user_to_update = Users.query.filter_by(id=user_id).first()
        if request.method == 'POST':
            user_to_update.username = request.form["username"]
            user_to_update.password = generate_password_hash(request.form["password"])

            db.session.commit()
            flash('User Updated', category='success')
            return redirect(url_for('manage_users'))
        return render_template(templates.update_user, user_to_update=user_to_update)
    return render_template(templates.login)


# home
@app.route('/home')
def home():
    if 'username' in session:
        students = Student.query.order_by(desc(Student.id))
        return render_template(templates.dashboard, students=students)
    return render_template(templates.login)


# Show all students records


# add student
@app.route('/add_students', methods=['GET', 'POST'])
def add_students():
    if 'username' in session:
        form = Form()

        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        form.state.choices = [(state.id, state.name) for state in State.query.all()]
        form.city.choices = [(city.id, city.name) for city in City.query.all()]
        form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
        form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]

        if request.method == "POST":
            city = City.query.filter_by(id=form.city.data).first()
            country = Country.query.filter_by(id=form.country.data).first()
            state = State.query.filter_by(id=form.state.data).first()
            standard = Standard.query.filter_by(id=form.standard.data).first()
            section = Section.query.filter_by(id=form.section.data).first()

            message = ""

            special_char = re.compile('[@_.,!#$%^&*()<>?/\|}{~:]')

            for fname in request.form['fname']:
                if fname.isdigit() or special_char.search(fname):
                    message = "First Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break

            for lname in request.form['lname']:
                if lname.isdigit() or special_char.search(lname):
                    message = "Last Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break
            for mother_name in request.form['mother_name']:
                if mother_name.isdigit() or special_char.search(mother_name):
                    message = "Mother Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break
            for father_name in request.form['father_name']:
                if father_name.isdigit() or special_char.search(father_name):
                    message = "Father Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break

            if not request.form['pin'].isnumeric():
                message = "Pin should be in numbers. No special characters/Alphabets allowed"
                flash(message, category='error')

            if not request.form['roll_no'].isnumeric():
                message = "Roll No. should be in numbers (Max./Min. length: 6/ No special characters/Alphabets allowed)"
                flash(message, category='error')

            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if not re.fullmatch(email_reg, request.form['email']):
                message = "Enter a Valid Email"
                flash(message, category='error')

            same_email = Student.query.filter(
                Student.email == request.form["email"])

            same_roll = Student.query.filter(
                Student.roll_no == request.form["roll_no"]
            )

            for res in same_email:

                if res.id == Student.id:
                    continue
                flash("User with same Email already exists", category='error')

                return render_template(templates.add_student, form=form)

            for res in same_roll:

                if res.id == Student.id:
                    continue

                flash("User with same Roll No. already exists", category='error')

                return render_template(templates.add_student, form=form)

            if message:
                form.country.default = request.form["country"]
                form.state.default = request.form["state"]
                form.city.default = request.form["city"]
                form.standard.default = request.form["standard"]
                form.section.default = request.form["section"]
                form.process()
                return render_template('add_student.html', form=form)
            else:
                student = Student(fname=request.form['fname'], lname=request.form["lname"],
                                  mother_name=request.form["mother_name"], father_name=request.form["father_name"],
                                  addr=request.form['addr'], country_id=country.id,
                                  state_id=state.id, city_id=city.id, pin=request.form['pin'],
                                  standard_id=standard.id,
                                  section_id=section.id,
                                  roll_no=request.form['roll_no'],
                                  email=request.form['email'])

            exists = db.session.query(db.exists().where(
                Student.email == request.form["email"] or Student.roll_no == request.form["roll_no"])).scalar()
            if exists:

                flash("User with same Email or Roll No. already exists", category='error')
                return render_template(templates.add_student, form=form)
            else:

                db.session.add(student)
                db.session.commit()
                flash(record_added, category='success')
                return redirect(url_for('home'))
        return render_template(templates.add_student, form=form)
    return render_template(templates.login)


# delete student record
@app.route('/del_student/<int:student_id>')
def del_student(student_id):
    if 'username' in session:
        user_to_del = Student.query.filter_by(id=student_id).first()
        if user_to_del:
            db.session.delete(user_to_del)
            db.session.commit()
            flash(record_deleted, category='success')
        return redirect(url_for('home'))
    return render_template(templates.login)


@app.route('/student_details/<int:student_id>', methods=['GET', 'POST'])
def student_details(student_id):
    if 'username' in session:
        form = Form()
        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        form.state.choices = [(state.id, state.name) for state in State.query.all()]
        form.city.choices = [(city.id, city.name) for city in City.query.all()]
        form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
        form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]

        user_to_update = Student.query.filter_by(id=student_id).first()

        if request.method == "POST":

            message = ""
            special_char = re.compile('[@_.,!#$%^&*()<>?/\|}{~:]')

            for fname in request.form['fname']:
                if fname.isdigit() or special_char.search(fname):
                    message = "First Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break

            for lname in request.form['lname']:
                if lname.isdigit() or special_char.search(lname):
                    message = "Last Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break
            for mother_name in request.form['mother_name']:
                if mother_name.isdigit() or special_char.search(mother_name):
                    message = "Mother Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break
            for father_name in request.form['father_name']:
                if father_name.isdigit() or special_char.search(father_name):
                    message = "Father Name cannot contain numbers or any special characters"
                    flash(message, category='error')
                    break
            else:
                user_to_update.fname = request.form['fname']
                user_to_update.lname = request.form['lname']
                user_to_update.mother_name = request.form['mother_name']
                user_to_update.father_name = request.form['father_name']

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

            email_reg = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            if re.fullmatch(email_reg, request.form['email']):
                user_to_update.email = request.form['email']
            else:
                message = "Enter a Valid Email"
                flash(message, category='error')

            same_email = Student.query.filter(
                Student.email == user_to_update.email)

            same_roll = Student.query.filter(
                Student.id != user_to_update.id, Student.standard_id == user_to_update.standard_id,
                Student.section_id == user_to_update.section_id, Student.roll_no == user_to_update.roll_no
            )

            for res in same_email:

                if res.id == user_to_update.id:
                    continue
                flash("User with same Email already exists", category='error')

                return render_template(templates.student_details, user_to_update=user_to_update, form=form)

            for res in same_roll:

                if res.id == user_to_update.id:
                    continue

                flash("User with same Roll No. already exists", category='error')

                return render_template(templates.student_details, user_to_update=user_to_update, form=form)

            if message:
                return render_template(templates.student_details, user_to_update=user_to_update, form=form)
            else:
                user_to_update.addr = request.form['addr']
                user_to_update.country_id = request.form["country"]
                user_to_update.state_id = request.form["state"]
                user_to_update.city_id = request.form['city']
                user_to_update.standard_id = request.form["standard"]
                user_to_update.section_id = request.form["section"]

                db.session.commit()
                flash(record_updated, category='success')
                return redirect(url_for('home'))

        form.country.default = user_to_update.country_id
        form.state.default = user_to_update.state_id
        form.city.default = user_to_update.city.id

        form.standard.default = user_to_update.standard.id
        form.section.default = user_to_update.section.id
        form.process()

        return render_template(templates.student_details, user_to_update=user_to_update, form=form)
    return render_template(templates.login)


# show all countries record
@app.route('/all_countries')
def all_countries():
    if 'username' in session:
        return render_template(templates.show_country_list, countries=Country.query.all())
    return render_template(templates.login)


# add country
@app.route('/add_country', methods=['GET', 'POST'])
def add_country():
    if 'username' in session:
        if request.method == "POST":

            exists = db.session.query(Country.id).filter_by(
                name=request.form["name"].capitalize()).first() is not None

            if exists:
                flash("Country Already Exists", category='danger')
                return redirect(url_for('all_countries'))

            if not request.form['name']:
                flash(required, category='error')

            if not request.form['name']:
                message = '''Country cannot contain numbers 
                            or any special characters'''
                flash(message, category='error')

            else:
                country_to_be_added = Country(name=request.form['name'])
                db.session.add(country_to_be_added)
                db.session.commit()
                flash(record_added, category='success')
                return redirect(url_for('all_countries'))
        return redirect(url_for('all_countries'))
    return render_template(templates.login)


# delete country
@app.route('/del_country/<int:country_id>')
def del_country(country_id):
    if 'username' in session:

        country_to_del = Country.query.filter_by(id=country_id).first()
        if Student.query.filter_by(country_id=country_id).first():
            flash("Country in use", category='error')

        else:
            db.session.delete(country_to_del)
            db.session.commit()
            flash(record_deleted, category='success')
        return redirect(url_for('all_countries'))

    return render_template(templates.login)


# update country
@app.route('/update_country/<int:country_id>', methods=['GET', 'POST'])
def update_country(country_id):
    if 'username' in session:
        country_to_update = Country.query.filter_by(id=country_id).first()
        if request.method == "POST":
            message = ""
            if not request.form["name"]:
                message = "Field cannot be empty"
                flash(message, category='error')
            else:
                country_to_update.name = request.form['name']

            if not request.form['name'].isalpha():
                message = "Country cannot contain numbers or any special characters"
                flash(message, category='error')
            else:
                country_to_update.name = request.form['name']

            if message:
                return render_template(templates.update_country, country_to_update=country_to_update)
            else:
                db.session.commit()
                flash(record_updated, category='success')
                return redirect(url_for('all_countries'))
        return render_template(templates.update_country, country_to_update=country_to_update)
    return render_template(templates.login)


# show all states record
@app.route('/all_states')
def all_states():
    if 'username' in session:
        form = Form()
        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        return render_template(templates.show_state_list, states=State.query.all(), form=form)
    return render_template(templates.login)


# add state
@app.route('/add_state', methods=['GET', 'POST'])
def add_state():
    form = Form()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]
    form.state.choices = [(state.id, state.name) for state in State.query.all()]

    if 'username' in session:
        if request.method == "POST":

            exists = db.session.query(State.id).filter_by(
                name=request.form["name"].capitalize()).first() is not None

            if exists:
                flash("State Already Exists", category='danger')
                return redirect(url_for('all_states'))

            if not request.form['name']:
                flash(required, category='error')

            if not request.form['name'].isalpha():
                message = '''State cannot contain numbers 
                            or any special characters'''
                flash(message, category='error')
                return redirect(url_for('all_states'))

            else:
                state_to_be_added = State(name=request.form['name'])
                state_to_be_added.country_id = request.form["country"]
                db.session.add(state_to_be_added)

                db.session.commit()
                flash(record_added, category='success')
                return redirect(url_for('all_states'))
        return render_template(templates.show_state_list, form=form)
    return render_template(templates.login)


# Delete state
@app.route('/del_state/<int:state_id>')
def del_state(state_id):
    if 'username' in session:
        state_to_del = State.query.filter_by(id=state_id).first()
        if Student.query.filter_by(state_id=state_id).first():
            flash("State in use", category='error')

        else:
            db.session.delete(state_to_del)
            db.session.commit()
            flash(record_deleted, category='success')
        return redirect(url_for('all_states'))
    return render_template(templates.login)


# update state
@app.route('/update_state/<int:state_id>', methods=['GET', 'POST'])
def update_state(state_id):
    if 'username' in session:
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
                return render_template(templates.update_state, state_to_update=state_to_update, form=form)
            else:

                db.session.commit()
                flash(record_updated, category='success')
                return redirect(url_for('all_states'))

        form.country.default = state_to_update.country_id
        form.process()
        return render_template(templates.update_state, state_to_update=state_to_update, form=form)
    return render_template(templates.login)


# show all cities record
@app.route('/all_cities')
def all_cities():
    form = Form()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]
    form.state.choices = [(state.id, state.name) for state in State.query.all()]
    if 'username' in session:
        return render_template(templates.show_city_list, cities=City.query.all(), form=form)
    return render_template(templates.login)


# add city
@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    form = Form()
    form.country.choices = [(country.id, country.name) for country in Country.query.all()]
    form.state.choices = [(state.id, state.name) for state in State.query.all()]
    if 'username' in session:
        if request.method == "POST":

            exists = db.session.query(City.id).filter_by(
                name=request.form["name"].capitalize()).first() is not None

            if exists:
                flash("City Already Exists", category='danger')
                return redirect(url_for('all_cities'))

            if not request.form['name']:
                flash(required, category='error')

            if not request.form['name'].isalpha():
                message = '''City cannot contain numbers 
                            or any special characters'''
                flash(message, category='error')

            else:
                city_to_be_added = City(name=request.form['name'])
                city_to_be_added.country_id = request.form["country"]
                city_to_be_added.state_id = request.form["state"]
                db.session.add(city_to_be_added)
                db.session.commit()
                flash(record_added, category='success')
                return redirect(url_for('all_cities'))

        return render_template('show_city_list.html', form=form)
    return render_template(templates.login)


# delete city
@app.route('/del_city/<int:city_id>')
def del_city(city_id):
    if 'username' in session:
        city_to_del = City.query.filter_by(id=city_id).first()
        if Student.query.filter_by(city_id=city_id).first():
            flash("City in use", category='error')
            return redirect(url_for('all_cities'))
        else:
            db.session.delete(city_to_del)
            db.session.commit()
            flash(record_deleted, category='success')
        return redirect(url_for('all_cities'))
    return render_template(templates.login)


# update city
@app.route('/update_city/<int:city_id>', methods=['GET', 'POST'])
def update_city(city_id):
    if 'username' in session:
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
                return render_template(templates.update_city, city_to_update=city_to_update, form=form)
            else:
                db.session.commit()
                flash(record_updated, category='success')
                return redirect(url_for('all_cities'))

        form.state.default = city_to_update.state_id
        form.country.default = city_to_update.country_id
        form.process()
        return render_template(templates.update_city, city_to_update=city_to_update, form=form)
    return render_template(templates.login)


@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session and request.method == "POST":
        stu_ids = request.form['stu_ids']
        for ids in stu_ids.split(','):
            delete_student = Student.query.filter_by(id=ids).first()
            db.session.delete(delete_student)
            db.session.commit()
        flash(record_deleted, category='success')
        return redirect(url_for('home'))

    return render_template(templates.login)


@app.route('/send_class_id', methods=['GET', 'POST'])
def send_class_id():
    form = Form()
    form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
    form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]
    if 'username' in session:
        class_ids = request.form["class_ids"]
        if request.method == "POST":
            return render_template(templates.update_class, stu_ids=class_ids, form=form)
    return render_template(templates.login)


@app.route('/update_class', methods=['GET', 'POST'])
def update_class():
    form = Form()
    form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
    form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]
    if 'username' in session:
        student_ids = request.form["standard_id"]
        for ids in student_ids.split(','):
            if request.method == "POST":
                student_class_to_update = Student.query.filter_by(id=ids).first()
                student_class_to_update.standard_id = request.form["standard"]
                student_class_to_update.section_id = request.form["section"]
                db.session.commit()
        flash(record_updated, category='success')
        return redirect(url_for('home', form=form))
    return render_template(templates.login)


@app.route('/standard_section', methods=['GET', 'POST'])
def standard_section():
    if 'username' in session:
        sections = Section.query.order_by(Section.section_name).all()
        standards = Standard.query.order_by(cast(Standard.standard_name, Integer))
        return render_template(templates.add_standard_section, standards=standards,
                               sections=sections)
    return render_template(templates.login)


@app.route('/add_standard', methods=['GET', 'POST'])
def add_standard():
    if 'username' in session:
        if request.method == "POST":

            exists = db.session.query(Standard.id).filter_by(
                standard_name=request.form["standard_name"]).first() is not None
            if exists:
                flash("Standard already exists", category='error')
                return redirect(url_for('standard_section'))
            if len(request.form["standard_name"]) > 12:
                flash("Standard limit is 12", category='error')
                return redirect(url_for('standard_section'))
            if not request.form["standard_name"].isnumeric():
                flash("Standard should be in numbers only", category='error')
                return redirect(url_for('standard_section'))

            if not request.form['standard_name']:
                flash(required, category='error')
            else:
                standard_to_be_added = Standard(standard_name=request.form['standard_name'])
                db.session.add(standard_to_be_added)
                db.session.commit()
                flash('New Standard Added', category='success')
                return redirect(url_for('standard_section'))
        return render_template(templates.add_standard_section, standards=Standard.query.all())
    return render_template(templates.login)


@app.route('/del_standard/<int:standard_id>')
def del_standard(standard_id):
    if 'username' in session:
        standard_to_del = Standard.query.filter_by(id=standard_id).first()

        if Student.query.filter_by(standard_id=standard_id).first():
            flash("Standard in use", category='error')
            return redirect(url_for('standard_section'))

        if standard_to_del:
            db.session.delete(standard_to_del)
            db.session.commit()
            flash(f"Standard {standard_to_del.standard_name}th Deleted", category='success')
        return redirect(url_for('standard_section'))
    return render_template(templates.login)


@app.route('/update_standard/<int:standard_id>', methods=['GET', 'POST'])
def update_standard(standard_id):
    if 'username' in session:
        standard_to_update = Standard.query.filter_by(id=standard_id).first()
        if request.method == 'POST':
            standard_to_update.standard_name = request.form["standard_name"]
            db.session.commit()
            flash('Standard Updated', category='success')
            return redirect(url_for('standard_section'))
        return render_template(templates.update_standard, standard_to_update=standard_to_update)
    return render_template(templates.login)


@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if 'username' in session:
        if request.method == "POST":
            exists = db.session.query(Section.id).filter_by(
                section_name=request.form["section_name"].upper()).first() is not None
            if exists:
                flash("Section already exists", category='error')
                return redirect(url_for('standard_section'))
            if len(request.form["section_name"]) > 1:
                flash("Section requires only one Alphabet", category='error')
                return redirect(url_for('standard_section'))
            if request.form['section_name'].isnumeric():
                flash("Section should be in Alphabets only", category='error')
                return redirect(url_for('standard_section'))
            else:
                section_to_be_added = Section(section_name=request.form['section_name'].upper())
                db.session.add(section_to_be_added)
                db.session.commit()
                flash('New Section Added', category='success')
                return redirect(url_for('standard_section'))
        return render_template(templates.add_standard_section, sections=Section.query.all())
    return render_template(templates.login)


@app.route('/del_section/<int:section_id>')
def del_section(section_id):
    if 'username' in session:
        section_to_del = Section.query.filter_by(id=section_id).first()

        if Student.query.filter_by(section_id=section_id).first():
            flash("Section in use", category='error')
            return redirect(url_for('standard_section'))

        if section_to_del:
            db.session.delete(section_to_del)
            db.session.commit()
            flash(f"Section '{section_to_del.section_name}' Deleted", category='success')
        return redirect(url_for('standard_section'))
    return render_template(templates.login)


@app.route('/update_section/<int:section_id>', methods=['GET', 'POST'])
def update_section(section_id):
    if 'username' in session:
        section_to_update = Standard.query.filter_by(id=section_id).first()
        if request.method == 'POST':
            section_to_update.section_name = request.form["section_name"]
            db.session.commit()
            flash('Section Updated', category='success')
            return redirect(url_for('standard_section'))
        return render_template(templates.update_section, section_to_update=section_to_update)
    return render_template(templates.login)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
