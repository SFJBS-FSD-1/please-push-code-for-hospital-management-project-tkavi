from flask import Flask,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

class Config():
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/hospital'

class Development_Config(Config):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://root:1234@localhost/hospital'

class Production_Config(Config):
    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://","postgresql://",1)
    SQLALCHEMY_DATABASE_URI = uri

env = os.environ.get("ENV","Development")

if env == "Production":
    config_str = Production_Config
else:
    config_str = Development_Config

app = Flask(__name__)
app.config.from_object(config_str)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:welcome$1234@localhost/hospital'
db = SQLAlchemy(app)
migrate = Migrate(app,db)

class Patient(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(80),  nullable = False)
    phone_number = db.Column(db.String(20), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    address = db.Column(db.String(150), nullable = False)
    state = db.Column(db.String(50),  nullable = False)
    city = db.Column(db.String(50), nullable=False)
    patient_status = db.Column(db.String(20), nullable = True)
    bed_type = db.Column(db.String(20), nullable=True)

class Medicine(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    medicine_name = db.Column(db.String(150),  nullable = False)
    quantity = db.Column(db.Integer, nullable = False)
    rate = db.Column(db.String(50), nullable = False)

def get_patients():
    patients = Patient.query.all()
    patients_list = []
    for patient in patients:
        dict = {}
        dict['id'] = patient.id
        dict['name'] = patient.name
        dict['phone'] = patient.phone_number
        dict['age'] = patient.age
        dict['address'] = patient.address
        dict['state'] = patient.state
        dict['city'] = patient.city
        dict['status'] = patient.patient_status
        dict['bed'] = patient.bed_type
        patients_list.append(dict)
    return patients_list

def patient_data():
    phone = request.form["phone"]
    patient = Patient.query.filter_by(phone_number=phone).first()
    patient_data ={}
    if patient:
        patient_data = {'id': patient.id, 'name': patient.name, 'phone': patient.phone_number,
                        'age': patient.age, 'address': patient.address,
                        'state': patient.state, 'city': patient.city,
                        'status': patient.patient_status, 'bed': patient.bed_type
                        }
    return patient_data

@app.route('/',methods=['GET'])
def home_page():
    return render_template("home.html")

@app.route('/register_patient',methods=['GET','POST'])
def register_patient():
    if request.method == "GET":
        return render_template("patient.html")

    if request.method == "POST":
        name = request.form["name"]
        phone_no = request.form["phone"]
        age = request.form["age"]
        address = request.form["address"]
        state = request.form["state"]
        city = request.form["city"]
        patient_status = request.form["status"]
        bed_type = request.form["bed"]

        patient = Patient.query.filter_by(phone_number=phone_no).first()
        if patient:
            return render_template("patient.html",msg = "Patient already registered")
        else:
            new_patient = Patient(name=name, phone_number=phone_no, age=age, address=address, state=state, city=city,
                                  patient_status=patient_status, bed_type=bed_type)
            db.session.add(new_patient)
            db.session.commit()
            return render_template("patient.html",patient = name)

@app.route('/getAllPatients',methods=['GET'])
def patinets_list():
    if request.method == 'GET':
        patients_list = get_patients()
        return render_template("patientList.html",patient = patients_list)

@app.route('/getActivePatients',methods=['GET'])
def active_patients():
    if request.method == 'GET':
        patients_list = get_patients()
        active_patients = []

        for patient in patients_list:
            if patient['status'] == 'Active':
                active_patients.append(patient)
        return render_template("patientList.html", patient=active_patients)

@app.route('/getPatient',methods=['GET'])
def patient_details():
    if request.method == 'GET':
        return render_template("patientById.html")

@app.route('/getPatientByPhone', methods=['GET','POST'])
def patient_by_Id():
    if request.method == 'POST':
        patient_dtls = patient_data()
        if patient_dtls:
            return render_template("patientById.html",data=patient_dtls)
        else:
            return render_template("patientById.html", msg="Patient not Found")

@app.route('/patient/update', methods=['POST'])
def patient_update():
    if request.method == 'POST':
        patient_dtls = patient_data()
        if patient_dtls:
            return render_template("patientById.html", update_msg=patient_dtls)
        else:
            return render_template("patientById.html", msg="Patient not Found")

@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address=request.form['address']
        state=request.form['state']
        city=request.form['city']
        age=request.form['age']
        patient_status=request.form['status']
        bed_type=request.form['bed']

        update_patient = Patient(name=name,phone_number=phone,address=address,state=state,city=city,age=age,patient_status=patient_status,bed_type=bed_type)
        patient_data = {'name': update_patient.name, 'phone_number': update_patient.phone_number,
                        'age': update_patient.age, 'address': update_patient.address,
                        'state': update_patient.state, 'city': update_patient.city,
                        'patient_status': update_patient.patient_status, 'bed_type': update_patient.bed_type
                        }
        Patient.query.filter_by(phone_number=phone).update(patient_data)
        db.session.commit()
        return render_template("patientById.html", update=patient_data)

@app.route('/patient/delete', methods=['GET','POST'])
def patient_delete():
    if request.method == 'POST':
        phone = request.form["phone"]
        patient = Patient.query.filter_by(phone_number=phone).first()
        if patient:
            Patient.query.filter_by(phone_number=phone).delete()
            db.session.commit()
            return render_template("patientById.html", msg = patient.name+" deleted successfully")
        else:
            return render_template("patientById.html", msg = "Patient not found")

@app.route('/register_medicine',methods=['GET','POST'])
def register_medicine():
    if request.method == "GET":
        return render_template("medicine.html")

    if request.method == "POST":
        medicine_name = request.form["name"]
        quantity = request.form["qty"]
        rate = request.form["rate"]

        medicine = Medicine.query.filter_by(medicine_name=medicine_name).first()
        if medicine:
            return render_template("medicine.html", msg="Medicine already registered")
        else:
            new_medicine = Medicine(medicine_name=medicine_name,quantity=quantity,rate=rate)
            db.session.add(new_medicine)
            db.session.commit()
            return render_template("medicine.html", medicine=medicine_name)

@app.route('/getAllMedicines',methods=['GET'])
def medicines_list():
    if request.method == 'GET':
        medicines = Medicine.query.all()
        medicines_list=[]
        for medicine in medicines:
            dict={}
            dict['id']= medicine.id
            dict['name'] = medicine.medicine_name
            dict['qty'] = medicine.quantity
            dict['rate'] = medicine.rate
            medicines_list.append(dict)
        return render_template("medicineList.html",medicine = medicines_list)

@app.route('/getMedicine',methods=['GET'])
def medicine_details():
    if request.method == 'GET':
        return render_template("medicineById.html")

@app.route('/getMedicineById', methods=['GET','POST'])
def medicine_by_Id():
    if request.method == 'POST':
        id = request.form['id']
        medicine = Medicine.query.filter_by(id=id).first()

        if medicine:
            medicine_data = {'id': medicine.id, 'name': medicine.medicine_name,
                             'qty': medicine.quantity, 'rate': medicine.rate}
            return render_template("medicineById.html",data=medicine_data)
        else:
            return render_template("medicineById.html", msg="Medicine not Found")

@app.route('/updateMedicine', methods=['POST'])
def medicine_update():
    if request.method == 'POST':
        id = request.form['id']
        medicine = Medicine.query.filter_by(id=id).first()

        if medicine:
            medicine_data = {'id': medicine.id, 'name': medicine.medicine_name,
                             'qty': medicine.quantity, 'rate': medicine.rate}

            return render_template("medicineById.html", update_msg =medicine_data)
        else:
            return render_template("medicineById.html", msg="Medicine not Found")

@app.route('/update_med', methods=['POST'])
def update_med():
    if request.method == 'POST':
        id = request.form['id']
        medicine_name = request.form['name']
        quantity = request.form['qty']
        rate=request.form['rate']

        update_medicine = Medicine(id=id,medicine_name=medicine_name, quantity=quantity, rate=rate)
        medicine_data = {'id': update_medicine.id, 'medicine_name': update_medicine.medicine_name,
                           'quantity': update_medicine.quantity, 'rate': update_medicine.rate}
        Medicine.query.filter_by(id=id).update(medicine_data)
        db.session.commit()
        return render_template("medicineById.html", update=medicine_data)

@app.route('/deleteMedicine', methods=['GET','POST'])
def medicine_delete():
    if request.method == 'POST':
        id = request.form["id"]
        medicine = Medicine.query.filter_by(id=id).first()
        medicine_name=medicine.medicine_name

        if medicine:
            Medicine.query.filter_by(id=id).delete()
            db.session.commit()
            return render_template("medicineById.html", msg = medicine_name+" deleted successfully")
        else:
            return render_template("medicineById.html", msg = "Medicine not found")

if __name__ == "__main__":
    app.run()