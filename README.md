# College Navigation and Classroom Booking
This web application has been developed to help students and admins of colleges to manage classroom booking. It also helps students navigate through their college campus through map and waypoints support. 

## Roles

1. Superadmin can create (or delete) waypoints in maps for facilitating easy navigation and can also add (or delete) classrooms.
2. Block admins can approve or reject booking requests from students for classrooms and conference halls.
3. Students can view waypoints, put forward booking requests and know the status of their requests (approved, rejected or pending).

## Tech Stack Used

Application uses Python (FastAPI, Flask, Pydantic) for frontend and SQLite for backend

### Code Structure
1. models.py: This file contains the Pydantic models for the various objects in the project, including users, rooms, bookings and waypoints.
2. api.py: This file contains the API endpoints and the connection to the SQLite database.
3. dbOdin.py: This file contains functions to create and populate the SQLite database.
4. views.py: This file contains functions to render HTML pages for the user to view.

### Models
The following Pydantic models are used
● User: Contains information about a user, including their ID, user type, password, first name, last name and contact information.
● UserType: An enum that represents different types of users.
● UserLogin: Contains the user ID and password for a user.
● Room: Contains information about a room, including the room ID, block ID, waypoint and manager ID.
● Booking: Contains information about a room booking, including the room ID, user ID, approved by, purpose and date/time.
● Waypoint: Contains information about a waypoint, including the waypoint ID, latitude and longitude.

### API
The API is built using FastAPI and the auto-generated documentation can be accessed at when the app is run.

### SQLite Database
The database is created and populated using the dbOdin.py script.
The following tables are used in the database
● Waypoints: Contains information about the different waypoints on campus.
● Users: Contains information about the users in the system.
● Rooms: Contains information about the different rooms on campus.
● Bookings: Contains information about the bookings made for each room.

### Installation
Clone the project but ensure the following directory structure within your folder: add all HTML files inside a "pages" sub-folder; add all CSS files inside a "static" sub-folder; add rest all files under the main folder itself.
To run this project, follow these steps
1. Install the required dependencies using the command ```pip install -r requirements.txt```
2. Create and populate the SQLite database using the dbOdin.py script. Call the two functions available in the file.
3. Run the api.py script using the command python api.py
4. Access the API endpoints using a tool like curl or a web browser.
5. Run the views.py script using the command python views.py
6. Once the server is running, you can access it in your web browser by navigating to http://localhost:8001/login or http://localhost:8001/register.

### Viewing the SQLite Database
To view the SQLite database, an online database viewer like (SQLite Online) can be used. Upload the database.db file to the website to view the contents of the database.

![Screenshot 2024-06-05 at 11 40 25 PM](https://github.com/SwethaatGH/collegenav/assets/98175379/3d1c4e23-d8be-4e71-8db7-f4d5ce9ab529)
![Screenshot 2024-06-05 at 11 40 07 PM](https://github.com/SwethaatGH/collegenav/assets/98175379/5d096761-8cd1-49ad-82e5-bf65382ef880)
![Screenshot 2024-06-05 at 11 40 55 PM](https://github.com/SwethaatGH/collegenav/assets/98175379/73e97997-6f9d-4b1d-8ea7-ac62b95e1639)
![Screenshot 2024-06-05 at 11 40 38 PM](https://github.com/SwethaatGH/collegenav/assets/98175379/2caa7aaa-74d8-4efe-9963-743538209b08)

