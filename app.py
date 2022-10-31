import re
from werkzeug.security import generate_password_hash, check_password_hash
from flask import render_template, request, url_for, flash, redirect, jsonify, session
from sqlalchemy import desc

from datetime import timedelta

from forms import Form
from models import State, Student, City, Country, app, db, Users, Standard, Section


# jwt = JWTManager(app)

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


# @app.route('/get_standard_list')
# def get_standard_list(standard_id):
#     result = Standard.query.filter_by().all()
#     standard_list = []
#     for standard in result:
#         standard_obj = {
#             'id': standard.id,
#             'standard_name': standard.standard_name
#         }
#         standard_list.append(standard_obj)
#     return jsonify({'standard_list': standard_list})


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
                # access_token = create_access_token(identity=username)
                # return jsonify(access_token=access_token)
                return redirect(url_for('home'))

        flash('Username or password is incorrect', category='error')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userpass = request.form["password"]
        confirm_userpass = request.form["confirm_password"]
        hash_pass = generate_password_hash(userpass)

        add_user = Users(username=request.form["username"], password=hash_pass)

        exists = db.session.query(db.exists().where(
            Users.username == request.form["username"])).scalar()
        if exists:
            flash("User with same username already exists", category='error')
            return render_template('register.html')
        if userpass != confirm_userpass:
            flash("Password does not match", category='error')
            return render_template('register.html')
        else:
            db.session.add(add_user)
            db.session.commit()
            flash('User Created', category='success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' in session:
        users = Users.query.all()
        return render_template('users.html', users=users)
    return render_template('login.html')


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
    return render_template('login.html')


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
        return render_template('update_user.html', user_to_update=user_to_update)
    return render_template('login.html')


# home
@app.route('/home')
def home():
    if 'username' in session:
        students = Student.query.order_by(desc(Student.id))
        return render_template('dashboard.html', students=students)
    return render_template('login.html')


# Show all students records


# add student
@app.route('/add_students', methods=['GET', 'POST'])
def add_students():
    if 'username' in session:
        form = Form()
        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
        form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]

        if request.method == "POST":
            city = City.query.filter_by(id=form.city.data).first()
            country = Country.query.filter_by(id=form.country.data).first()
            state = State.query.filter_by(id=form.state.data).first()
            standard = Standard.query.filter_by(id=form.standard.data).first()
            section = Section.query.filter_by(id=form.section.data).first()

            message = ""

            if (request.form['fname'] or request.form["lname"]).isnumeric():
                message = '''Minimum name length should be 2 
                            and cannot contain numbers 
                            or any special characters'''
                flash(message, category='error')

            if not request.form['pin'].isnumeric() or len(request.form['pin']) < 6:
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
                return render_template('add_student.html', form=form)
            else:
                db.session.add(student)
                db.session.commit()
                flash("Record added!", category='success')
                return redirect(url_for('home'))

        return render_template('add_student.html', form=form)
    return render_template('login.html')


# delete student record
@app.route('/del_student/<int:student_id>')
def del_student(student_id):
    if 'username' in session:
        user_to_del = Student.query.filter_by(id=student_id).first()
        if user_to_del:
            db.session.delete(user_to_del)
            db.session.commit()
            flash(f"Record Deleted", category='success')
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/student_details/<int:student_id>', methods=['GET', 'POST'])
def student_details(student_id):
    if 'username' in session:

        form = Form()

        user_to_update = Student.query.filter_by(id=student_id).first()
        form.country.choices = [(country.id, country.name) for country in Country.query.all()]
        form.state.choices = [(state.id, state.name) for state in State.query.all()]
        form.city.choices = [(city.id, city.name) for city in City.query.all()]
        form.standard.choices = [(standard.id, standard.standard_name) for standard in Standard.query.all()]
        form.section.choices = [(section.id, section.section_name) for section in Section.query.all()]

        if request.method == "POST":

            message = ""

            if (request.form['fname'] or request.form['lname'] or request.form["father_name"] or request.form[
                "mother_name"]).isnumeric():
                message = "Name cannot contain numbers or any special characters"
                flash(message, category='error')
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

            search_res = Student.query.filter(
                Student.email == user_to_update.email or Student.roll_no == user_to_update.roll_no)
            for res in search_res:

                if res.id == user_to_update.id:
                    continue
                flash("User with same Email or Roll No. already exists", category='error')

                return render_template('student_details.html', user_to_update=user_to_update, form=form)

            if message:
                return render_template('student_details.html', user_to_update=user_to_update, form=form)
            else:
                user_to_update.addr = request.form['addr']
                db.session.commit()
                flash("Record Updated!", category='success')
                return redirect(url_for('home'))

        print(user_to_update.country.name, user_to_update.state.name)
        form.country.default = user_to_update.country_id
        form.state.default = user_to_update.state_id
        form.city.default = user_to_update.city.id

        form.standard.default = user_to_update.standard.id
        form.section.default = user_to_update.section.id
        form.process()

        return render_template('student_details.html', user_to_update=user_to_update, form=form)
    return render_template('login.html')


