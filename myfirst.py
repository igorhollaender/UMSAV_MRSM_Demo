# myfirst
#
# For Qt, see
# https://www.pythonguis.com/tutorials/creating-your-first-pyqt-window/

# IH's tips and tricks
# to activate venv, use (in PowerShell terminal)
#    Set-ExecutionPolicy AllSigned -Scope CurrentUser
#    .\.venv\Scripts\activate

# to install packages in virtual env, use something like
#   (.venv) PS C:\Users\igorh\OneDrive\Dokumente\Igor\UMSAV\Python sandbox>   python -m pip install pyqt5 
# see https://stackoverflow.com/questions/39630944/python-cant-find-packages-in-virtual-environment

#

# 
# this was added from my other working environment  240715 12:30PM

from PyQt6.QtWidgets import     \
        QApplication,           \
        QWidget,                \
        QPushButton         


# Only needed for access to command line arguments
import sys



#aaa
def quit_clicked():
    QApplication.quit()

# You need one (and only one) QApplication instance per application.
# Pass in sys.argv to allow command line arguments for your app.
# If you know you won't use command line arguments QApplication([]) works too.
app = QApplication(sys.argv)

# Create a Qt widget, which will be our window.
window = QWidget()

b = QPushButton("QUIT",window)
b.clicked.connect(quit_clicked)
b.setGeometry(1000,100,300,100)

#bla bla bla

# window.show()  # IMPORTANT!!!!! Windows are hidden by default.
window.showFullScreen()

# Start the event loop.
app.exec()

