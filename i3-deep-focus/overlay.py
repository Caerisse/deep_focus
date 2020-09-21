# from PyQt5 import QtGui, QtCore, uic
# from PyQt5 import QtWidgets
# from PyQt5.QtWidgets import QMainWindow, QApplication
#
#
# class Overlay(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         self.setWindowFlags(
#                 QtCore.Qt.WindowStaysOnTopHint |
#                 QtCore.Qt.FramelessWindowHint |
#                 QtCore.Qt.X11BypassWindowManagerHint
#         )
#         self.setGeometry(
#                 QtWidgets.QStyle.alignedRect(
#                         QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
#                         QtCore.QSize(800, 600),
#                         QtWidgets.qApp.desktop().availableGeometry()
#                 ))
#
#     def mousePressEvent(self, event):
#         QtWidgets.qApp.quit()

import tkinter
label = tkinter.Label(text='X', font=('Times','30'), fg='black', bg='white')
label.master.overrideredirect(True)
label.master.geometry("+0+0")
label.master.lift()
label.master.wm_attributes("-topmost", True)
#label.master.wm_attributes("-alpha", 1.0)
#label.master.wm_attributes("-fullscreen", True)
label.pack()
label.mainloop()