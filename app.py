import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Configure Flask and SQLAlchemy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'

# Check if running on Render (DATABASE_URL will be set in Render's environment variables)
database_url = os.getenv('DATABASE_URL')

# Log the database URL to debug the issue
print("DATABASE_URL:", database_url)

if database_url:
    # Use Render's external PostgreSQL database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgres://", "postgresql://", 1)
else:
    # Use Render's external database URL for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://rushi:yi73COKlyyUBFwRPclWqkBC8fgbyNzNH@dpg-cuereg5ds78s73fb0fe0-a.oregon-postgres.render.com/taskdb_x11i"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Database Models
class SchoolInfo(db.Model):
    school_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    num_boys = db.Column(db.Integer, nullable=False)
    num_girls = db.Column(db.Integer, nullable=False)

class Students(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school_info.school_id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    father_name = db.Column(db.String(100), nullable=False)
    mother_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.String(20), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

class StudentResponses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    Q1 = db.Column(db.Boolean, default=False)
    Q2 = db.Column(db.Boolean, default=False)
    Q3 = db.Column(db.Boolean, default=False)
    Q4 = db.Column(db.Boolean, default=False)
    Q5 = db.Column(db.Boolean, default=False)
    Q6 = db.Column(db.Boolean, default=False)
    Q7 = db.Column(db.Boolean, default=False)
    Q8 = db.Column(db.Boolean, default=False)
    Q9 = db.Column(db.Boolean, default=False)
    Q10 = db.Column(db.Boolean, default=False)
    Q11 = db.Column(db.Boolean, default=False)
    Q12 = db.Column(db.Boolean, default=False)
    Q13 = db.Column(db.Boolean, default=False)
    Q14 = db.Column(db.Boolean, default=False)
    Q15 = db.Column(db.Boolean, default=False)
    Q16 = db.Column(db.Boolean, default=False)
    Q17 = db.Column(db.Boolean, default=False)
    Q18 = db.Column(db.Boolean, default=False)
    Q19 = db.Column(db.Boolean, default=False)
    Q20 = db.Column(db.Boolean, default=False)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        school = request.form['school']
        num_boys = int(request.form['num_boys'])
        num_girls = int(request.form['num_girls'])

        school_info = SchoolInfo(name=name, school=school, num_boys=num_boys, num_girls=num_girls)
        db.session.add(school_info)
        db.session.commit()

        return redirect(url_for('student_entry', school_id=school_info.school_id))
    return render_template('index.html')

@app.route('/student_entry/<int:school_id>', methods=['GET', 'POST'])
def student_entry(school_id):
    if request.method == 'POST':
        students = request.form.getlist('full_name')
        for i in range(len(students)):
            student = Students(
                school_id=school_id,
                full_name=request.form.getlist('full_name')[i],
                father_name=request.form.getlist('father_name')[i],
                mother_name=request.form.getlist('mother_name')[i],
                dob=request.form.getlist('dob')[i],
                weight=float(request.form.getlist('weight')[i]),
                height=float(request.form.getlist('height')[i]),
                gender=request.form.getlist('gender')[i]
            )
            db.session.add(student)
        db.session.commit()
        return redirect(url_for('responses', school_id=school_id))
    return render_template('student_entry.html', school_id=school_id)

@app.route('/responses/<int:school_id>', methods=['GET', 'POST'])
def responses(school_id):
    students = Students.query.filter_by(school_id=school_id).all()

    if request.method == 'POST':
        for student in students:
            # Check if response exists for this student
            student_response = StudentResponses.query.filter_by(student_id=student.student_id).first()

            if not student_response:
                # Create new response
                student_response = StudentResponses(student_id=student.student_id)
                db.session.add(student_response)

            # Update each question's response
            for i in range(1, 21):
                checkbox_name = f'Q{i}_{student.student_id}'
                # Convert checkbox value to True/False in database
                checkbox_value = request.form.get(checkbox_name) == 'on'
                setattr(student_response, f'Q{i}', checkbox_value)

        db.session.commit()
        return redirect(url_for('index'))

    # Get existing responses
    student_responses = {sr.student_id: sr for sr in StudentResponses.query.all()}

    return render_template('responses.html', students=students, student_responses=student_responses)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
