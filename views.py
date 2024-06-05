from flask import Flask, render_template, request, session, redirect, url_for
import requests, json

from functools import wraps
from datetime import datetime

def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            json.loads(session.get("user"))
            return func(*args, **kwargs)
        except Exception as e:
            print("UN LOGGEDIN", e)
            return redirect(url_for('login'))
    return decorated_view

router = Flask(__name__, template_folder='pages')

router.config['SECRET_KEY'] = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"

API_PORT = 8000
ROUTER_PORT = 8001

@router.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        resp = requests.post(f"http://localhost:{API_PORT}/register_user", json={
                                                                              "UserID": request.form.get("userID"),
                                                                              "UserType": request.form.get("userType"),
                                                                              "UserPassword": request.form.get("password"),
                                                                              "FName": request.form.get("firstName"),
                                                                              "LName": request.form.get("lastName"),
                                                                              "Contact": request.form.get("contact")
                                                                            })
        try:
            if resp.json().get("message") == "User registered successfully":
                return redirect(url_for('login'))
            else:
                return resp.text
                raiseAnExceptionBecauseIDontExist()
        except Exception as e:
            return f'{e}'
    return render_template('register.html')

@router.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        resp = requests.post(f"http://localhost:{API_PORT}/login_user", json={"UserID":request.form.get("userID"),
                                                                             "UserPassword":request.form.get("pwd")})
        try:
            if resp.json().get("message") == "User logged in successfully":
                session['user'] = json.dumps(resp.json().get('user'))
                return redirect(url_for('dashboard'))
            else:
                return resp.text
                raiseAnExceptionBecauseIDontExist()
        except Exception as e:
            return f'{e}'
    return render_template('login.html')

@router.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method=='POST':
        resp = requests.put(f"http://localhost:{API_PORT}/reset_password", json={"UserID":request.form.get("userID"),
                                                                             "UserPassword":request.form.get("pwd")})
        try:
            if resp.json().get("message") == "Password reset successfully":
                return redirect(url_for('login'))
            else:
                return resp.text
                raiseAnExceptionBecauseIDontExist()
        except Exception as e:
            return f'{e}'
    return render_template('reset_password.html')

@router.route('/dashboard')
@login_required
def dashboard():
    user = json.loads(session.get("user"))
    myBookings = []
    bookings = requests.get(f"http://localhost:{API_PORT}/bookings").json()
    for i in bookings:
        if i["User"] == user.get("UserID"):
            myBookings.append(i)
    avblRooms = requests.get(f"http://localhost:{API_PORT}/available_rooms?datentime={datetime.now().strftime('%Y-%m-%d %H:%M')}").json()
    return render_template("dashboard.html", user=user, user_bookings=myBookings, available_rooms=avblRooms)

@router.route('/book-a-room', methods=['GET', 'POST'])
@login_required
def book_room():
    user = json.loads(session.get("user"))
    if request.method=='POST':
        resp = requests.post(f"http://localhost:{API_PORT}/request_booking", json={
                                                                              "RoomID": request.form.get("roomId"),
                                                                              "User": user.get("UserID"),
                                                                              "ApprovedBy": "None",
                                                                              "Purpose": request.form.get("purpose"),
                                                                              "datetime": request.form.get("dateTime")
                                                                            })
        try:
            if resp.json().get("message") == "Booking requested successfully":
                return redirect(url_for('dashboard'))
            else:
                return resp.text
                raiseAnExceptionBecauseIDontExist()
        except Exception as e:
            return f'{e}'
    user = json.loads(session.get("user"))
    myBookings = []
    bookings = requests.get(f"http://localhost:{API_PORT}/bookings").json()
    for i in bookings:
        if i["User"] == user.get("UserID"):
            myBookings.append(i)
    avblRooms = requests.get(f"http://localhost:{API_PORT}/available_rooms?datentime={datetime.now().strftime('%Y-%m-%d %H:%M')}").json()
    return render_template("book_a_room.html", user=user, user_bookings=myBookings, available_rooms=avblRooms)


@router.route('/view-requests', methods=['GET', 'POST'])
@login_required
def view_requests():
    user = json.loads(session.get("user"))
    if request.method=='POST':
        if request.form.get("action")=="Approve":
            print({
                  "RoomID": request.form.get("RoomID"),
                  "User": request.form.get("UserID"),
                  "ApprovedBy": user.get("UserID")
                })
            resp = requests.put(f"http://localhost:{API_PORT}/approve_booking", params={
                                                                              "RoomID": request.form.get("RoomID"),
                                                                              "User": request.form.get("UserID"),
                                                                              "ApprovedBy": user.get("UserID")
                                                                            })
            print(resp.text)
        if request.form.get("action")=="Disapprove":
            resp = requests.delete(f"http://localhost:{API_PORT}/delete_booking", params={
                                                                              "RoomID": request.form.get("RoomID"),
                                                                              "User": request.form.get("UserID"),
                                                                              "DeletedBy": user.get("UserID")
                                                                            })
    bookings = requests.get(f"http://localhost:{API_PORT}/bookings").json()
    user_bookings = []
    for i in bookings:
        if i["ApprovedBy"]=="":
            user_bookings.append(i)
    return render_template("view_requests.html", user=user, user_bookings=user_bookings)

