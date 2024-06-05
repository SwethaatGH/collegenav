import hashlib

# Create tables
def CreateTables(conn, c):
    c.execute('''CREATE TABLE Waypoints
                 (WaypointID varchar(5) PRIMARY KEY,
                  latitude float,
                  longitude float)''')

    c.execute('''CREATE TABLE Users
                 (UserID varchar(10) PRIMARY KEY,
                  UserType varchar(20),
                  UserPassword varchar(50),
                  FName varchar(20),
                  LName varchar(20),
                  Contact varchar(20))''')

    c.execute('''CREATE TABLE Rooms
                 (RoomID varchar(5) PRIMARY KEY,
                  BlockID varchar(1),
                  Waypoint varchar(5),
                  managerID varchar(10),
                  FOREIGN KEY (Waypoint) REFERENCES Waypoints(WaypointID),
                  FOREIGN KEY (managerID) REFERENCES Users(UserID))''')

    c.execute('''CREATE TABLE Bookings
                 (RoomID varchar(5),
                  User varchar(10),
                  ApprovedBy varchar(10),
                  Purpose varchar(250),
                  datetime varchar(20),
                  PRIMARY KEY (RoomID, User),
                  FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
                  FOREIGN KEY (User) REFERENCES Users(UserID),
                  FOREIGN KEY (ApprovedBy) REFERENCES Users(UserID))''')
    conn.commit()

# Insert sample data
def InsertSampleData(conn, c):

    c.execute("INSERT INTO Waypoints VALUES ('A Block', 11.0237, 77.0028)")
    c.execute("INSERT INTO Waypoints VALUES ('B Block', 11.0257, 77.0024)")
    c.execute("INSERT INTO Waypoints VALUES ('C Block', 11.0248, 77.0026)")

    password_hash = hashlib.sha256(b"password").hexdigest()
    c.execute("INSERT INTO Users VALUES ('USER001', 'User', ?, 'John', 'Doe', '1234567890')", (password_hash,))
    c.execute("INSERT INTO Users VALUES ('BA001', 'BlockAdmin', ?, 'Jane', 'Doe', '0987654321')", (password_hash,))
    c.execute("INSERT INTO Users VALUES ('SA001', 'SuperAdmin', ?, 'Admin', 'User', '9876543210')", (password_hash,))

    c.execute("INSERT INTO Rooms VALUES ('ROOM001', 'B', 'A Block', 'BA001')")
    c.execute("INSERT INTO Rooms VALUES ('ROOM002', 'A', 'B Block', 'SA001')")
    c.execute("INSERT INTO Rooms VALUES ('ROOM003', 'C', 'C Block', 'BA001')")

    c.execute("INSERT INTO Bookings VALUES ('ROOM001', 'USER001', 'BA001', 'Meeting', '2023-05-01')")

    conn.commit()