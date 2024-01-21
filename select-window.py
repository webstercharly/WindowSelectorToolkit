import pygetwindow as gw
import PySimpleGUI as sg
import numpy as np
import pyautogui
import cv2
import time
from PyQt5 import QtWidgets, QtCore, QtGui

class OverlayWindow(QtWidgets.QWidget):
    def __init__(self, window, parent=None):
        super(OverlayWindow, self).__init__(parent)
        self.window = window
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Start a timer to update the window every 100ms
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)

    def paintEvent(self, event):
        pos = (self.window.left, self.window.top)
        size = (self.window.width, self.window.height)

        top_left = pos
        top_right = (pos[0] + size[0], pos[1])
        bottom_left = (pos[0], pos[1] + size[1])
        bottom_right = (pos[0] + size[0], pos[1] + size[1])
        self.points = [top_left, bottom_left, bottom_right, top_right]

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 2.5))  # Set color and width of points
        for point in self.points:
            painter.drawPoint(*point)

        num_points = len(self.points)
        for i in range(num_points):
            painter.drawLine(QtCore.QPoint(*self.points[i]), QtCore.QPoint(*self.points[(i+1)%num_points]))

        painter.end()

layout = [[sg.Button('Select application', key='select')],
          [sg.Text('Selected window coordinates will be shown here', key='coords')],
          [sg.Image(key='image')]]

window = sg.Window('Select Application', layout)

while True:
    event, values = window.read(timeout=100)
    if event == "Exit" or event == sg.WINDOW_CLOSED:
        break

    if event == 'select':
        sg.popup('Please click on the window you want to select', auto_close=True, auto_close_duration=2)
        time.sleep(2)
        x, y = pyautogui.position()
        selected_window = None
        for win in gw.getAllWindows():
            if win.left < x < win.left + win.width and win.top < y < win.top + win.height:
                selected_window = win
                break
        if selected_window is not None:
            window['coords'].update(f'x start: {selected_window.left}, y start: {selected_window.top}, '
                                    f'x end: {selected_window.left + selected_window.width}, '
                                    f'y end: {selected_window.top + selected_window.height}')
            screenshot = pyautogui.screenshot(region=(selected_window.left, selected_window.top,
                                                      selected_window.width, selected_window.height))
            screenshot_np = np.array(screenshot)
            screenshot_np = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)  # Add this line
            imgbytes = cv2.imencode('.png', screenshot_np)[1].tobytes()

            #screenshot.save('temp.png')
            window['image'].update(data=imgbytes, size=(selected_window.width, selected_window.height))

            # Get the corners of the window
            # top_left = (max(1, selected_window.left), max(1, selected_window.top))
            # top_right = (max(1, selected_window.left + selected_window.width), max(1, selected_window.top))
            # bottom_left = (max(1, selected_window.left), max(1, selected_window.top + selected_window.height))
            # bottom_right = (max(1, selected_window.left + selected_window.width), max(1, selected_window.top + selected_window.height))
            # corners = [top_left, top_right, bottom_left, bottom_right]

            # # Briefly move the mouse to each corner
            # for corner in corners:
            #     pyautogui.moveTo(corner)
            #     time.sleep(1)  # Pause so you can see where the mouse moved

            app = QtWidgets.QApplication([])
            overlay = OverlayWindow(selected_window)
            overlay.showFullScreen()
            app.exec_()

window.close()
