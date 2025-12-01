#!/usr/bin/env python3
"""
Flarm Styler - IDE para QSS con Inteligencia Artificial.
"""

import sys
import os
import re
import json
import urllib.request
import urllib.error
import ssl
import threading
from typing import Dict, List, Optional

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QPushButton, QFileDialog, 
                                QTextEdit, QFrame, QGraphicsDropShadowEffect, QSizePolicy,
                                QSplitter, QTableWidget, QTableWidgetItem,
                                QHeaderView, QLineEdit, QComboBox, QCheckBox, QRadioButton,
                                QProgressBar, QSlider, QGroupBox, QScrollArea)
    from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QObject, QSize, QTimer, QEvent
    from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QLinearGradient
    from PyQt5.QtSvg import QSvgWidget
    HAS_PYQT5 = True
except ImportError:
    HAS_PYQT5 = False
    print("Error: PyQt5 no está instalado.")
    sys.exit(1)

# --- Clases de UI Compartidas ---

class Win11Button(QPushButton):
    """Botón estilo Windows 11 (Accent Color)."""
    def __init__(self, text, parent=None, is_primary=True):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        self.setFont(QFont("Segoe UI Variable Display", 9))
        
        self.is_primary = is_primary
        self.update_style()

    def update_style(self):
        if self.is_primary:
            # Estilo Accent (Azul)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border-radius: 4px;
                    border: 1px solid #0078D4;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background-color: #1084D9;
                    border: 1px solid #1084D9;
                }
                QPushButton:pressed {
                    background-color: #006CC1;
                    border: 1px solid #006CC1;
                }
                QPushButton:disabled {
                    background-color: #333333;
                    color: #888888;
                    border: 1px solid #333333;
                }
            """)
        else:
            # Estilo Standard (Gris Oscuro)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2D2D2D;
                    color: white;
                    border-radius: 4px;
                    border: 1px solid #3D3D3D;
                    padding: 0 16px;
                }
                QPushButton:hover {
                    background-color: #3D3D3D;
                    border: 1px solid #4D4D4D;
                }
                QPushButton:pressed {
                    background-color: #262626;
                    border: 1px solid #262626;
                }
            """)

