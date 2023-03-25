import sys
import pyps4controller
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton

# Initialize pygame
pygame.init()

# Create the application
app = QApplication(sys.argv)

# Create a window
window = QWidget()
window.setWindowTitle('PyQt5 and PyPS4Controller Game')
window.set