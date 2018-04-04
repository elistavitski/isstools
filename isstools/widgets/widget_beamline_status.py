from PyQt5 import uic, QtCore, QtWidgets
import pkg_resources


from isstools.dialogs import UpdateUserDialog


ui_path = pkg_resources.resource_filename('isstools', 'ui/ui_beamline_status.ui')


class UIBeamlineStatus(*uic.loadUiType(ui_path)):
    shutters_sig = QtCore.pyqtSignal()
    def __init__(self,
                 shutters={},
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.setupUi(self)
        # Initialize Ophyd elements
        self.shutters_sig.connect(self.change_shutter_color)
        self.shutters = shutters


        self.shutters_buttons = []
        for key, item in zip(self.shutters.keys(), self.shutters.items()):
            self.shutter_layout = QtWidgets.QVBoxLayout()

            label = QtWidgets.QLabel(key)
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.shutter_layout.addWidget(label)
            label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

            button = QtWidgets.QPushButton('')
            button.setFixedSize(self.height() * 0.5, self.height() * 0.5)
            self.shutter_layout.addWidget(button)
            # button.setSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)

            self.horizontalLayout_shutters.addLayout(self.shutter_layout)

            self.shutters_buttons.append(button)
            button.setFixedWidth(button.height() * 1.2)
            QtCore.QCoreApplication.processEvents()

            if hasattr(item[1].state, 'subscribe'):
                item[1].button = button
                item[1].state.subscribe(self.update_shutter)

                def toggle_shutter_call(shutter):
                    def toggle_shutter():
                        if int(shutter.state.value):
                            shutter.open()
                        else:
                            shutter.close()

                    return toggle_shutter

                button.clicked.connect(toggle_shutter_call(item[1]))

                if item[1].state.value == 0:
                    button.setStyleSheet("background-color: lime")
                else:
                    button.setStyleSheet("background-color: red")

            elif hasattr(item[1], 'subscribe'):
                item[1].output.parent.button = button
                item[1].subscribe(self.update_shutter)

                def toggle_shutter_call(shutter):
                    def toggle_shutter():
                        if shutter.state == 'closed':
                            shutter.open()
                        else:
                            shutter.close()

                    return toggle_shutter

                if item[1].state == 'closed':
                    button.setStyleSheet("background-color: red")
                elif item[1].state == 'open':
                    button.setStyleSheet("background-color: lime")

                button.clicked.connect(toggle_shutter_call(item[1]))

        if self.horizontalLayout_shutters.count() <= 1:
            self.groupBox_shutters.setVisible(False)

    def update_shutter(self, pvname=None, value=None, char_value=None, **kwargs):
        if 'obj' in kwargs.keys():
            if hasattr(kwargs['obj'].parent, 'button'):
                self.current_button = kwargs['obj'].parent.button

                if int(value) == 0:
                    self.current_button_color = 'lime'
                elif int(value) == 1:
                    self.current_button_color = 'red'

                self.shutters_sig.emit()

    def change_shutter_color(self):
        self.current_button.setStyleSheet("background-color: " + self.current_button_color)