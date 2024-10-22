from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rooms.db'  # ใช้ SQLite สำหรับฐานข้อมูล
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='room', lazy=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String, nullable=False)  # ใช้ string สำหรับวันที่

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_id = int(request.form['room_id'])
        capacity = int(request.form['capacity'])
        
        existing_room = db.session.query(Room).filter_by(room_id=room_id).first()
        if existing_room:
            print(f"ห้อง {room_id} มีอยู่แล้วในฐานข้อมูล")
            return redirect(url_for('add_room'))
        
        new_room = Room(room_id=room_id, capacity=capacity)
        db.session.add(new_room)
        db.session.commit()
        print(f"เพิ่มห้อง {room_id} สำเร็จ")
        return redirect(url_for('index'))

    return render_template('add_room.html')

@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    if request.method == 'POST':
        room_id = int(request.form['room_id'])
        start_time = int(request.form['start_time'])
        end_time = int(request.form['end_time'])
        date = request.form['date']

        room = Room.query.filter_by(room_id=room_id).first()
        if room:
            for booking in room.bookings:
                if booking.date == date and not (end_time <= booking.start_time or start_time >= booking.end_time):
                    return "ห้องเรียนไม่ว่างในเวลานี้!"

            new_booking = Booking(room_id=room_id, start_time=start_time, end_time=end_time, date=date)
            db.session.add(new_booking)
            db.session.commit()
            return "จองห้องเรียนสำเร็จ!"
    return render_template('book_room.html')

@app.route('/check_availability', methods=['GET', 'POST'])
def check_availability():
    available_rooms = []
    date = None
    if request.method == 'POST':
        date = request.form['date']
        all_rooms = Room.query.all()

        for room in all_rooms:
            is_available = True
            for booking in room.bookings:
                if booking.date == date and not (booking.end_time <= 0 or booking.start_time >= 24):
                    is_available = False
                    break
            if is_available:
                available_rooms.append(room)

    return render_template('check_availability.html', available_rooms=available_rooms, date=date)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
