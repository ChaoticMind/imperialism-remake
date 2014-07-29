# Imperialism remake
# Copyright (C) 2014 Trilarion
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from PySide import QtCore, QtGui

"""
    Graphics (Qt) based objects and algorithms that do not depend specifically on the project but only on Qt.

    Abstraction of the used elements in the project to achieve an intermediate layer and to minimize dependencies.
"""

class Relative_Positioner():
    def __init__(self, x=(0, 0, 0), y=(0, 0, 0)):
        self.x = x
        self.y = y

    def south(self, gap):
        self.y = (1, -1, -gap)
        return self

    def north(self, gap):
        self.y = (0, 0, gap)
        return self

    def west(self, gap):
        self.x = (0, 0, gap)
        return self

    def east(self, gap):
        self.x = (1, -1, -gap)
        return self

    def centerH(self):
        self.x = (0.5, -0.5, 0)
        return self

    def centerV(self):
        self.y = (0.5, -0.5, 0)
        return self

    def calculate(self, parent_rect, own_size):
        pos_x = parent_rect.x() + self.x[0] * parent_rect.width() + self.x[1] * own_size.width() + self.x[2]
        pos_y = parent_rect.y() + self.y[0] * parent_rect.height() + self.y[1] * own_size.height() + self.y[2]
        return QtCore.QPoint(pos_x, pos_y)


class Notification(QtCore.QObject):
    finished = QtCore.Signal()

    def __init__(self, parent, content, fade_duration=2000, stay_duration=2000, positioner=None):
        super().__init__()

        # create a clickable widget as standalone window and without a frame
        self.widget = QtGui.QWidget(parent, QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)

        # widget must be translucent, otherwise when setting semi-transparent background colors
        self.widget.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # replace content by QLabel if content is a string
        if isinstance(content, str):
            content = QtGui.QLabel(content)
            content.setObjectName('notification')

        # set background
        layout = QtGui.QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(content)

        # fade in animation
        self.fade_in = QtCore.QPropertyAnimation(self.widget, 'windowOpacity')
        self.fade_in.setDuration(fade_duration)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1)

        # fading out and waiting for fading out makes only sense if a positive stay_duration has been given
        if stay_duration > 0:
            # fade out animation
            self.fade_out = QtCore.QPropertyAnimation(self.widget, 'windowOpacity')
            self.fade_out.setDuration(fade_duration)
            self.fade_out.setStartValue(1)
            self.fade_out.setEndValue(0)
            # when fade out has finished, emit finished
            self.fade_out.finished.connect(self.finished.emit)

            # timer for fading out animation
            self.timer = QtCore.QTimer()
            self.timer.setSingleShot(True)
            self.timer.setInterval(stay_duration)
            self.timer.timeout.connect(self.fade_out.start)

            # start the timer as soon as the fading in animation has finished
            self.fade_in.finished.connect(self.timer.start)

        # to avoid short blinking show transparent and start animation
        # self.widget.setWindowOpacity(0)

        # if given, set a position
        if parent and positioner:
            position = positioner.calculate(parent.geometry(), content.sizeHint())
            self.widget.move(position)

    def show(self):
        # show and start fade in
        self.widget.show()
        self.fade_in.start()


class RelativeLayoutConstraint():
    def __init__(self, x=(0, 0, 0), y=(0, 0, 0)):
        self.x = x
        self.y = y

    def south(self, gap):
        self.y = (1, -1, -gap)
        return self

    def north(self, gap):
        self.y = (0, 0, gap)
        return self

    def west(self, gap):
        self.x = (0, 0, gap)
        return self

    def east(self, gap):
        self.x = (1, -1, -gap)
        return self

    def centerH(self):
        self.x = (0.5, -0.5, 0)
        return self

    def centerV(self):
        self.y = (0.5, -0.5, 0)
        return self


class RelativeLayout(QtGui.QLayout):
    def __init__(self, *args):
        super().__init__(*args)
        self.setContentsMargins(0, 0, 0, 0)
        self.items = []

    def addItem(self, item):
        if item.widget() is None or not hasattr(item.widget(), 'layout_constraint'):
            raise RuntimeError('Only add widgets (with attribute position_constraint).')
        self.items.append(item)

    def sizeHint(self):
        return self.minimumSize()

    def setGeometry(self, rect):
        for item in self.items:
            o_size = item.sizeHint()

            c = item.widget().layout_constraint

            x = rect.x() + c.x[0] * rect.width() + c.x[1] * o_size.width() + c.x[2]
            y = rect.y() + c.y[0] * rect.height() + c.y[1] * o_size.height() + c.y[2]

            item.setGeometry(QtCore.QRect(x, y, o_size.width(), o_size.height()))

    def itemAt(self, index):
        if index < len(self.items):
            return self.items[index]
        else:
            return None

    def takeAt(self, index):
        return self.items.pop(index)

    def minimumSize(self):
        min_width = 0
        min_height = 0

        for item in self.items:
            o_size = item.sizeHint()

            c = item.widget().layout_constraint
            gap_x = abs(c.x[2])
            gap_y = abs(c.y[2])

            min_width = max(min_width, o_size.width() + gap_x)
            min_height = max(min_height, o_size.height() + gap_y)

        return QtCore.QSize(min_width, min_height)