class TitleBarButton(QPushButton):
    """Botón de barra de título (Min, Max, Close)."""
    def __init__(self, icon_path, parent=None, is_close=False):
        super().__init__(parent)
        self.setFixedSize(46, 32)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(10, 10))
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: %s;
            }
            QPushButton:pressed {
                background-color: %s;
            }
        """ % ("#C42B1C" if is_close else "#333333", "#B32415" if is_close else "#262626"))

# --- Lógica QSS ---

class QSSParser:
    """Parser simple para leer y modificar archivos QSS."""
    
    @staticmethod
    def parse(qss_content: str) -> Dict[str, Dict[str, str]]:
        rules = {}
        qss_content = re.sub(r'/\*.*?\*/', '', qss_content, flags=re.DOTALL)
        pattern = re.compile(r'([^{]+)\{([^}]+)\}')
        
        for match in pattern.finditer(qss_content):
            selector = match.group(1).strip()
            body = match.group(2).strip()
            props = {}
            for prop_line in body.split(';'):
                if ':' in prop_line:
                    key, val = prop_line.split(':', 1)
                    props[key.strip()] = val.strip()
            if selector in rules:
                rules[selector].update(props)
            else:
                rules[selector] = props
        return rules

    @staticmethod
    def stringify(rules: Dict[str, Dict[str, str]]) -> str:
        qss = ""
        for selector, props in rules.items():
            qss += f"{selector} {{\n"
            for key, val in props.items():
                qss += f"    {key}: {val};\n"
            qss += "}\n\n"
        return qss

class QSSModderWidget(QWidget):
    """Widget para editar y previsualizar QSS."""
    update_editor_signal = pyqtSignal(str)
    generate_btn_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.current_rules = {}
        self.update_editor_signal.connect(self._on_update_editor)
        self.generate_btn_signal.connect(self._on_generate_finished)

    def init_ui(self):
        layout = QHBoxLayout(self)
        
        # --- Panel Izquierdo ---
        left_splitter = QSplitter(Qt.Vertical)
        
        self.selector_list = QTableWidget()
        self.selector_list.setColumnCount(1)
        self.selector_list.setHorizontalHeaderLabels(["Selectores"])
        self.selector_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.selector_list.itemSelectionChanged.connect(self.on_selector_selected)
        left_splitter.addWidget(self.selector_list)
        
        self.prop_table = QTableWidget()
        self.prop_table.setColumnCount(2)
        self.prop_table.setHorizontalHeaderLabels(["Propiedad", "Valor"])
        self.prop_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.prop_table.itemChanged.connect(self.on_property_changed)
        left_splitter.addWidget(self.prop_table)
        
        self.raw_editor = QTextEdit()
        self.raw_editor.setPlaceholderText("O pega tu código QSS aquí...")
        self.raw_editor.textChanged.connect(self.on_raw_text_changed)
        left_splitter.addWidget(self.raw_editor)
        
        layout.addWidget(left_splitter, 1)

        # --- Panel Central: Generador IA ---
        ai_group = QGroupBox("Generador IA (Gemini)")
        ai_layout = QVBoxLayout(ai_group)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Tu API Key de Gemini...")
        self.api_key_input.setEchoMode(QLineEdit.Password)
        ai_layout.addWidget(self.api_key_input)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe el tema que quieres...")
        self.prompt_input.setMaximumHeight(100)
        ai_layout.addWidget(self.prompt_input)
        
        self.generate_btn = Win11Button("Generar con IA", is_primary=True)
        self.generate_btn.clicked.connect(self.generate_qss_with_ai)
        ai_layout.addWidget(self.generate_btn)
        
        ai_layout.addStretch()
        layout.addWidget(ai_group, 0)

        # --- Panel Derecho: Previsualización ---
        preview_group = QGroupBox("Vista Previa")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_area = QScrollArea()
        self.preview_widget = QWidget()
        self.preview_widget.setObjectName("PreviewContainer")
        self.preview_ui(self.preview_widget)
        self.preview_area.setWidget(self.preview_widget)
        self.preview_area.setWidgetResizable(True)
        
        preview_layout.addWidget(self.preview_area)
        
        btn_layout = QHBoxLayout()
        load_btn = Win11Button("Cargar QSS", is_primary=False)
        load_btn.clicked.connect(self.load_qss_file)
        apply_btn = Win11Button("Aplicar Cambios", is_primary=True)
        apply_btn.clicked.connect(self.apply_changes)
        
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(apply_btn)
        preview_layout.addLayout(btn_layout)
        
        layout.addWidget(preview_group, 1)
        
        self.updating_ui = False
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(600)
        self.debounce_timer.timeout.connect(self.process_text_change)

    def preview_ui(self, parent):
        layout = QVBoxLayout(parent)
        layout.setSpacing(15)
        layout.addWidget(QLabel("Etiqueta de Ejemplo (QLabel)"))
        layout.addWidget(QPushButton("Botón Normal (QPushButton)"))
        btn_primary = QPushButton("Botón Primario (QPushButton#primary)")
        btn_primary.setObjectName("primary")
        layout.addWidget(btn_primary)
        layout.addWidget(QLineEdit("Campo de Texto (QLineEdit)"))
        cb = QComboBox()
        cb.addItems(["Opción 1", "Opción 2", "Opción 3"])
        layout.addWidget(cb)
        layout.addWidget(QCheckBox("Casilla de Verificación (QCheckBox)"))
        layout.addWidget(QRadioButton("Botón de Radio (QRadioButton)"))
        slider = QSlider(Qt.Horizontal)
        slider.setValue(50)
        layout.addWidget(slider)
        prog = QProgressBar()
        prog.setValue(75)
        layout.addWidget(prog)
        layout.addStretch()

    def load_qss_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo QSS", "", "QSS Files (*.qss);;All Files (*)")
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.raw_editor.setPlainText(content)

    def on_raw_text_changed(self):
        if self.updating_ui: return
        self.debounce_timer.start()

    def process_text_change(self):
        content = self.raw_editor.toPlainText()
        if re.search(r':\s*#[0-9a-fA-F]{0,5}$', content):
            return 
        self.current_rules = QSSParser.parse(content)
        self.populate_selectors()
        self.apply_preview(content)

    def generate_qss_with_ai(self):
        api_key = self.api_key_input.text().strip()
        prompt_text = self.prompt_input.toPlainText().strip()
        
        if not api_key:
            self.raw_editor.append("\n/* [ERROR] Por favor ingresa tu API Key de Gemini. */")
            return
        if not prompt_text:
            self.raw_editor.append("\n/* [ERROR] Por favor describe el tema. */")
            return
            
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generando...")
        threading.Thread(target=self._call_gemini_api, args=(api_key, prompt_text)).start()

    def _call_gemini_api(self, api_key, prompt):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json', 'User-Agent': 'FlarmStyler/1.0'}
            system_instruction = "Eres un experto en Qt QSS. Genera código QSS válido para una app moderna."
            full_prompt = f"{system_instruction}\n\nDescripción: {prompt}"
            data = {"contents": [{"parts": [{"text": full_prompt}]}]}
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req, context=ctx) as response:
                result = json.loads(response.read().decode('utf-8'))
                
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text']
                clean_qss = re.sub(r'^```(css|qss)?', '', text, flags=re.MULTILINE)
                clean_qss = re.sub(r'```$', '', clean_qss, flags=re.MULTILINE).strip()
                self.update_editor_signal.emit(clean_qss)
            else:
                self.update_editor_signal.emit("/* La IA no devolvió candidatos válidos. */")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            self.update_editor_signal.emit(f"/* [ERROR API] HTTP {e.code}: {e.reason}\n{error_body} */")
        except Exception as e:
            self.update_editor_signal.emit(f"/* [ERROR] {e} */")
        finally:
            self.generate_btn_signal.emit()

    def _on_update_editor(self, text):
        self.raw_editor.setPlainText(text)
    
    def _on_generate_finished(self):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generar con IA")

    def populate_selectors(self):
        self.updating_ui = True
        self.selector_list.setRowCount(0)
        self.prop_table.setRowCount(0)
        for selector in self.current_rules:
            row = self.selector_list.rowCount()
            self.selector_list.insertRow(row)
            self.selector_list.setItem(row, 0, QTableWidgetItem(selector))
        self.updating_ui = False

    def on_selector_selected(self):
        items = self.selector_list.selectedItems()
        if not items: return
        selector = items[0].text()
        props = self.current_rules.get(selector, {})
        self.updating_ui = True
        self.prop_table.setRowCount(0)
        for key, val in props.items():
            row = self.prop_table.rowCount()
            self.prop_table.insertRow(row)
            self.prop_table.setItem(row, 0, QTableWidgetItem(key))
            self.prop_table.setItem(row, 1, QTableWidgetItem(val))
        self.updating_ui = False

    def on_property_changed(self, item):
        if self.updating_ui: return
        sel_items = self.selector_list.selectedItems()
        if not sel_items: return
        selector = sel_items[0].text()
        row = item.row()
        key_item = self.prop_table.item(row, 0)
        val_item = self.prop_table.item(row, 1)
        if key_item and val_item:
            key = key_item.text()
            val = val_item.text()
            if selector in self.current_rules:
                self.current_rules[selector][key] = val
            self.updating_ui = True
            new_qss = QSSParser.stringify(self.current_rules)
            self.raw_editor.setPlainText(new_qss)
            self.apply_preview(new_qss)
            self.updating_ui = False

    def apply_changes(self):
        self.apply_preview(self.raw_editor.toPlainText())

    def apply_preview(self, qss):
        self.preview_widget.setStyleSheet(qss)

class FlarmStylerWindow(QMainWindow):
    """Ventana principal de Flarm Styler."""
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1100, 750)
        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("CentralWidget")
        self.central_widget.setStyleSheet("""
            #CentralWidget {
                background-color: #202020;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
        """)
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Barra de Título ---
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(16, 0, 0, 0)
        title_bar.setSpacing(0)
        
        app_icon = QSvgWidget("assets/ui/win11_terminal.svg")
        app_icon.setFixedSize(16, 16)
        title_bar.addWidget(app_icon)
        title_bar.addSpacing(12)
        
        title_label = QLabel("Flarm Styler")
        title_label.setFont(QFont("Segoe UI Variable Display", 9))
        title_label.setStyleSheet("color: #FFFFFF;")
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        
        min_btn = TitleBarButton("assets/ui/win11_min.svg")
        min_btn.clicked.connect(self.showMinimized)
        
        self.max_btn = TitleBarButton("assets/ui/win11_max.svg")
        self.max_btn.clicked.connect(self.toggle_maximized)
        
        close_btn = TitleBarButton("assets/ui/win11_close.svg", is_close=True)
        close_btn.clicked.connect(self.close)
        
        title_bar.addWidget(min_btn)
        title_bar.addWidget(self.max_btn)
        title_bar.addWidget(close_btn)
        
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setLayout(title_bar)
        self.title_bar_widget.setFixedHeight(32)
        main_layout.addWidget(self.title_bar_widget)

        # --- Contenido ---
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(10, 10, 10, 10)
        self.qss_modder = QSSModderWidget()
        content_layout.addWidget(self.qss_modder)
        main_layout.addLayout(content_layout)

        self.old_pos = None

    def toggle_maximized(self):
        if self.isMaximized():
            self.showNormal()
            self.central_widget.setStyleSheet("""
                #CentralWidget {
                    background-color: #202020;
                    border: 1px solid #333333;
                    border-radius: 8px;
                }
                QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
            """)
            # Restaurar icono de maximizar
            # self.max_btn.setIcon(QIcon("assets/ui/win11_max.svg")) 
        else:
            self.showMaximized()
            self.central_widget.setStyleSheet("""
                #CentralWidget {
                    background-color: #202020;
                    border: none;
                    border-radius: 0px;
                }
                QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
            """)
            # Cambiar icono a restaurar (si tuviéramos el svg)
            # self.max_btn.setIcon(QIcon("assets/ui/win11_restore.svg"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.y() < 40:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.isMaximized():
                self.central_widget.setStyleSheet("""
                    #CentralWidget {
                        background-color: #202020;
                        border: none;
                        border-radius: 0px;
                    }
                    QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
                """)
            else:
                self.central_widget.setStyleSheet("""
                    #CentralWidget {
                        background-color: #202020;
                        border: 1px solid #333333;
                        border-radius: 8px;
                    }
                    QLabel { color: #FFFFFF; font-family: 'Segoe UI Variable Display'; }
                """)
        super().changeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FlarmStylerWindow()
    window.show()
    sys.exit(app.exec_())
