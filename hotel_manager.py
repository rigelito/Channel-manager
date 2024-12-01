from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# Database setup
def init_db():
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number INTEGER,
            guest_name TEXT,
            start_date TEXT,
            end_date TEXT,
            UNIQUE(room_number, start_date, end_date)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Reservation model
class Reservation(BaseModel):
    room_number: int
    guest_name: str
    start_date: str
    end_date: str

@app.post("/reserve")
def reserve_room(reservation: Reservation):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO reservations (room_number, guest_name, start_date, end_date)
            VALUES (?, ?, ?, ?)
        """, (reservation.room_number, reservation.guest_name, reservation.start_date, reservation.end_date))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Room is already booked for this date range")
    finally:
        conn.close()
    return {"message": "Reservation successful", "reservation": reservation}

@app.get("/availability")
def check_availability(start_date: str, end_date: str):
    conn = sqlite3.connect("hotel.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT room_number FROM reservations
        WHERE NOT (end_date < ? OR start_date > ?)
    """, (start_date, end_date))
    booked_rooms = {row[0] for row in cursor.fetchall()}
    conn.close()

    available_rooms = [room for room in range(1, 11) if room not in booked_rooms]
    return {"available_rooms": available_rooms}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)