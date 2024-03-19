import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

class DonorDatabase:
    def __init__(self):
        self.donors = {}

    def add_donor(self, donor):
        self.donors[donor["donor_id"]] = donor

    def get_donor(self, donor_id):
        return self.donors.get(donor_id)

    def get_all_donors(self):
        return list(self.donors.values())

    def save_to_file(self, filename):
        with open(filename, "w") as file:
            json.dump(self.donors, file)

    def load_from_file(self, filename):
        with open(filename, "r") as file:
            self.donors = json.load(file)

class BloodBank:
    def __init__(self):
        self.inventory = {}

    def add_blood_bag(self, blood_type, quantity):
        self.inventory[blood_type] = self.inventory.get(blood_type, 0) + quantity

    def remove_blood_bag(self, blood_type, quantity):
        if blood_type in self.inventory:
            self.inventory[blood_type] = max(0, self.inventory[blood_type] - quantity)

    def get_blood_quantity(self, blood_type):
        return self.inventory.get(blood_type, 0)

class Scheduler:
    def __init__(self):
        self.appointments = []

    def book_appointment(self, appointment):
        self.appointments.append(appointment)

    def get_all_appointments(self):
        return self.appointments

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        
        self.label = tk.Label(self.root, text="Login as Donor or Admin")
        self.label.pack(pady=10)
        
        self.donor_button = tk.Button(self.root, text="Login as Donor", command=self.login_as_donor)
        self.donor_button.pack(pady=5)
        
        self.admin_button = tk.Button(self.root, text="Login as Admin", command=self.login_as_admin)
        self.admin_button.pack(pady=5)
        
        self.root.mainloop()

    def login_as_donor(self):
        self.root.destroy()
        DonorManagementSystem()

    def login_as_admin(self):
        self.root.destroy()
        AdminManagementSystem()

class DonorManagementSystem:
    valid_blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

    def __init__(self):
        self.database = DonorDatabase()
        self.blood_bank = BloodBank()
        self.scheduler = Scheduler()
        self.load_donor_details()

        self.root = tk.Tk()
        self.root.title("Donor Management System")

        # Load the background image
        image_path = r"C:\Users\Udit\Downloads\download.jpeg"
        background_image = Image.open(image_path)
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Create a label to display the background image
        self.background_label = tk.Label(self.root, image=self.background_photo)
        self.background_label.image = self.background_photo  # Store a reference to the image to prevent garbage collection
        self.background_label.pack()

        # Create transparent buttons
        self.create_buttons()

        self.root.mainloop()

    def load_donor_details(self):
        try:
            self.database.load_from_file("donor_data.json")
        except FileNotFoundError:
            # If the file doesn't exist, initialize an empty database
            self.database = DonorDatabase()

    def save_donor_details(self):
        self.database.save_to_file("donor_data.json")

    def create_buttons(self):
        # Button coordinates (x, y) and sizes (width, height) relative to the background image size
        button_positions = {
            "Find Donor": (0.2, 0.3, 0.3, 0.1),  # Increased width
            "Register Donor": (0.6, 0.3, 0.3, 0.1),  # Increased width
            "Place Blood Request": (0.2, 0.5, 0.3, 0.1),  # Increased width
            "Book Appointment": (0.6, 0.5, 0.3, 0.1)  # Increased width
        }

        for button_text, (x, y, width, height) in button_positions.items():
            button_x = int(self.background_photo.width() * x)
            button_y = int(self.background_photo.height() * y)
            button_width = int(self.background_photo.width() * width)
            button_height = int(self.background_photo.height() * height)

            button = tk.Button(self.root, text=button_text, command=self.get_button_command(button_text))
            button.place(x=button_x, y=button_y, width=button_width, height=button_height)

    def get_button_command(self, button_text):
        if button_text == "Find Donor":
            return self.find_donor
        elif button_text == "Register Donor":
            return self.register_donor
        elif button_text == "Place Blood Request":
            return self.place_request
        elif button_text == "Book Appointment":
            return self.book_appointment

    def find_donor(self):
        donor_id = simpledialog.askstring("Find Donor", "Enter donor ID:")
        if donor_id:
            donor = self.database.get_donor(donor_id)
            if donor:
                messagebox.showinfo("Donor Details", f"Name: {donor['name']}\nBlood Type: {donor['blood_type']}")
            else:
                messagebox.showinfo("Donor Details", "Donor not found.")

    def register_donor(self):
        donor_id = simpledialog.askstring("Register Donor", "Enter donor ID:")
        if donor_id:
            # Check if the donor ID already exists
            if self.database.get_donor(donor_id):
                messagebox.showinfo("Register Donor", "Donor ID already exists.")
            else:
                name = simpledialog.askstring("Register Donor", "Enter donor name:")
                blood_type = simpledialog.askstring("Register Donor", "Enter donor blood type:")
                if blood_type.upper() in self.valid_blood_types:
                    donor = {"donor_id": donor_id, "name": name, "blood_type": blood_type.upper()}
                    self.database.add_donor(donor)
                    self.save_donor_details()
                    messagebox.showinfo("Register Donor", "Donor registered successfully.")
                else:
                    messagebox.showinfo("Register Donor", "Invalid blood type.")

    def place_request(self):
        blood_type = simpledialog.askstring("Place Blood Request", "Enter blood type:")
        if blood_type.upper() in self.valid_blood_types:
            quantity = simpledialog.askinteger("Place Blood Request", "Enter quantity:")
            if quantity:
                available_quantity = self.blood_bank.get_blood_quantity(blood_type.upper())
                if available_quantity >= quantity:
                    self.blood_bank.remove_blood_bag(blood_type.upper(), quantity)
                    messagebox.showinfo("Place Blood Request", f"{quantity} bags of {blood_type} blood released.")
                    # Notify donors of the requested blood type
                    self.notify_donors(blood_type)
                else:
                    messagebox.showinfo("Place Blood Request", "Insufficient blood quantity.")
        else:
            messagebox.showinfo("Place Blood Request", "Invalid blood type.")

    def book_appointment(self):
        donor_id = simpledialog.askstring("Book Appointment", "Enter donor ID:")
        if donor_id:
            donor = self.database.get_donor(donor_id)
            if donor:
                appointment = {
                    "donor_id": donor_id,
                    "name": donor["name"],
                    "blood_type": donor["blood_type"],
                    "date": simpledialog.askstring("Book Appointment", "Enter appointment date:")
                }
                self.scheduler.book_appointment(appointment)
                messagebox.showinfo("Book Appointment", "Appointment booked successfully.")
            else:
                messagebox.showinfo("Book Appointment", "Donor not found.")

    def notify_donors(self, blood_type):
        donors = self.database.get_all_donors()
        for donor in donors:
            if donor["blood_type"] == blood_type:
                messagebox.showinfo("Blood Request", f"A request for {blood_type} blood has been made. Please consider donating if you can.")

class AdminManagementSystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Admin Management System")

        self.database = DonorDatabase()
        self.load_donor_details()

        self.button_show_donor_details = tk.Button(self.root, text="Show Donor Details", command=self.show_donor_details)
        self.button_show_donor_details.pack(pady=5)

        self.button_generate_request = tk.Button(self.root, text="Generate Blood Request", command=self.generate_blood_request)
        self.button_generate_request.pack(pady=5)

        self.button_show_appointments = tk.Button(self.root, text="Show Appointments", command=self.show_appointments)
        self.button_show_appointments.pack(pady=5)

        self.root.mainloop()

    def load_donor_details(self):
        try:
            self.database.load_from_file("donor_data.json")
        except FileNotFoundError:
            # If the file doesn't exist, initialize an empty database
            self.database = DonorDatabase()

    def show_donor_details(self):
        all_donors = self.database.get_all_donors()
        if all_donors:
            details = "\n".join([f"Donor ID: {donor['donor_id']}, Name: {donor['name']}, Blood Type: {donor['blood_type']}" for donor in all_donors])
            messagebox.showinfo("Donor Details", details)
        else:
            messagebox.showinfo("Donor Details", "No donors found.")

    def generate_blood_request(self):
        blood_type = simpledialog.askstring("Generate Blood Request", "Enter blood type:")
        if blood_type.upper() in DonorManagementSystem.valid_blood_types:
            quantity = simpledialog.askinteger("Generate Blood Request", "Enter quantity:")
            if quantity:
                messagebox.showinfo("Generate Blood Request", f"{quantity} bags of {blood_type} blood requested.")
                # Notify donors of the requested blood type
                self.notify_donors(blood_type)
        else:
            messagebox.showinfo("Generate Blood Request", "Invalid blood type.")

    def notify_donors(self, blood_type):
        donors = self.database.get_all_donors()
        for donor in donors:
            if donor["blood_type"] == blood_type:
                messagebox.showinfo("Blood Request", f"A request for {blood_type} blood has been made. Please consider donating if you can.")

    def show_appointments(self):
        appointments = Scheduler().get_all_appointments()
        if appointments:
            details = "\n".join([f"Donor ID: {appointment['donor_id']}, Name: {appointment['name']}, Blood Type: {appointment['blood_type']}, Date: {appointment['date']}" for appointment in appointments])
            messagebox.showinfo("Appointments", details)
        else:
            messagebox.showinfo("Appointments", "No appointments found.")

if __name__ == "__main__":
    LoginWindow()