@router.route('/crud-rooms', methods=['GET', 'POST'])
@login_required
def crud_rooms():
    user = json.loads(session.get("user"))
    if request.method=='POST':
        action = "C"
        roomID = request.form.get("RoomID")
        if request.form.get("managerID") in (None, "", " ", 0):
            action = "D"
        else:
            rooms = requests.get(f"http://localhost:{API_PORT}/rooms").json()
            for i in rooms:
                if i.get("RoomID") == roomID:
                    print(i.get("RoomID") == roomID,i.get("RoomID"), roomID)
                    action = "U"
        if action=="C":
            resp = requests.post(f"http://localhost:{API_PORT}/rooms", params={
                                                                              "room_id": request.form.get("RoomID"),
                                                                              "block_id": request.form.get("BlockID"),
                                                                              "waypoint": request.form.get("Waypoint"),
                                                                              "manager_id": request.form.get("managerID")
                                                                            })
            try:
                if resp.json().get("message") == "Room created successfully":
                    return redirect(url_for('crud_rooms'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

        if action=="U":
            resp = requests.put(f"http://localhost:{API_PORT}/rooms/{request.form.get('RoomID')}", params={
                                                                              "room_id": request.form.get("RoomID"),
                                                                              "block_id": request.form.get("BlockID"),
                                                                              "waypoint": request.form.get("Waypoint"),
                                                                              "manager_id": request.form.get("managerID")
                                                                            })
            try:
                if resp.json().get("message") == "Room updated successfully":
                    return redirect(url_for('crud_rooms'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

        if action=="D":
            resp = requests.delete(f"http://localhost:{API_PORT}/rooms/{request.form.get('RoomID')}", params={
                                                                              "room_id": request.form.get("RoomID")
                                                                            })
            try:
                if resp.json().get("message") == "Room deleted successfully":
                    return redirect(url_for('crud_rooms'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

    rooms = requests.get(f"http://localhost:{API_PORT}/rooms").json()
    return render_template("crud_rooms.html", user=user, rooms=rooms)


@router.route('/crud-waypoints', methods=['GET', 'POST'])
@login_required
def crud_waypoints():
    user = json.loads(session.get("user"))
    if request.method=='POST':
        action = "C"
        waypointID = request.form.get("Waypoint")
        if request.form.get("longitude") in (None, "", " ", 0):
            action = "D"
        else:
            waypoints = requests.get(f"http://localhost:{API_PORT}/waypoints").json().get('waypoints')
            for i in waypoints:
                if i.get("WaypointID") == str(waypointID).strip():
                    action = "U"
        print(dict(request.form), action)
        if action=="C":
            resp = requests.post(f"http://localhost:{API_PORT}/waypoints", params={
                                                                              "waypoint_id": request.form.get("WaypointID"),
                                                                              "lat": request.form.get("latitude"),
                                                                              "lon": request.form.get("longitude")
                                                                            })
            try:
                if resp.json().get("message") == "Waypoint created successfully.":
                    return redirect(url_for('crud_waypoints'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

        if action=="U":
            resp = requests.put(f"http://localhost:{API_PORT}/waypoints/{request.form.get('Waypoint')}", params={
                                                                              "waypoint_id": request.form.get("Waypoint"),
                                                                              "lat": request.form.get("latitude"),
                                                                              "lon": request.form.get("longitude")
                                                                            })
            try:
                if resp.json().get("message") == "Waypoint updated successfully.":
                    return redirect(url_for('crud_waypoints'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

        if action=="D":
            resp = requests.delete(f"http://localhost:{API_PORT}/waypoints/{request.form.get('Waypoint')}", params={
                                                                              "waypoint_id": request.form.get("Waypoint")
                                                                            })
            try:
                if resp.json().get("msg") == "Waypoint deleted successfully.":
                    return redirect(url_for('crud_waypoints'))
                else:
                    return resp.text
                    raiseAnExceptionBecauseIDontExist()
            except Exception as e:
                return f'{e}'

    waypoints = requests.get(f"http://localhost:{API_PORT}/waypoints").json().get('waypoints')
    return render_template("crud_waypoints.html", user=user, waypoints=waypoints)

@router.route('/maps')
@login_required
def maps():
    user = json.loads(session.get("user"))
    waypoints = requests.get(f"http://localhost:{API_PORT}/waypoints").json().get('waypoints')
    return render_template("map.html", user=user, waypoints=list(waypoints))

@router.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    
    router.run(host='0.0.0.0',
               port=ROUTER_PORT,
               debug=True)