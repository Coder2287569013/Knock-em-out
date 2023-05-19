from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit
app = QApplication([])
app_win = QWidget()
app_win.resize(50,50)
app_win.setWindowTitle("Name")
app_win.show()
text, ok = QInputDialog.getText(None, "Get Name", "Your name:", QLineEdit.Normal, "")
if ok:
	app_win.close()