# show all countries record
@app.route('/show_all_country')
def show_all_country():
    if 'username' in session:
        return render_template('show_country_list.html', countries=Country.query.all())
    return render_template('login.html')


# redirect to add country
@app.route('/redirect_to_add_country')
def redirect_to_add_country():
    if 'username' in session:
        return redirect('show_all_country')
    return render_template('login.html')


# add country
@app.route('/add_country', methods=['GET', 'POST'])
def add_country():
    if 'username' in session:
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
    return render_template('login.html')


# delete country
@app.route('/redirect_to_del_country/<int:country_id>')
def redirect_to_del_country(country_id):
    if 'username' in session:
        country_to_del = Country.query.filter_by(id=country_id).first()
        if country_to_del:
            db.session.delete(country_to_del)
            db.session.commit()
            flash("Record Deleted", category='success')
        return redirect(url_for('show_all_country'))
    return render_template('login.html')


# update country
@app.route('/redirect_to_update_country/<int:country_id>', methods=['GET', 'POST'])
def redirect_to_update_country(country_id):
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
    return render_template('login.html')


# show all states record
@app.route('/show_all_states')
def show_all_states():
    if 'username' in session:
        return render_template('show_state_list.html', states=State.query.all())
    return render_template('login.html')


# redirect to add states
@app.route('/redirect_to_add_state')
def redirect_to_add_state():
    if 'username' in session:
        return redirect('show_all_states')
    return render_template('login.html')


# add state
@app.route('/add_state', methods=['GET', 'POST'])
def add_state():
    if 'username' in session:
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
    return render_template('login.html')


# del state
@app.route('/redirect_to_del_state/<int:state_id>')
def redirect_to_del_state(state_id):
    if 'username' in session:
        state_to_del = State.query.filter_by(id=state_id).first()
        if state_to_del:
            db.session.delete(state_to_del)
            db.session.commit()
            flash("Record Deleted", category='success')
        return redirect(url_for('show_all_states'))
    return render_template('login.html')


# update state
@app.route('/redirect_to_update_state/<int:state_id>', methods=['GET', 'POST'])
def redirect_to_update_state(state_id):
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
                return render_template('update_state.html', state_to_update=state_to_update, form=form)
            else:
                db.session.commit()
                flash("Record Updated!", category='success')
                return redirect(url_for('show_all_states'))
        return render_template('update_state.html', state_to_update=state_to_update, form=form)
    return render_template('login.html')


# show all cities record
@app.route('/show_all_cities')
def show_all_cities():
    if 'username' in session:
        return render_template('show_city_list.html', cities=City.query.all())
    return render_template('login.html')


# redirect to add city
@app.route('/redirect_to_add_city')
def redirect_to_add_city():
    if 'username' in session:
        return redirect('show_all_cities')
    return render_template('login.html')


# add city
@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    if 'username' in session:
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
    return render_template('login.html')


# delete city
@app.route('/redirect_to_del_city/<int:city_id>')
def redirect_to_del_city(city_id):
    if 'username' in session:
        city_to_del = City.query.filter_by(id=city_id).first()
        if city_to_del:
            db.session.delete(city_to_del)
            db.session.commit()
            flash("Record Deleted", category='success')
        return redirect(url_for('show_all_cities'))
    return render_template('login.html')


# update city
@app.route('/redirect_to_update_city/<int:city_id>', methods=['GET', 'POST'])
def redirect_to_update_city(city_id):
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
                return render_template('update_city.html', city_to_update=city_to_update, form=form)
            else:
                db.session.commit()
                flash("Record Updated!", category='success')
                return redirect(url_for('show_all_cities'))
        return render_template('update_city.html', city_to_update=city_to_update, form=form)
    return render_template('login.html')


