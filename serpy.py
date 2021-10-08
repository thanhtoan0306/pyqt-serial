# importing libraries
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QComboBox
from PyQt5.QtCore import QSize, QRect , QTimer, QTime, Qt, QThread, pyqtSignal

# import time
import sys
import serial
import serial.tools.list_ports

rc=''
i=0

ports = serial.tools.list_ports.comports()
list_com = []
m = ""
for p in ports:	
	m = p.device
	list_com.append(m)

commPort = p.device	
ser = serial.Serial(commPort, baudrate = 115200, timeout = 1)
		
def turnOnLED():
	ser.write(b't')
		
def turnOffLED():
	ser.write(b'o')	

def invertLED():
	ser.write(b'q')

class TestThread(QThread):
	serialUpdate = pyqtSignal(str)
	def run(self):
		while ser.is_open:
			QThread.sleep(1)			
			value = ser.readline().decode()
			self.serialUpdate.emit(value)
			ser.flush()

class Window(QMainWindow):

	def __init__(self):
		super().__init__()

		self.thread = TestThread(self)
		self.thread.serialUpdate.connect(self.handleSerialUpdate)
		self.thread.start()

		self.setWindowIcon(QtGui.QIcon('C:/Users/Toanpc/Desktop/waste/logo2.png'))

		# setting title
		self.setWindowTitle("Serial Command ")

		#toa do xuat phat (500,100) col_w =360; row_w = 500
		self.setGeometry(300, 100, 550, 400)

		# calling method
		self.UiComponents()

		# showing all the widgets
		self.show()


	#close gui safely
	def closeEvent(self, event):
		#Your desired functionality here
		self.thread.terminate()
		sys.exit(0)

		

		# method for widgets
	def UiComponents(self):

		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		# creating combo_box_com widget
		self.combo_box_com = QComboBox(self)

		# setting geometry of combo_box_com
		self.combo_box_com.setGeometry(10, 310, 145, 40)

		# adding list of items to combo_box_com
		self.combo_box_com.addItems(list_com)

		# setting default item
		self.combo_box_com.setCurrentText(commPort)

		# action of combo box
		self.combo_box_com.activated.connect(self.refresh_port)
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		# creating a combo_box_baud widget
		self.combo_box_baud = QComboBox(self)

		# setting geometry of combo_box_baud
		self.combo_box_baud.setGeometry(200, 310, 160, 40)

        # baud list
		baud_list = ["9600", "115200","230400"]

		# adding list of items to combo_box_baud
		self.combo_box_baud.addItems(baud_list)

		# setting default item
		self.combo_box_baud.setCurrentText("115200")

		# action of combo box
		self.combo_box_baud.activated.connect(self.refresh_port)
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		# creating a QLineEdit object
		self.line_send = QLineEdit("", self)
		# setting geometry
		self.line_send.setGeometry(10, 10, 350, 40)
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

		#vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
		# creating a label
		self.label_r = QLabel(self)

		# setting geometry to the label
		self.label_r.setGeometry(10, 70, 350, 200)

		# creating label multi line
		self.label_r.setWordWrap(True)

		# setting style sheet to the label
		self.label_r.setStyleSheet("QLabel"
								"{"
								"border : 1px solid black;"
								"background : white;"
								"}")

		# setting alignment to the label
		self.label_r.setAlignment(Qt.AlignLeft)	
		#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

		# send button
		push_send = QPushButton("Send", self)
		push_send.setGeometry(380, 10, 145, 40)
		push_send.clicked.connect(self.sendData) 

		# Toggle button
		push_toggle = QPushButton("Toggle", self)
		push_toggle.setGeometry(380, 70, 145, 40)
		push_toggle.clicked.connect(invertLED) 
		
		# On button
		push_on = QPushButton("On", self)
		push_on.setGeometry(380, 120, 70, 40) 
		push_on.clicked.connect(turnOnLED)				

		# Off button
		push_off = QPushButton("Off", self)
		push_off.setGeometry(455, 120, 70, 40)
		push_off.clicked.connect(turnOffLED)

        # clear button
		push_clear = QPushButton("Clear", self)
		push_clear.setGeometry(380, 310, 145, 40)
		push_clear.clicked.connect(self.clearData)

	def refresh_port(self):
		global 	com_content, baud_content, ser
		com_content = self.combo_box_com.currentText()
		baud_content = self.combo_box_baud.currentText()
		ser.close()
		ser = serial.Serial(com_content, baudrate = baud_content, timeout = 1)

	def clearData(self):
		global rc, i
		rc=''
		i=0
		self.label_r.setText(rc)


	def sendData(self):
		cr = self.line_send.text()
		ser.write(cr.encode())
		self.line_send.setText("") 	#Set text to null
		self.line_send.setFocus() 	#Set cursor to default


	def handleSerialUpdate(self, value):
		if value != '':				
			current_time = QTime.currentTime()
			# converting QTime object to string
			label_time = current_time.toString('hh:mm:ss:zzz>>')
			global rc, i
			rc = rc  + label_time + value #data receive			
			i = rc.count('\n')	#count lines of label_r 
			if i > 14: #if line ==15 then reset line
				i = 0
				rc = label_time + value + '\n'
			self.label_r.setText(rc)
			self.label_r.setWordWrap(True)


# create pyqt5 app
App = QApplication(sys.argv)

# create the instance of our Window
window = Window()

# start the app
sys.exit(App.exec())

