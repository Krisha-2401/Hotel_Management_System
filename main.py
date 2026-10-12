import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date

DB_NAME = "hotel.db"

ROOM_RATES = {
    "Single": 1200,
    "Double": 2000,
    "Deluxe": 3000,
    "Suite": 5000,
}

def connect_db():
    return sqlite3.connect(DB_NAME)

def initialize_db():
    with connect_db() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                room_no INTEGER NOT NULL,
                room_type TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT,
                status TEXT NOT NULL DEFAULT 'Booked',
                bill REAL DEFAULT 0
            )
        """)
        # Seed a fixed set of rooms only when the rooms table is empty.
        con.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_no INTEGER PRIMARY KEY,
                room_type TEXT NOT NULL
            )
        """)
        count = con.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
        if count == 0:
            rooms = []
            for number in range(101, 111):
                rooms.append((number, "Single"))
            for number in range(201, 211):
                rooms.append((number, "Double"))
            for number in range(301, 306):
                rooms.append((number, "Deluxe"))
            for number in range(401, 404):
                rooms.append((number, "Suite"))
            con.executemany("INSERT INTO rooms(room_no, room_type) VALUES (?, ?)", rooms)

def available_rooms(room_type):
    with connect_db() as con:
        rows = con.execute("""
            SELECT room_no FROM rooms
            WHERE room_type = ?
            AND room_no NOT IN (
                SELECT room_no FROM bookings WHERE status = 'Booked'
            )
            ORDER BY room_no
        """, (room_type,)).fetchall()
    return [str(row[0]) for row in rows]

class HotelManagementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System")
        self.root.geometry("1050x680")
        self.root.minsize(900, 600)
        self.root.configure(bg="#f3f6fb")
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", rowheight=27, font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        self.build_ui()
        self.refresh_bookings()
        self.update_room_choices()

    def build_ui(self):
        header = tk.Frame(self.root, bg="#16324f", height=78)
        header.pack(fill="x")
        tk.Label(header, text="HOTEL MANAGEMENT SYSTEM", bg="#16324f",
                 fg="white", font=("Segoe UI", 20, "bold")).pack(pady=(12, 0))
        tk.Label(header, text="Python • Tkinter • SQLite", bg="#16324f",
                 fg="#d6e6f5", font=("Segoe UI", 10)).pack(pady=(0, 10))

        main = tk.Frame(self.root, bg="#f3f6fb", padx=18, pady=14)
        main.pack(fill="both", expand=True)

        form = tk.LabelFrame(main, text="New Room Booking", bg="white",
                             font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        form.pack(fill="x", pady=(0, 12))

        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.type_var = tk.StringVar(value="Single")
        self.room_var = tk.StringVar()
        self.checkin_var = tk.StringVar(value=date.today().isoformat())

        fields = [
            ("Guest Name", self.name_var),
            ("Mobile Number", self.phone_var),
        ]
        for col, (label, var) in enumerate(fields):
            tk.Label(form, text=label, bg="white", font=("Segoe UI", 10)).grid(
                row=0, column=col * 2, sticky="w", padx=(0, 6), pady=5)
            tk.Entry(form, textvariable=var, width=24, font=("Segoe UI", 10)).grid(
                row=0, column=col * 2 + 1, sticky="ew", padx=(0, 14), pady=5)

        tk.Label(form, text="Room Type", bg="white", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky="w", padx=(0, 6), pady=5)
        type_box = ttk.Combobox(form, textvariable=self.type_var,
                                values=list(ROOM_RATES.keys()), state="readonly", width=21)
        type_box.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=5)
        type_box.bind("<<ComboboxSelected>>", lambda _e: self.update_room_choices())

        tk.Label(form, text="Room Number", bg="white", font=("Segoe UI", 10)).grid(
            row=1, column=2, sticky="w", padx=(0, 6), pady=5)
        self.room_box = ttk.Combobox(form, textvariable=self.room_var,
                                     state="readonly", width=21)
        self.room_box.grid(row=1, column=3, sticky="ew", padx=(0, 14), pady=5)

        tk.Label(form, text="Check-in Date (YYYY-MM-DD)", bg="white",
                 font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", padx=(0, 6), pady=5)
        tk.Entry(form, textvariable=self.checkin_var, width=24,
                 font=("Segoe UI", 10)).grid(row=2, column=1, sticky="ew", padx=(0, 14), pady=5)

        tk.Label(form, text="Room Rate / Night", bg="white",
                 font=("Segoe UI", 10)).grid(row=2, column=2, sticky="w", padx=(0, 6), pady=5)
        self.rate_label = tk.Label(form, text="₹1,200", bg="white", fg="#16324f",
                                   font=("Segoe UI", 10, "bold"))
        self.rate_label.grid(row=2, column=3, sticky="w", pady=5)
        type_box.bind("<<ComboboxSelected>>", self.update_rate)

        for c in range(4):
            form.grid_columnconfigure(c, weight=1)

        actions = tk.Frame(form, bg="white")
        actions.grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))
        self.make_button(actions, "Book Room", self.book_room, "#19734a").pack(side="left", padx=(0, 8))
        self.make_button(actions, "Clear Form", self.clear_form, "#64748b").pack(side="left")

        records_frame = tk.LabelFrame(main, text="Booking Records", bg="white",
                                      font=("Segoe UI", 11, "bold"), padx=10, pady=10)
        records_frame.pack(fill="both", expand=True)

        toolbar = tk.Frame(records_frame, bg="white")
        toolbar.pack(fill="x", pady=(0, 8))
        self.make_button(toolbar, "Refresh", self.refresh_bookings, "#245b8f").pack(side="left", padx=(0, 8))
        self.make_button(toolbar, "Check Out / Generate Bill", self.checkout, "#9a5b13").pack(side="left", padx=(0, 8))
        self.make_button(toolbar, "Cancel Booking", self.cancel_booking, "#a83232").pack(side="left")

        columns = ("id", "guest", "phone", "room", "type", "checkin", "status", "bill")
        self.tree = ttk.Treeview(records_frame, columns=columns, show="headings", height=10)
        headings = {
            "id": "ID", "guest": "Guest Name", "phone": "Mobile", "room": "Room",
            "type": "Room Type", "checkin": "Check-in", "status": "Status", "bill": "Bill (₹)"
        }
        widths = {"id": 45, "guest": 170, "phone": 115, "room": 70, "type": 95,
                  "checkin": 110, "status": 95, "bill": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")
        self.tree.column("guest", anchor="w")
        scroll = ttk.Scrollbar(records_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self.root, textvariable=self.status_var, anchor="w",
                 bg="#e5edf6", fg="#334155", padx=12, pady=5).pack(fill="x")

    def make_button(self, parent, text, command, color):
        return tk.Button(parent, text=text, command=command, bg=color, fg="white",
                         activebackground=color, activeforeground="white",
                         relief="flat", padx=12, pady=7, cursor="hand2",
                         font=("Segoe UI", 9, "bold"))

    def update_rate(self, _event=None):
        rate = ROOM_RATES.get(self.type_var.get(), 0)
        self.rate_label.config(text=f"₹{rate:,}")

    def update_room_choices(self):
        choices = available_rooms(self.type_var.get())
        self.room_box["values"] = choices
        self.room_var.set(choices[0] if choices else "")
        self.update_rate()

    def book_room(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        room = self.room_var.get().strip()
        room_type = self.type_var.get()
        checkin = self.checkin_var.get().strip()

        if not name or not phone or not room or not checkin:
            messagebox.showwarning("Missing Information", "Please fill in all booking fields.")
            return
        if not phone.isdigit() or len(phone) < 10:
            messagebox.showwarning("Invalid Mobile Number", "Enter a valid mobile number (at least 10 digits).")
            return
        try:
            datetime.strptime(checkin, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date", "Use YYYY-MM-DD format, for example 2026-10-12.")
            return

        with connect_db() as con:
            busy = con.execute(
                "SELECT COUNT(*) FROM bookings WHERE room_no=? AND status='Booked'", (int(room),)
            ).fetchone()[0]
            if busy:
                messagebox.showerror("Room Unavailable", "This room is already booked. Please select another room.")
                self.update_room_choices()
                return
            con.execute("""
                INSERT INTO bookings(guest_name, phone, room_no, room_type, check_in, status)
                VALUES (?, ?, ?, ?, ?, 'Booked')
            """, (name, phone, int(room), room_type, checkin))
        messagebox.showinfo("Booking Successful", f"Room {room} booked successfully for {name}.")
        self.clear_form()
        self.refresh_bookings()
        self.update_room_choices()

    def refresh_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        with connect_db() as con:
            rows = con.execute("""
                SELECT id, guest_name, phone, room_no, room_type, check_in, status, bill
                FROM bookings ORDER BY id DESC
            """).fetchall()
        for row in rows:
            display = list(row)
            display[-1] = f"{float(display[-1] or 0):,.2f}"
            self.tree.insert("", "end", values=display)
        self.status_var.set(f"Total bookings: {len(rows)}")

    def selected_booking(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Select Booking", "Please select a booking record first.")
            return None
        return self.tree.item(selection[0], "values")

    def checkout(self):
        row = self.selected_booking()
        if not row:
            return
        booking_id = int(row[0])
        if row[6] != "Booked":
            messagebox.showinfo("Already Checked Out", "This booking is not currently active.")
            return
        with connect_db() as con:
            data = con.execute(
                "SELECT check_in, room_type, guest_name, room_no FROM bookings WHERE id=?",
                (booking_id,)
            ).fetchone()
        checkin_text, room_type, guest, room_no = data
        checkin_date = datetime.strptime(checkin_text, "%Y-%m-%d").date()
        today = date.today()
        days = max(1, (today - checkin_date).days)
        rate = ROOM_RATES[room_type]
        total = days * rate
        with connect_db() as con:
            con.execute("""
                UPDATE bookings SET status='Checked Out', check_out=?, bill=? WHERE id=?
            """, (today.isoformat(), total, booking_id))
        self.refresh_bookings()
        self.update_room_choices()
        messagebox.showinfo(
            "Final Bill",
            f" HOTEL BILL\n"
            f"-----------------------------\n"
            f"Guest: {guest}\nRoom: {room_no} ({room_type})\n"
            f"Check-in: {checkin_text}\nCheck-out: {today.isoformat()}\n"
            f"Days charged: {days}\nRate per night: ₹{rate:,}\n"
            f"-----------------------------\nTOTAL: ₹{total:,}\n\n"
            f"Thank you for staying with us!"
        )

    def cancel_booking(self):
        row = self.selected_booking()
        if not row:
            return
        if row[6] != "Booked":
            messagebox.showinfo("Cannot Cancel", "Only active bookings can be cancelled.")
            return
        if not messagebox.askyesno("Confirm Cancellation", f"Cancel booking ID {row[0]}?"):
            return
        with connect_db() as con:
            con.execute("UPDATE bookings SET status='Cancelled' WHERE id=?", (int(row[0]),))
        self.refresh_bookings()
        self.update_room_choices()
        messagebox.showinfo("Cancelled", "Booking cancelled successfully.")

    def clear_form(self):
        self.name_var.set("")
        self.phone_var.set("")
        self.checkin_var.set(date.today().isoformat())
        self.update_room_choices()

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = HotelManagementApp(root)
    root.mainloop()
