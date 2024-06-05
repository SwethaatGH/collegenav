from pydantic import BaseModel
from enum import Enum

class UserType(str, Enum):
    User = 'User'
    BlockAdmin = 'BlockAdmin'
    SuperAdmin = 'SuperAdmin'

class Waypoint(BaseModel):
    WaypointID: str
    latitude: float
    longitude: float
    def as_dict(self):
        return {
            "WaypointID": self.WaypointID,
            "latitude": self.latitude,
            "longitude": self.longitude
        }

class User(BaseModel):
    UserID: str
    UserType: UserType
    UserPassword: str
    FName: str
    LName: str
    Contact: str
    def as_dict(self):
        return {
            "UserID": self.UserID,
            "UserType": self.UserType,
            "UserPassword": self.UserPassword,
            "FName": self.FName,
            "LName": self.LName,
            "Contact": self.Contact
        }

class UserLogin(BaseModel):
    UserID: str
    UserPassword: str
    def as_dict(self):
        return {
            "UserID" : self.UserID,
            "UserPassword" : self.UserPassword
        }

class Room(BaseModel):
    RoomID: str
    BlockID: str
    Waypoint: str
    managerID: str
    def as_dict(self):
        return {
            "RoomID": self.RoomID,
            "BlockID": self.BlockID,
            "Waypoint": self.Waypoint,
            "managerID": self.managerID
        }

class Booking(BaseModel):
    RoomID: str
    User: str
    ApprovedBy: str
    Purpose: str
    datetime: str
    def as_dict(self):
        return {
            "RoomID": self.RoomID,
            "User": self.User,
            "ApprovedBy": self.ApprovedBy,
            "Purpose": self.Purpose,
            "datetime": self.datetime
        }