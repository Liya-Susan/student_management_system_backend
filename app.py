from flask import Flask,render_template,request,session,redirect,url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_cors import CORS
import json

local_server= True
app = Flask(__name__)
CORS(app)
app.secret_key='team5'


login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/studentdatabase'
db=SQLAlchemy(app)

class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class Department(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    branch = db.Column(db.String(255))

    def __init__(self, branch):
        self.branch = branch

    def to_dict(self):
        return {
            'id': self.cid,
            'branch': self.branch
        }

class Attendence(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    attendance=db.Column(db.Integer())

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))





class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(50))
    sname=db.Column(db.String(50))
    sem=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    branch=db.Column(db.String(50))
    email=db.Column(db.String(50))
    number=db.Column(db.String(12))
    address=db.Column(db.String(100))
    

def serialize_sqlalchemy_obj(obj):
    if isinstance(obj, db.Model):
        return {column.key: getattr(obj, column.key) for column in obj.__table__.columns}
    raise TypeError("Type not serializable")

def serialize_student(student):
    return {
        'id': student.id,
        'rollno': student.rollno,
        'sname': student.sname,
        'sem':student.sem,
        'gender':student.gender,
        'branch':student.branch,
        'email':student.email,
        'number':student.number,
        'address':student.address
    }

def serialize_trig(trig):
    return {
        'tid': trig.tid,
        'rollno': trig.rollno,
        'action': trig.action,
        'timestamp': trig.timestamp,
    }



@app.route('/attendance', methods=['GET'])
def get_attendance():
    try:
        attendance_records = Attendence.query.all()

        serialized_data = []
        for record in attendance_records:
            serialized_data.append({
                'aid': record.aid,
                'rollno': record.rollno,
                'attendance': record.attendance
            })

        return jsonify(serialized_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/triggers')
def triggers():
    triggers=Trig.query.all()
    serialized_triggers = [serialize_trig(trigger) for trigger in triggers]
    return jsonify(serialized_triggers)

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        rollno = request.json.get('roll')
        student = Student.query.filter_by(rollno=rollno).first()

        if student:
            serialized_student = serialize_student(student)
            return jsonify(serialized_student)

    return jsonify({'message': 'Student not found'}), 404
        

@app.route('/department',methods=['POST','GET'])
def department():
    if request.method=="POST":
        dept=request.form.get('dept')
        query=Department.query.filter_by(branch=dept).first()
        if query:
            flash("Department Already Exist","warning")
            return redirect('/department')
        dep=Department(branch=dept)
        db.session.add(dep)
        db.session.commit()
        flash("Department Added","success")
    departments = [department.to_dict() for department in Department.query.all()]

    return jsonify(departments)


@app.route('/addattendance',methods=['POST','GET'])
def addattendance():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    if request.method=="POST":
        data = request.json
        rollno = data.get('rollno')
        attend = data.get('attend')
        print(attend,rollno)
        if rollno is not None and attend is not None:

            atte=Attendence(rollno=rollno,attendance=attend)
            db.session.add(atte)
            db.session.commit()
            flash("Attendance added","warning")
        else:
            flash("Invalid data provided for attendance", "danger")

        
    
    students = [serialize_sqlalchemy_obj(student) for student in Student.query.all()]

    return jsonify(students)


@app.route('/studentdetails')
def studentdetails():
    students=Student.query.all() 
    serialized_students = [serialize_student(student) for student in students]
    return jsonify(serialized_students)

@app.route("/delete/<string:id>", methods=['POST', 'GET'])
def delete(id):
    try:
        student = Student.query.get(id)
        if student:
            db.session.delete(student)
            db.session.commit()
            flash("Student Deleted Successfully", "success")
            return jsonify({'message': 'Student deleted successfully'})
        else:
            return jsonify({'message': 'Student not found'}), 404
    except Exception as e:
        print(f"Error deleting student: {e}")
        return jsonify({'message': 'Internal Server Error'}), 500



@app.route("/edit/<int:id>", methods=['GET'])
def get_student(id):
    student = Student.query.get(id)
    if student:
        return jsonify(serialize_student(student))
    else:
        return jsonify({'message': 'Student not found'}), 404

@app.route("/edit/<int:id>", methods=['POST'])
def update_student(id):
    rollno = request.json.get('rollno')
    sname = request.json.get('sname')
    sem = request.json.get('sem')
    gender = request.json.get('gender')
    branch = request.json.get('branch')
    email = request.json.get('email')
    num = request.json.get('num')
    address = request.json.get('address')

    student = Student.query.get(id)
    if student:
        student.rollno = rollno
        student.sname = sname
        student.sem = sem
        student.gender = gender
        student.branch = branch
        student.email = email
        student.num = num
        student.address = address

        db.session.commit()
        return jsonify({'message': 'Student updated successfully'})
    else:
        return jsonify({'message': 'Student not found'}), 404
    
@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid form data'})

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not (username and email and password):
            return jsonify({'message': 'Invalid form data'})

        user = User.query.filter_by(email=email).first()

        if user:
            return jsonify({'message': 'Email Already Exists'})

        encpassword = generate_password_hash(password)
        newuser = User(username=username, email=email, password=encpassword)
        db.session.add(newuser)
        db.session.commit()

        return jsonify({'message': 'User added successfully'})
    except json.JSONDecodeError:
        return jsonify({'message': 'Invalid JSON data'})
    

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
        else:
            flash("invalid credentials","danger")
        return jsonify({'message': 'User added successfully'})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return jsonify({'message': 'User added successfully'})



@app.route('/addstudent',methods=['POST','GET'])
#@login_required
def addstudent():
    if request.method == 'POST':
        data = request.json

        rollno = data.get('rollno')
        sname = data.get('sname')
        sem = data.get('sem')
        gender = data.get('gender')
        branch = data.get('branch')
        email = data.get('email')
        num = data.get('num')
        address = data.get('address')

        new_student = Student(rollno=rollno, sname=sname, sem=sem, gender=gender,
                              branch=branch, email=email, number=num, address=address)

        db.session.add(new_student)
        db.session.commit()

        flash("Added student details", "info")
        return jsonify({'message': 'Added student details'})


    
@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'


app.run(debug=True)    