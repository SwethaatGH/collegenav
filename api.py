import hashlib

import sqlite3
import hashlib
from datetime import datetime, timedelta

import uvicorn

from models import *
import dbOdin as dbodin

from fastapi import FastAPI, HTTPException


app = FastAPI()

API_PORT = 8000
ROUTER_PORT = 8001

# Create connection to SQLite database
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Register User
@app.post("/register_user")
async def register_user(user: User):
    # Check if user already exists
    c.execute("SELECT * FROM Users WHERE UserID = ?", (user.UserID,))
    if c.fetchone() is not None:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash user password
    password_hash = hashlib.sha256(user.UserPassword.encode()).hexdigest()
    
    # Insert new user into database
    c.execute("INSERT INTO Users VALUES (?, ?, ?, ?, ?, ?)",
              (user.UserID, user.UserType, password_hash, user.FName, user.LName, user.Contact))
    conn.commit()
    return {"message": "User registered successfully"}

# Login User
@app.post("/login_user")
async def login_user(user: UserLogin):
    # Retrieve hashed password for the given user
    c.execute("SELECT UserPassword FROM Users WHERE UserID = ?", (user.UserID,))
    result = c.fetchone()
    
    # Check if user exists and password is correct
    if result is None or hashlib.sha256(user.UserPassword.encode()).hexdigest() != result[0]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    c.execute("SELECT * FROM Users WHERE UserID = ?", (user.UserID,))
    result = c.fetchone()
    result_dict = dict(zip(('UserID', 'UserType', 'UserPassword', 'FName', 'LName', 'Contact'), result))
    result = User(**result_dict)
    return {"message": "User logged in successfully", "user":result.as_dict()}