@app.route('/get_checked_boxes', methods=['GET', 'POST'])
def get_checked_boxes():
    if 'username' in session:
        if request.method == "POST":
            stu_ids = request.form['stu_ids']
            for ids in stu_ids.split(','):
                delete_student = Student.query.filter_by(id=ids).first()
                db.session.delete(delete_student)
                db.session.commit()
                flash(f"Record Deleted", category='success')
            return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/send_class_id', methods=['GET', 'POST'])
def send_class_id():
    if 'username' in session:
        class_ids = request.form["class_ids"]
        if request.method == "POST":
            return render_template('update_class.html', stu_ids=class_ids)
    return render_template('login.html')


@app.route('/update_class', methods=['GET', 'POST'])
def update_class():
    if 'username' in session:
        student_ids = request.form["standard_id"]
        for ids in student_ids.split(','):
            if request.method == "POST":
                student_class_to_update = Student.query.filter_by(id=ids).first()
                student_class_to_update.standard = request.form["standard"]
                db.session.commit()
                flash(f"Record Updated", category='success')
        return redirect('home')
    return render_template('login.html')


@app.route('/standard_section', methods=['GET', 'POST'])
def standard_section():
    if 'username' in session:
        return render_template('add_standard_section.html', standards=Standard.query.all(),
                               sections=Section.query.all())
    return render_template('login.html')


@app.route('/add_standard', methods=['GET', 'POST'])
def add_standard():
    if 'username' in session:
        if request.method == "POST":

            if not request.form['standard_name']:
                flash('Field required!', category='error')


            else:
                standard_to_be_added = Standard(standard_name=request.form['standard_name'])
                db.session.add(standard_to_be_added)
                db.session.commit()
                flash('New Standard Added', category='success')
                return redirect(url_for('standard_section'))
        return render_template('add_standard_section.html', standards=Standard.query.all())
    return render_template('login.html')


@app.route('/del_standard/<int:standard_id>')
def del_standard(standard_id):
    if 'username' in session:
        standard_to_del = Standard.query.filter_by(id=standard_id).first()
        if standard_to_del:
            db.session.delete(standard_to_del)
            db.session.commit()
            flash(f"Standard {standard_to_del.standard_name}th Deleted", category='success')
        return redirect(url_for('standard_section'))
    return render_template('login.html')


@app.route('/update_standard/<int:standard_id>', methods=['GET', 'POST'])
def update_standard(standard_id):
    if 'username' in session:
        standard_to_update = Standard.query.filter_by(id=standard_id).first()
        if request.method == 'POST':
            standard_to_update.standard_name = request.form["standard_name"]
            db.session.commit()
            flash('Standard Updated', category='success')
            return redirect(url_for('standard_section'))
        return render_template('update_standard.html', standard_to_update=standard_to_update)
    return render_template('login.html')


@app.route('/add_section', methods=['GET', 'POST'])
def add_section():
    if 'username' in session:
        if request.method == "POST":

            if not request.form['section_name']:
                flash('Field required!', category='error')

            else:
                section_to_be_added = Section(section_name=request.form['section_name'])
                db.session.add(section_to_be_added)
                db.session.commit()
                flash('New Section Added', category='success')
                return redirect(url_for('standard_section'))
        return render_template('add_standard_section.html', sections=Section.query.all())
    return render_template('login.html')


@app.route('/del_section/<int:section_id>')
def del_section(section_id):
    if 'username' in session:
        section_to_del = Section.query.filter_by(id=section_id).first()
        if section_to_del:
            db.session.delete(section_to_del)
            db.session.commit()
            flash(f"Standard '{section_to_del.section_name}' Deleted", category='success')
        return redirect(url_for('standard_section'))
    return render_template('login.html')


@app.route('/update_section/<int:section_id>', methods=['GET', 'POST'])
def update_section(section_id):
    if 'username' in session:
        section_to_update = Standard.query.filter_by(id=section_id).first()
        if request.method == 'POST':
            section_to_update.section_name = request.form["section_name"]
            db.session.commit()
            flash('Section Updated', category='success')
            return redirect(url_for('standard_section'))
        return render_template('update_section.html', section_to_update=section_to_update)
    return render_template('login.html')


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
