import os
import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QProgressBar, QLabel
)
from PySide6.QtCore import Qt

# Database setup
def initialize_database():
    conn = sqlite3.connect("thralls.db")
    cursor = conn.cursor()

    # Thrall classes
    classes = [
        "Alchemist", "Archer", "Armorer", "Bearer", "Blacksmith",
        "Carpenter", "Cook", "Fighter", "Performer", "Priest",
        "Smelter", "Sorcerer", "Tanner", "Taskmaster"
    ]

    # Create tables
    for thrall_class in classes:
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {thrall_class} (
                name TEXT PRIMARY KEY,
                id TEXT,
                class TEXT,
                health TEXT,
                strength TEXT,
                agility TEXT,
                vitality TEXT,
                grit TEXT,
                bonus_vitality TEXT,
                level_rate TEXT,
                armor TEXT,
                incoming_damage_reduction TEXT,
                killed_xp TEXT,
                temperament TEXT,
                gender TEXT,
                thrallable TEXT,
                race TEXT,
                faction TEXT,
                description TEXT,
                notes TEXT
            )
        """)
    conn.commit()
    conn.close()

# Parse thrall data
def parse_thrall_file(file_path):
    data = {}
    with open(file_path, "r") as file:
        for line in file:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                data[key.strip().lower()] = value.strip() or "N/A"
    return data

# Insert or update data in database
def insert_or_update_data(data):
    conn = sqlite3.connect("thralls.db")
    cursor = conn.cursor()

    thrall_class = data.get("class", "").lower()
    if thrall_class not in [
        "alchemist", "archer", "armorer", "bearer", "blacksmith",
        "carpenter", "cook", "fighter", "performer", "priest",
        "smelter", "sorcerer", "tanner", "taskmaster"
    ]:
        conn.close()
        return f"INVALID CLASS: {thrall_class.upper()}"

    cursor.execute(f"""
        INSERT INTO {thrall_class} (
            name, id, class, health, strength, agility, vitality, grit,
            bonus_vitality, level_rate, armor, incoming_damage_reduction,
            killed_xp, temperament, gender, thrallable, race, faction,
            description, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            id=excluded.id,
            health=excluded.health,
            strength=excluded.strength,
            agility=excluded.agility,
            vitality=excluded.vitality,
            grit=excluded.grit,
            bonus_vitality=excluded.bonus_vitality,
            level_rate=excluded.level_rate,
            armor=excluded.armor,
            incoming_damage_reduction=excluded.incoming_damage_reduction,
            killed_xp=excluded.killed_xp,
            temperament=excluded.temperament,
            gender=excluded.gender,
            thrallable=excluded.thrallable,
            race=excluded.race,
            faction=excluded.faction,
            description=excluded.description,
            notes=excluded.notes
    """, (
        data.get("name", "N/A"), data.get("id", "N/A"), data.get("class", "N/A"),
        data.get("health", "N/A"), data.get("strength", "N/A"),
        data.get("agility", "N/A"), data.get("vitality", "N/A"),
        data.get("grit", "N/A"), data.get("bonus vitality", "N/A"),
        data.get("level rate", "N/A"), data.get("armor", "N/A"),
        data.get("incoming damage reduction", "N/A"), data.get("killed xp", "N/A"),
        data.get("temperament", "N/A"), data.get("gender", "N/A"),
        data.get("thrallable", "N/A"), data.get("race", "N/A"),
        data.get("faction", "N/A"), data.get("description", "N/A"),
        data.get("notes", "N/A")
    ))
    conn.commit()
    conn.close()
    return "SUCCESS"

# GUI Application
class ThrallApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Thrall Data Importer")
        self.setGeometry(100, 100, 800, 600)
        self.layout = QVBoxLayout()

        # Widgets
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.progress = QProgressBar()
        self.file_label = QLabel("No files selected")
        self.file_label.setAlignment(Qt.AlignCenter)

        self.load_button = QPushButton("Load Thrall Files")
        self.load_button.clicked.connect(self.load_files)

        self.layout.addWidget(self.file_label)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.log)
        self.layout.addWidget(self.progress)

        self.setLayout(self.layout)

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Thrall Files", "", "Text Files (*.txt)")
        if not files:
            return

        self.file_label.setText(f"Processing {len(files)} file(s)...")
        self.progress.setValue(0)

        for i, file_path in enumerate(files):
            file_name = os.path.basename(file_path)
            try:
                thrall_data = parse_thrall_file(file_path)
                result = insert_or_update_data(thrall_data)
                if "INVALID CLASS" in result:
                    self.log.append(f"<b style='color:red;'>{file_name}: {result}</b>")
                else:
                    self.log.append(f"<b>{file_name}: {result}</b>")
            except Exception as e:
                self.log.append(f"<b style='color:red;'>{file_name}: ERROR - {e}</b>")

            self.progress.setValue(int((i + 1) / len(files) * 100))

        self.file_label.setText("Processing Complete")

if __name__ == "__main__":
    import sys

    initialize_database()
    app = QApplication(sys.argv)
    window = ThrallApp()
    window.show()
    sys.exit(app.exec())
