#!/usr/bin/env python3
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout, QFileDialog

class NaveRPGCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculador de Fichas de Naves RPG")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Input para nivel
        level_layout = QHBoxLayout()
        level_label = QLabel("Nivel (1-125):")
        self.level_input = QLineEdit()
        self.level_input.textChanged.connect(self.update_points_available)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_input)
        main_layout.addLayout(level_layout)

        # Indicador de puntos disponibles
        self.points_available_label = QLabel("Puntos disponibles: 0")
        main_layout.addWidget(self.points_available_label)

        # Inputs y botones para puntos en stats
        stats_group = QGroupBox("Puntos a distribuir")
        stats_layout = QFormLayout()

        self.att_input = QLineEdit("3")
        att_buttons = self.create_stat_buttons(self.att_input)
        self.def_input = QLineEdit("3")
        def_buttons = self.create_stat_buttons(self.def_input)
        self.eva_input = QLineEdit("3")
        eva_buttons = self.create_stat_buttons(self.eva_input)
        self.ene_input = QLineEdit("3")
        ene_buttons = self.create_stat_buttons(self.ene_input)
        self.shi_input = QLineEdit("3")
        shi_buttons = self.create_stat_buttons(self.shi_input)
        self.fue_input = QLineEdit("3")
        fue_buttons = self.create_stat_buttons(self.fue_input)

        stats_layout.addRow("Attack:", self.create_stat_row(self.att_input, att_buttons))
        stats_layout.addRow("Defence:", self.create_stat_row(self.def_input, def_buttons))
        stats_layout.addRow("Evasion:", self.create_stat_row(self.eva_input, eva_buttons))
        stats_layout.addRow("Energy:", self.create_stat_row(self.ene_input, ene_buttons))
        stats_layout.addRow("Shield:", self.create_stat_row(self.shi_input, shi_buttons))
        stats_layout.addRow("Fuel:", self.create_stat_row(self.fue_input, fue_buttons))
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        # Botones calcular, exportar y reset
        buttons_layout = QHBoxLayout()
        self.calc_button = QPushButton("Calcular")
        self.calc_button.clicked.connect(self.calcular)
        buttons_layout.addWidget(self.calc_button)

        self.export_button = QPushButton("Exportar a TXT")
        self.export_button.clicked.connect(self.exportar)
        buttons_layout.addWidget(self.export_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        buttons_layout.addWidget(self.reset_button)
        main_layout.addLayout(buttons_layout)

        # Resultados stats
        self.stats_result = QGroupBox("Valores de Stats")
        self.stats_layout = QFormLayout()
        self.att_value_label = QLabel()
        self.def_value_label = QLabel()
        self.eva_value_label = QLabel()
        self.ene_value_label = QLabel()
        self.shi_value_label = QLabel()
        self.fue_value_label = QLabel()
        self.stats_layout.addRow("Attack:", self.att_value_label)
        self.stats_layout.addRow("Defence:", self.def_value_label)
        self.stats_layout.addRow("Evasion:", self.eva_value_label)
        self.stats_layout.addRow("Energy:", self.ene_value_label)
        self.stats_layout.addRow("Shield:", self.shi_value_label)
        self.stats_layout.addRow("Fuel:", self.fue_value_label)
        self.stats_result.setLayout(self.stats_layout)
        main_layout.addWidget(self.stats_result)

        # Cuadro % marcadores
        self.percent_group = QGroupBox("Marcadores %")
        percent_layout = QFormLayout()
        self.pierce_label = QLabel()
        self.def_perc_label = QLabel()
        self.eva_perc_label = QLabel()
        percent_layout.addRow("Pierce %:", self.pierce_label)
        percent_layout.addRow("Defence %:", self.def_perc_label)
        percent_layout.addRow("Evasion %:", self.eva_perc_label)
        self.percent_group.setLayout(percent_layout)
        main_layout.addWidget(self.percent_group)

        # Cuadro marcadores energy, shield, fuel
        self.markers_group = QGroupBox("Marcadores")
        markers_layout = QFormLayout()
        self.ene_mark_label = QLabel()
        self.shi_total_label = QLabel()
        self.fue_mark_label = QLabel()
        markers_layout.addRow("Energy marker:", self.ene_mark_label)
        markers_layout.addRow("Shield total (joules):", self.shi_total_label)
        markers_layout.addRow("Fuel marker (litros):", self.fue_mark_label)
        self.markers_group.setLayout(markers_layout)
        main_layout.addWidget(self.markers_group)

        # Label para errores
        self.error_label = QLabel()
        main_layout.addWidget(self.error_label)

        self.setLayout(main_layout)
        self.update_points_available()

    def create_stat_buttons(self, input_field):
        layout = QHBoxLayout()
        btn_minus10 = QPushButton("-10")
        btn_minus3 = QPushButton("-3")
        btn_minus1 = QPushButton("-1")
        btn_plus1 = QPushButton("+1")
        btn_plus3 = QPushButton("+3")
        btn_plus10 = QPushButton("+10")
        btn_minus10.clicked.connect(lambda: self.add_points(input_field, -10))
        btn_minus3.clicked.connect(lambda: self.add_points(input_field, -3))
        btn_minus1.clicked.connect(lambda: self.add_points(input_field, -1))
        btn_plus1.clicked.connect(lambda: self.add_points(input_field, 1))
        btn_plus3.clicked.connect(lambda: self.add_points(input_field, 3))
        btn_plus10.clicked.connect(lambda: self.add_points(input_field, 10))
        layout.addWidget(btn_minus10)
        layout.addWidget(btn_minus3)
        layout.addWidget(btn_minus1)
        layout.addWidget(btn_plus1)
        layout.addWidget(btn_plus3)
        layout.addWidget(btn_plus10)
        return layout

    def create_stat_row(self, input_field, buttons_layout):
        layout = QHBoxLayout()
        layout.addWidget(input_field)
        layout.addLayout(buttons_layout)
        return layout

    def add_points(self, input_field, delta):
        try:
            level = int(self.level_input.text() or 0)
            if level < 1 or level > 125:
                return

            total_points = (level * 3) + (3 * 6)  # 3 por nivel + 3 base por 6 stats
            used_points = int(self.att_input.text() or 0) + int(self.def_input.text() or 0) + \
                          int(self.eva_input.text() or 0) + int(self.ene_input.text() or 0) + \
                          int(self.shi_input.text() or 0) + int(self.fue_input.text() or 0)

            max_stat = 340 if level > 100 else 300
            current = int(input_field.text() or 0)
            new = current + delta

            if delta > 0:
                if new <= max_stat and (used_points + delta) <= total_points:
                    input_field.setText(str(new))
            elif delta < 0:
                if new >= 3:
                    input_field.setText(str(new))

            self.update_points_available()

        except ValueError:
            pass

    def update_points_available(self):
        try:
            level = int(self.level_input.text() or 0)
            if level < 1 or level > 125:
                self.points_available_label.setText("Puntos disponibles: 0")
                return

            total_points = (level * 3) + (3 * 6)
            used_points = int(self.att_input.text() or 0) + int(self.def_input.text() or 0) + \
                          int(self.eva_input.text() or 0) + int(self.ene_input.text() or 0) + \
                          int(self.shi_input.text() or 0) + int(self.fue_input.text() or 0)

            available = total_points - used_points
            self.points_available_label.setText(f"Puntos disponibles: {available}")

        except ValueError:
            self.points_available_label.setText("Puntos disponibles: 0")

    def reset(self):
        # Restablecer inputs a valor base (3)
        self.att_input.setText("3")
        self.def_input.setText("3")
        self.eva_input.setText("3")
        self.ene_input.setText("3")
        self.shi_input.setText("3")
        self.fue_input.setText("3")

        # Limpiar resultados
        self.att_value_label.setText("")
        self.def_value_label.setText("")
        self.eva_value_label.setText("")
        self.ene_value_label.setText("")
        self.shi_value_label.setText("")
        self.fue_value_label.setText("")
        self.pierce_label.setText("")
        self.def_perc_label.setText("")
        self.eva_perc_label.setText("")
        self.ene_mark_label.setText("")
        self.shi_total_label.setText("")
        self.fue_mark_label.setText("")
        self.error_label.setText("")

        self.update_points_available()

    def calcular(self):
        try:
            level = int(self.level_input.text())
            if level < 1 or level > 125:
                self.error_label.setText("Nivel debe estar entre 1 y 125.")
                return

            total_points = (level * 3) + (3 * 6)
            max_stat = 340 if level > 100 else 300

            points_att = int(self.att_input.text() or 0)
            points_def = int(self.def_input.text() or 0)
            points_eva = int(self.eva_input.text() or 0)
            points_ene = int(self.ene_input.text() or 0)
            points_shi = int(self.shi_input.text() or 0)
            points_fue = int(self.fue_input.text() or 0)

            points_list = [points_att, points_def, points_eva, points_ene, points_shi, points_fue]

            if any(p < 3 for p in points_list):
                self.error_label.setText("Cada stat debe tener al menos 3 puntos.")
                return
            if any(p > max_stat for p in points_list):
                self.error_label.setText(f"Cada valor de stat no puede exceder {max_stat}.")
                return

            used_points = sum(points_list)
            if used_points > total_points:
                self.error_label.setText(f"Puntos usados: {used_points}, no pueden exceder {total_points}.")
                return

            self.error_label.setText("")

            # Asignar valores de stats (mismos que puntos)
            att_value = points_att
            def_value = points_def
            eva_value = points_eva
            ene_value = points_ene
            shi_value = points_shi
            fue_value = points_fue

            self.att_value_label.setText(str(att_value))
            self.def_value_label.setText(str(def_value))
            self.eva_value_label.setText(str(eva_value))
            self.ene_value_label.setText(str(ene_value))
            self.shi_value_label.setText(str(shi_value))
            self.fue_value_label.setText(str(fue_value))

            # Marcadores %
            pierce = att_value * 0.1
            def_perc = def_value * 0.1
            eva_perc = eva_value * 0.1

            self.pierce_label.setText(f"{pierce:.1f}%")
            self.def_perc_label.setText(f"{def_perc:.1f}%")
            self.eva_perc_label.setText(f"{eva_perc:.1f}%")

            # Marcadores energy, shield, fuel (solo puntos añadidos)
            added_ene = max(0, points_ene - 3)
            added_shi = max(0, points_shi - 3)
            added_fue = max(0, points_fue - 3)

            ene_mark = (added_ene // 3) * 10
            shi_total = (added_shi // 3) * (1 / 8)
            fue_mark = added_fue * (34 / 3)  # 30 puntos añadidos = 340 litros

            self.ene_mark_label.setText(str(ene_mark))
            self.shi_total_label.setText(f"{shi_total:.3f}")
            self.fue_mark_label.setText(f"{fue_mark:.0f}")

        except ValueError:
            self.error_label.setText("Ingresa valores numéricos válidos.")

    def exportar(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exportar a TXT", "", "Text Files (*.txt)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(f"Nivel: {self.level_input.text()}\n\n")
                    f.write("Puntos distribuidos:\n")
                    f.write(f"Attack: {self.att_input.text()}\n")
                    f.write(f"Defence: {self.def_input.text()}\n")
                    f.write(f"Evasion: {self.eva_input.text()}\n")
                    f.write(f"Energy: {self.ene_input.text()}\n")
                    f.write(f"Shield: {self.shi_input.text()}\n")
                    f.write(f"Fuel: {self.fue_input.text()}\n\n")
                    f.write("Valores de Stats:\n")
                    f.write(f"Attack: {self.att_value_label.text()}\n")
                    f.write(f"Defence: {self.def_value_label.text()}\n")
                    f.write(f"Evasion: {self.eva_value_label.text()}\n")
                    f.write(f"Energy: {self.ene_value_label.text()}\n")
                    f.write(f"Shield: {self.shi_value_label.text()}\n")
                    f.write(f"Fuel: {self.fue_value_label.text()}\n\n")
                    f.write("Marcadores %:\n")
                    f.write(f"Pierce: {self.pierce_label.text()}\n")
                    f.write(f"Defence: {self.def_perc_label.text()}\n")
                    f.write(f"Evasion: {self.eva_perc_label.text()}\n\n")
                    f.write("Marcadores:\n")
                    f.write(f"Energy marker: {self.ene_mark_label.text()}\n")
                    f.write(f"Shield total (joules): {self.shi_total_label.text()}\n")
                    f.write(f"Fuel marker (litros): {self.fue_mark_label.text()}\n")
                    f.write(f"Error (si hay): {self.error_label.text()}\n")
            except Exception as e:
                self.error_label.setText(f"Error al exportar: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NaveRPGCalculator()
    window.show()
    sys.exit(app.exec())
