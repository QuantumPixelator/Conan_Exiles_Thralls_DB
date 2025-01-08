import sqlite3
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QListWidget, QFrame, QGridLayout, QLineEdit, QPushButton, QScrollArea
)
from PySide6.QtCore import Qt

class ThrallViewerApp(QWidget):
    def __init__(self):
        """
        Initialize the Thrall Viewer application.
        This app allows users to view and search through thrall data stored in an SQLite database.
        """
        super().__init__()
        self.setWindowTitle("Thrall Data Viewer for Conan Exiles")
        self.setFixedSize(1000, 700)

        # Establish database connection
        self.conn = sqlite3.connect("thralls.db")
        self.cursor = self.conn.cursor()

        # Set up the main layout
        self.main_layout = QVBoxLayout()

        # Header layout: Dropdown menu and search bar
        self.header_layout = QVBoxLayout()

        # Dropdown label
        self.header_label = QLabel("<b>Choose Thrall Type:</b>")
        self.header_label.setAlignment(Qt.AlignLeft)
        self.header_label.setStyleSheet("font-size: 16px; color: #E0C097;")

        # Dropdown to select thrall class/table
        self.table_dropdown = QComboBox()
        self.table_dropdown.addItems([
            "Alchemist", "Archer", "Armorer", "Bearer", "Blacksmith",
            "Carpenter", "Cook", "Fighter", "Performer", "Priest",
            "Smelter", "Sorcerer", "Tanner", "Taskmaster"
        ])
        self.table_dropdown.currentTextChanged.connect(self.populate_names)
        self.table_dropdown.setStyleSheet("background-color: #6F4E37; color: #E0C097; font-size: 14px; padding: 5px; border: 1px solid #8B5A2B;")

        # Search bar and button
        self.search_layout = QHBoxLayout()
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Enter search conditions (e.g., Gender=female AND Level Rate=fast, Agility=30 AND Strength<10, etc)")
        self.search_field.setStyleSheet("background-color: #3B3024; color: #E0C097; padding: 5px; border: 1px solid #6F4E37;")
        self.search_button = QPushButton("Search")
        self.search_button.setStyleSheet("background-color: #6F4E37; color: #E0C097; padding: 5px; border: 1px solid #8B5A2B;")
        self.search_button.clicked.connect(self.perform_search)
        self.search_layout.addWidget(self.search_field)
        self.search_layout.addWidget(self.search_button)

        # Add header components to layout
        self.header_layout.addWidget(self.header_label)
        self.header_layout.addWidget(self.table_dropdown)
        self.header_layout.addLayout(self.search_layout)

        # Separator line
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setStyleSheet("color: #6F4E37; background-color: #6F4E37; height: 1px;")

        # Lower area layout: Name list and details display
        self.lower_layout = QHBoxLayout()

        # List of names
        self.name_list = QListWidget()
        self.name_list.setFixedWidth(250)
        self.name_list.itemClicked.connect(self.display_data)
        self.name_list.setStyleSheet("background-color: #3B3024; color: #E0C097; font-size: 14px; border: 1px solid #6F4E37;")

        # Scrollable details area
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_widget = QWidget()
        self.details_layout = QGridLayout()
        self.details_widget.setLayout(self.details_layout)
        self.details_scroll.setWidget(self.details_widget)

        # Labels for displaying thrall details
        self.fields = [
            "Name", "ID", "Class", "Health", "Strength", "Agility",
            "Vitality", "Grit", "Bonus Vitality", "Level Rate", "Armor",
            "Incoming Damage Reduction", "Killed XP", "Temperament",
            "Gender", "Thrallable", "Race", "Faction", "Description", "Notes"
        ]
        self.detail_labels = {}
        for i, field in enumerate(self.fields):
            label = QLabel(f"<b>{field}:</b>")
            label.setStyleSheet("color: #C19A6B; font-size: 14px;")
            value = QLabel("N/A")
            value.setStyleSheet("color: #E0C097; font-size: 14px;")
            value.setWordWrap(True)
            self.details_layout.addWidget(label, i, 0)
            self.details_layout.addWidget(value, i, 1)
            self.detail_labels[field] = value

        # Combine lower layout components
        self.lower_layout.addWidget(self.name_list)
        self.lower_layout.addWidget(self.details_scroll)

        # Add all components to main layout
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.separator)
        self.main_layout.addLayout(self.lower_layout)
        self.setLayout(self.main_layout)

        # Populate initial names
        self.populate_names()

    def populate_names(self):
        """
        Populate the name list with entries from the selected thrall table.
        """
        self.name_list.clear()
        table = self.table_dropdown.currentText()
        try:
            self.cursor.execute(f"SELECT name FROM {table} ORDER BY name ASC")
            names = self.cursor.fetchall()
            for name in names:
                self.name_list.addItem(name[0])
        except Exception as e:
            self.name_list.addItem(f"Error loading names: {e}")

    def display_data(self, item):
        """
        Display detailed data for the selected thrall.

        :param item: QListWidgetItem representing the selected thrall name.
        """
        table = self.table_dropdown.currentText()
        name = item.text()
        try:
            self.cursor.execute(f"SELECT * FROM {table} WHERE name = ?", (name,))
            data = self.cursor.fetchone()
            if data:
                for i, field in enumerate(self.fields):
                    self.detail_labels[field].setText(data[i] if data[i] else "N/A")
        except Exception as e:
            for field in self.fields:
                self.detail_labels[field].setText("Error")

    def perform_search(self):
        """
        Perform a search based on user-defined conditions in the search bar.
        """
        query = self.search_field.text().strip()
        table = self.table_dropdown.currentText()
        self.name_list.clear()

        if not query:
            self.populate_names()
            return

        try:
            conditions = []
            params = []

            # Parse query conditions (e.g., Agility>25 AND Vitality<=10)
            for condition in query.split(" AND "):
                operators = [">=", "<=", ">", "<", "="]
                for operator in operators:
                    if operator in condition:
                        field, value = condition.split(operator, 1)
                        field = field.strip().lower().replace(" ", "_")
                        value = value.strip()
                        conditions.append(f"[{field}] {operator} ?")
                        params.append(value)
                        break

            sql = f"SELECT name FROM {table}"
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            self.cursor.execute(sql, params)
            results = self.cursor.fetchall()

            if results:
                for result in results:
                    self.name_list.addItem(result[0])
            else:
                self.name_list.addItem("No results found.")
        except Exception as e:
            self.name_list.addItem(f"Search error: {e}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #1F1B16;
            color: #E0C097;
            font-family: Arial, sans-serif;
        }
        QLabel {
            font-size: 16px;
        }
    """)

    window = ThrallViewerApp()
    window.show()
    sys.exit(app.exec())