# Reset Password
@app.put("/reset_password")
async def reset_password(user: UserLogin):
    # Check if user exists
    c.execute("SELECT * FROM Users WHERE UserID = ?", (user.UserID,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash new password
    password_hash = hashlib.sha256(user.UserPassword.encode()).hexdigest()
    
    # Update user's password in database
    c.execute("UPDATE Users SET UserPassword = ? WHERE UserID = ?", (password_hash, user.UserID))
    conn.commit()
    return {"message": "Password reset successfully"}

@app.get("/bookings")
async def get_bookings():
    query = "SELECT * FROM Bookings"
    c.execute(query)
    bookings = []
    for row in c.fetchall():
        myDict = dict(zip(("RoomID","User","ApprovedBy","Purpose","datetime"), row))
        myBooking = Booking(**myDict)
        bookings.append(myBooking.as_dict())
    return bookings

@app.get("/rooms")
async def get_rooms():
    query = "SELECT * FROM Rooms"
    c.execute(query)
    rooms = [Room(**dict(zip(("RoomID","BlockID","Waypoint","managerID"), row))).as_dict() for row in c.fetchall()]
    return rooms

@app.post("/rooms")
async def create_room(room_id: str, block_id: str, waypoint: str, manager_id: str):
    query = f"INSERT INTO Rooms (RoomID, BlockID, Waypoint, managerID) VALUES (?, ?, ?, ?)"
    conn.execute(query, (room_id, block_id, waypoint, manager_id))
    conn.commit()
    return {"message": "Room created successfully"}

@app.put("/rooms/{room_id}")
async def update_room(room_id: str, block_id: str, waypoint: str, manager_id: str):
    query = f"UPDATE Rooms SET BlockID=?, Waypoint=?, managerID=? WHERE RoomID=?"
    conn.execute(query, (block_id, waypoint, manager_id, room_id))
    conn.commit()
    return {"message": "Room updated successfully"}

@app.delete("/rooms/{room_id}")
async def delete_room(room_id: str):
    query = f"DELETE FROM Rooms WHERE RoomID=?"
    conn.execute(query, (room_id,))
    conn.commit()
    return {"message": "Room deleted successfully"}

@app.get("/available_rooms")
async def get_available_rooms(datentime: str):
    datentime = datetime.strptime(datentime, "%Y-%m-%d %H:%M")
    grace_time = timedelta(minutes=30)
    start_time = datentime - grace_time
    end_time = datentime + grace_time

    # Get all bookings within grace time of datetime
    query = "SELECT * FROM Bookings WHERE datetime BETWEEN ? AND ?"
    c.execute(query, (start_time, end_time))
    bookings = []
    for row in c.fetchall():
        myDict = dict(zip(("RoomID","User","ApprovedBy","Purpose","datetime"), row))
        myBooking = Booking(**myDict)
        bookings.append(myBooking.as_dict())

    # Get all rooms
    query = "SELECT * FROM Rooms"
    c.execute(query)
    rooms = [Room(**dict(zip(("RoomID","BlockID","Waypoint","managerID"), row))).as_dict() for row in c.fetchall()]

    # Find all rooms that are available for booking
    available_rooms = []
    for room in rooms:
        is_available = True
        for booking in bookings:
            if booking.get("RoomID") == room.get("RoomID"):
                is_available = False
                break
        if is_available:
            available_rooms.append(room)
    
    return available_rooms

# Request Room Booking (User)
@app.post("/request_booking")
async def request_booking(booking: Booking):
    # Check if room exists
    c.execute("SELECT * FROM Rooms WHERE RoomID = ?", (booking.RoomID,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Insert booking request into database
    c.execute("INSERT INTO Bookings VALUES (?, ?, '', ?, ?)",
              (booking.RoomID, booking.User, booking.Purpose, booking.datetime))
    conn.commit()
    return {"message": "Booking requested successfully"}

# Approve Room Booking (BlockAdmin/Superadmin)
@app.put("/approve_booking")
async def approve_booking(RoomID: str, User: str, ApprovedBy: str):
    # Check if room and user exists
    c.execute("SELECT * FROM Rooms WHERE RoomID = ?", (RoomID,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    c.execute("SELECT * FROM Users WHERE UserID = ?", (User,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if approving user has permission
    c.execute("SELECT UserType, BlockID FROM Users JOIN Rooms ON Users.UserID = Rooms.managerID WHERE RoomID = ?", (RoomID,))
    result = c.fetchone()
    
    # Approve booking in database
    c.execute("UPDATE Bookings SET ApprovedBy = ? WHERE RoomID = ? AND User = ?", (ApprovedBy, RoomID, User))
    conn.commit()
    return {"message": "Booking approved successfully"}

# Delete Room Booking (BlockAdmin/Superadmin)
@app.delete("/delete_booking")
async def delete_booking(RoomID: str, User: str, DeletedBy: str):
    # Check if room and user exists
    c.execute("SELECT * FROM Rooms WHERE RoomID = ?", (RoomID,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="Room not found")
    
    c.execute("SELECT * FROM Users WHERE UserID = ?", (User,))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if deleting user has permission
    c.execute("SELECT UserType, BlockID FROM Users JOIN Rooms ON Users.UserID = Rooms.managerID WHERE RoomID = ?", (RoomID,))
    result = c.fetchone()

    # Delete booking from database
    c.execute("DELETE FROM Bookings WHERE RoomID = ? AND User = ?", (RoomID, User))
    conn.commit()
    return {"message": "Booking deleted successfully"}

# Delete My Room Booking Request (User)
@app.delete("/delete_my_booking")
async def delete_my_booking(booking: Booking):
    # Check if booking exists and user matches
    c.execute("SELECT * FROM Bookings WHERE RoomID = ? AND User = ?", (booking.RoomID, booking.User))
    if c.fetchone() is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Delete booking from database
    c.execute("DELETE FROM Bookings WHERE RoomID = ? AND User = ?", (booking.RoomID, booking.User))
    conn.commit()
    return {"message": "Booking deleted successfully"}

# CRUD operations for Waypoints
@app.post("/waypoints/")
def create_waypoint(waypoint_id: str, lat:str, lon:str):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Insert new waypoint into the database
    try:
        c.execute("INSERT INTO Waypoints (WaypointID, latitude, longitude) VALUES (?, ?, ?)",
                  (waypoint_id.upper(), lat, lon))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Waypoint with this ID already exists.")
    
    return {"message": "Waypoint created successfully."}

@app.get("/waypoints/")
def read_all_waypoints():

    # Get all waypoints from the database

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT WaypointID, latitude, longitude FROM Waypoints")
    waypoints = [{"WaypointID": row[0], "latitude": row[1], "longitude": row[2]} for row in c.fetchall()]
    
    return {"waypoints": waypoints}

@app.put("/waypoints/{waypoint_id}")
def update_waypoint(waypoint_id: str, lat:str, lon:str):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Update the waypoint in the database
    try:
        c.execute("UPDATE Waypoints SET latitude = ?, longitude = ? WHERE WaypointID = ?",
                  (lat, lon, waypoint_id.upper()))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Waypoint with this ID already exists.")
    
    return {"message": "Waypoint updated successfully."}

@app.delete('/waypoints/{waypoint_id}')
async def delete_waypoint(waypoint_id: str):

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM Waypoints WHERE WaypointID=?", (waypoint_id,))
    result = c.fetchone()
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Waypoint not found")
    c.execute("DELETE FROM Waypoints WHERE WaypointID=?", (waypoint_id,))
    conn.commit()
    return {"msg": "Waypoint deleted successfully."}

if __name__ == '__main__':

    #Create connection to SQLite database
    #conn = sqlite3.connect('database.db')
    #c = conn.cursor()

    #dbodin.CreateTables(conn, c)
    #dbodin.InsertSampleData(conn, c)

    uvicorn.run(app, host='0.0.0.0', port=API_PORT)
