import sys
import requests
from pyqt5_plugins.examplebutton import QtWidgets
import guiCode


def get_tickers():  # takes whatever tickers are provided in the tickers file and returns them in a list
    file_path = 'tickers.txt'
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the contents of the file into a list
        lines = file.readlines()
    # remove the newline character from each line
    lines = [line.strip() for line in lines]
    return lines

# Launching Gui
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
goo = guiCode.Ui_MainWindow()
goo.setupUi(MainWindow)
MainWindow.show()
sys.exit(app.exec_())