class FadeAnimation():
    def __init__(self, graphics_item, duration):
        # create opacity effect
        self.effect = QtGui.QGraphicsOpacityEffect()
        self.effect.setOpacity(0)
        graphics_item.setGraphicsEffect(self.effect)

        # create animation
        self.animation = QtCore.QPropertyAnimation(self.effect, 'opacity')
        self.animation.setDuration(duration)  # in ms
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

    def fade_in(self):
        self.animation.setDirection(QtCore.QAbstractAnimation.Forward)
        self.animation.start()

    def fade_out(self):
        self.animation.setDirection(QtCore.QAbstractAnimation.Backward)
        self.animation.start()


class GraphicsItemSet():
    """
        A set (internally a list because a list might be less overhead) of QGraphicsItem elements.
        Some collective actions are possible like setting a Z-value to each of them.
    """

    def __init__(self):
        self.content = []

    def add_item(self, item):
        """
            item -- QGraphicsItem
        """
        if not isinstance(item, QtGui.QGraphicsItem):
            raise RuntimeError('Expected instance of QGraphicsItem!')
        self.content.append(item)

    def set_level(self, level):
        """

        """
        for item in self.content:
            item.setZValue(level)


class ZStackingManager():
    """

    """

    def __init__(self):
        self.floors = []

    def new_floor(self, floor=None, above=True):
        """

        """
        # if a floor is given, it should exist
        if floor and floor not in self.floors:
            raise RuntimeError('Specified floor unknown!')
        if floor:
            # insert above or below the given floor
            insert_position = self.floors.index(floor) + (1 if above else 0)
        else:
            # insert at the end or the beginning of the floors
            insert_position = len(self.floors) if above else 0
        # create new floor, insert in list and return it
        new_floor = GraphicsItemSet()
        self.floors.insert(insert_position, new_floor)
        return new_floor

    def stack(self):
        """

        """
        for z in range(0, len(self.floors)):
            self.floors[z].set_level(z)


class ZoomableGraphicsView(QtGui.QGraphicsView):
    ScaleFactor = 1.15
    MinScaling = 0.5
    MaxScaling = 2

    def __init__(self, *args):
        super().__init__(*args)
        self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)

    def wheelEvent(self, event):
        current_scale = self.transform().m11()  # horizontal scaling factor = vertical scaling factor
        if event.delta() > 0:
            f = ZoomableGraphicsView.ScaleFactor
            if current_scale * f > ZoomableGraphicsView.MaxScaling:
                return
        else:
            f = 1 / ZoomableGraphicsView.ScaleFactor
            if current_scale * f < ZoomableGraphicsView.MinScaling:
                return
        self.scale(f, f)

def makeWidgetClickable(parent):
    """
        Takes any QtGui.QWidget derived class and emits a signal emitting on mousePressEvent.
    """
    class ClickableWidgetSubclass(parent):
        clicked = QtCore.Signal(QtGui.QMouseEvent)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            self.clicked.emit(event)

    return ClickableWidgetSubclass

def makeDraggableWidget(parent):
    """
        Takes any QtGui.QWidget derived class and emits a signal on mouseMoveEvent emitting the position change since
        the last mousePressEvent. By default mouseMoveEvents are only invoked while the mouse is pressed. Therefore
        we can use it to listen to dragging or implement dragging.
    """
    class DraggableWidgetSubclass(parent):
        dragged = QtCore.Signal(QtCore.QPoint)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def mousePressEvent(self, event):
            super().mousePressEvent(event)
            self.position_on_click = event.globalPos()

        def mouseMoveEvent(self, event):
            super().mouseMoveEvent(event)
            position_now = event.globalPos()
            self.dragged.emit(position_now - self.position_on_click)
            self.position_on_click = position_now

    return DraggableWidgetSubclass

def makeClickableGraphicsItem(parent):
    """
        Takes a QtGui.QGraphicsItem and adds signals for entering, leaving and clicking on the item. For this the item
        must have setAcceptHoverEvents and it must also inherit from QObject to have signals. Only use it when really
        needed because there is some performance hit attached.
    """
    class ClickableGraphicsItem(parent, QtCore.QObject):
        entered = QtCore.Signal(QtGui.QGraphicsSceneHoverEvent)
        left = QtCore.Signal(QtGui.QGraphicsSceneHoverEvent)
        clicked = QtCore.Signal(QtGui.QGraphicsSceneMouseEvent)

        def __init__(self, *args, **kwargs):
            parent.__init__(self, *args, **kwargs)
            QtCore.QObject.__init__(self)
            self.setAcceptHoverEvents(True)
            self.setAcceptedMouseButtons(QtCore.Qt.LeftButton)

        def hoverEnterEvent(self, event):
            self.entered.emit(event)

        def hoverLeaveEvent(self, event):
            self.left.emit(event)

        def mousePressEvent(self, event):
            self.clicked.emit(event)

    return ClickableGraphicsItem

# Some classes we need (just to make the naming clear), Name will be used in Stylesheet selectors
DraggableToolBar = makeDraggableWidget(QtGui.QToolBar)
ClickableWidget = makeWidgetClickable(QtGui.QWidget)
ClickablePixmapItem = makeClickableGraphicsItem(QtGui.QGraphicsPixmapItem)