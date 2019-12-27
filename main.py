# ======================================================================================================================
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import subprocess
import threading
from time import sleep


# ======================================================================================================================


class MyThread(threading.Thread):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.active = True

    def run(self, ):
        global actions
        global connected

        try:
            while self.active:
                output = subprocess.check_output(["nordvpn", "status"])
                status_connected = "status: connected" in output.decode("utf-8").lower()

                if status_connected and (connected is None or not connected):
                    updateMenu(output)
                    connected = True
                    print('CONNECTED')
                elif not status_connected and (connected is None or connected):
                    updateMenu()
                    connected = False
                    print('DISCONNECTED')

                sleep(5)        # TODO: 5 seconds. Is it enough? Is it too much?
        except Exception as e:
            print(e)
            exit(1)


# ======================================================================================================================

def createSystemTray():
    global app
    global tray
    global menu
    global thr
    global actions

    # ------------------------------------------------------
    # Application:
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    # ------------------------------------------------------
    # Icon:
    tray = QSystemTrayIcon()
    tray.setIcon(QIcon("./nordvpn-icon.png"))
    tray.setVisible(True)

    # ------------------------------------------------------
    # Menu:
    menu = QMenu()

    # ------------------------------------------------------
    # NordVPN Items on Menu:
    for dic in actions.values():
        action = dic["action"]
        action.triggered.connect(dic["target"])
        action.setEnabled(False)
        menu.addAction(action)

    # ------------------------------------------------------
    # Last Item on Menu:
    exitAction = QAction("&Exit")
    exitAction.triggered.connect(exitPressed)
    menu.addAction(exitAction)

    # ------------------------------------------------------
    # Add Menu:
    tray.setContextMenu(menu)

    # ------------------------------------------------------
    thr = MyThread()
    thr.start()

    # ------------------------------------------------------
    app.exec_()


def fastConnectPressed():
    # TODO: Loading Icon

    if not connected:
        try:
            print("Trying to connect...")
            output = subprocess.check_output(["nordvpn", "connect"])
            updateMenu(output)
        except subprocess.CalledProcessError as err:
            print("ERROR", err)
            # TODO: Notification
    else:
        print("Already connected")


def disconnectPressed():
    # TODO: Loading Icon

    if connected:
        try:
            print("Trying to disconnect...")
            subprocess.check_output(["nordvpn", "disconnect"])
            updateMenu()
        except subprocess.CalledProcessError as err:
            print("ERROR", err)
            # TODO: Notification
    else:
        print("Is not connected")


def exitPressed():
    # TODO: Loading Icon
    global thr

    thr.active = False
    exit(0)


def updateMenu(tooltip_txt=None):
    if tooltip_txt:
        tray.setIcon(QIcon("./nordvpn-icon.png"))
        actions["Quick Connect"]["action"].setEnabled(False)
        actions["Disconnect"]["action"].setEnabled(True)
        tray.setToolTip(tooltip_txt.decode("utf-8"))
    else:
        tray.setIcon(QIcon("./nordvpn-icon-gray.png"))
        actions["Quick Connect"]["action"].setEnabled(True)
        actions["Disconnect"]["action"].setEnabled(False)
        tray.setToolTip("Disconnected")

# ======================================================================================================================


app = None
tray = None
menu = None
thr = None
connected = None
actions = {
    "Quick Connect": {
        "action": QAction("Quick Connect"),
        "target": fastConnectPressed,
    },
    "Disconnect": {
        "action": QAction("Disconnect"),
        "target": disconnectPressed,
    },
}

# ======================================================================================================================


if __name__ == "__main__":
    createSystemTray()


# ======================================================================================================================
