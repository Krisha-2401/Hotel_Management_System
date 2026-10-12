HOTEL MANAGEMENT SYSTEM - PYTHON MINI PROJECT

Features
- Graphical user interface built with Tkinter
- SQLite database (created automatically)
- Room booking and room availability
- Guest booking records
- Cancel active bookings
- Check-out and bill calculation
- Room types and per-night rates

Requirements
- Python 3.10 or later recommended
- Tkinter is included with most standard Windows Python installations
- No pip packages are required

How to run in VS Code (Windows)
1. Extract Hotel_Management_System.zip.
2. Open the extracted folder in VS Code.
3. Make sure Python is installed. In the VS Code terminal, check:
   python --version
4. Run:
   python main.py
   If that command does not work, try:
   py main.py
5. The app window will open. The file hotel.db will be created automatically
   in the same folder after the first run.

Default room rates (per night)
- Single: Rs. 1,200
- Double: Rs. 2,000
- Deluxe: Rs. 3,000
- Suite: Rs. 5,000

Notes
- Enter dates in YYYY-MM-DD format.
- The checkout bill charges at least one night.
- This is a student/demo project; it is not intended for real hotel operations.
