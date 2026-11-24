from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QStyle,QApplication
from PySide6.QtGui import QColor
from core.app_state import AppState


class TableModel(QAbstractTableModel):

    def __init__(self):
        super().__init__()
        self.estado = AppState()
        self._all_checked = False
        self._columns = [("Numero Usuario","numero_usuario"), 
                        ("Nombre","nombre_completo"), 
                        ("CURP","curp"), 
                        ("Area","area"), 
                        ("Tipo Usuario","tipo_usuario"),
                        ("Fotografia","fotografia"),
                        ("Fecha Impresion","fecha_impresion"),
                        ("Acciones","acciones")]


    def rowCount(self, parent=QModelIndex()):
        return len(self.estado.datos)

    def columnCount(self, parent=QModelIndex()):
        return len(self._columns)

    def headerData(self, section, orientation, role = Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._columns[section][0]
        else:
            return str(section +1)

    def data(self, index, role = Qt.ItemDataRole.DisplayRole ):
        if not index.isValid():
            return None
        row_num = index.row()
        col_num = index.column()

        data = self.estado.datos[row_num]
        if role == Qt.ItemDataRole.DisplayRole:
    
            if col_num == 0:
                return data.get("numero_usuario",None)

            if col_num == len(self._columns) - 1:
                # La columna de acciones la dibuja el delegado.
                return None

            if not data.get("encontrado",False):
                return None
            
            column_name = self._columns[col_num][1]
        
            if column_name == 'fotografia':
                msg_foto = ""
                if data.get(column_name, None):
                    msg_foto = "✅ Con Foto "
                else:
                    msg_foto = "❌ Sin foto "
                if data.get("remplazo_foto",False):
                    msg_foto =msg_foto + "\t| 🔵 Con remplazo"
                return msg_foto


            if column_name == 'fecha_impresion' and data.get(column_name, None) is None:
                return "S/F"
            
            return data.get(column_name, None)
        elif role == Qt.ItemDataRole.BackgroundRole:
            if not data.get("encontrado",False):
                return QColor(110,2,2,255)

            if data.get("fecha_impresion",None):
                return QColor(1,74,10)
        elif role == Qt.ItemDataRole.ForegroundRole:
            if data.get("fotografia",False):
                return QColor(255,255,255,255)
            else:
                return QColor(0,0,0,255)
        elif role == Qt.ItemDataRole.CheckStateRole:
            if col_num == 0:
                if data.get("checked",False):
                    return Qt.CheckState.Checked
                else:
                    return Qt.CheckState.Unchecked
        else:
            return None
    def flags(self, index):
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.CheckStateRole:
            checked = value == Qt.CheckState.Checked.value
            self.estado.datos[index.row()]["checked"] = checked
            self.dataChanged.emit(index,index,[role])
            return True
        return False

    def toogle_all_checked(self):
        self.beginResetModel()
        for i in range (0,self.rowCount()):
            self.estado.datos[i]["checked"] = self._all_checked
        self.endResetModel()
        self._all_checked = not self._all_checked

    def update_row(self, fila, registro):
        if not 0 <= fila < len(self.estado.datos):
            return False
        self.estado.datos[fila] = registro
        self.dataChanged.emit(
            self.index(fila,0),
            self.index(fila,self.columnCount()-1)
        )
        return True

    def remove_row(self, fila: int) -> bool:
        if not 0 <= fila < len(self.estado.datos):
            return False
        self.beginRemoveRows(QModelIndex(), fila, fila)
        del self.estado.datos[fila]
        self.endRemoveRows()
        return True

    def add_row(self, registro: dict) -> int:
        fila = len(self.estado.datos)
        self.beginInsertRows(QModelIndex(), fila, fila)
        self.estado.datos.append(registro)
        self.endInsertRows()
        return fila
    