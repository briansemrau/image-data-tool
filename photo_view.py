# Adapted from https://stackoverflow.com/a/74941896

import math

from PySide6 import QtCore, QtGui, QtWidgets
import PySide6.QtGui


class PhotoView(QtWidgets.QGraphicsView):
    photoClicked = QtCore.Signal(QtCore.QPointF)

    def __init__(self, parent=None):
        super(PhotoView, self).__init__(parent)
        self._zoom = 0
        self._drag_mode = QtWidgets.QGraphicsView.DragMode.ScrollHandDrag
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        rect = rect.marginsAdded(QtCore.QMarginsF(rect.width() * 0.05, rect.height() * 0.05, rect.width() * 0.05, rect.height() * 0.05))
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0
            self._on_zoom_changed()

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._drag_mode = QtWidgets.QGraphicsView.DragMode.ScrollHandDrag
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self._drag_mode = QtWidgets.QGraphicsView.DragMode.NoDrag
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()
    
    def getPhotoSize(self):
        if self.hasPhoto():
            return self._photo.pixmap().size()
        return QtCore.QSize(0, 0)

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
                self._on_zoom_changed()
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0
                self._on_zoom_changed()

    def toggleDragMode(self):
        if self._drag_mode != QtWidgets.QGraphicsView.DragMode.NoDrag:
            self._drag_mode = QtWidgets.QGraphicsView.DragMode.NoDrag
        elif not self._photo.pixmap().isNull():
            self._drag_mode = QtWidgets.QGraphicsView.DragMode.ScrollHandDrag

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setDragMode(self._drag_mode)
            super().mousePressEvent(QtGui.QMouseEvent(
                QtCore.QEvent.Type.GraphicsSceneMousePress,
                event.pos(),
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.KeyboardModifier.NoModifier
            ))
            return

        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.position().toPoint()))

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self.mouseReleaseEvent(QtGui.QMouseEvent(
                QtCore.QEvent.Type.GraphicsSceneMouseRelease,
                event.pos(),
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.MouseButton.LeftButton,
                QtCore.Qt.KeyboardModifier.NoModifier
            ))
            return
        super().mouseReleaseEvent(event)

    def _on_zoom_changed(self):
        xform = self.transform()
        scale_factor_x = math.sqrt(xform.m11() * xform.m11() + xform.m12() * xform.m12())
        scale_factor_y = math.sqrt(xform.m21() * xform.m21() + xform.m22() * xform.m22())
        scale = max(scale_factor_x, scale_factor_y)
        if scale < 2.0:
            self._photo.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
        else:
            self._photo.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)


class MaskDrawPhotoView(PhotoView):
    maskModified = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = QtGui.QPixmap()
        self.drawing = False
        self.brushSize = 32
        self.brushColor = QtCore.Qt.GlobalColor.black
        self.last_point = QtCore.QPoint()
        self.history = []
        self.history_index = 0
        self.max_history = 20
        self.draw_enabled = True

    def mousePressEvent(self, event):
        if self.draw_enabled:
            if event.button() in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton):
                self.drawing = True

                painter = QtGui.QPainter(self.canvas)
                color = self.brushColor
                if event.button() == QtCore.Qt.MouseButton.RightButton:
                    color = QtCore.Qt.GlobalColor.white
                    #painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                pos = self.mapToScene(event.pos())
                pen = QtGui.QPen(color, self.brushSize, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen)
                painter.drawPoint(pos)
                painter.end()
                self.last_point = pos

                self.viewport().update()
        
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.draw_enabled:
            if self.drawing and event.buttons() & (QtCore.Qt.MouseButton.LeftButton | QtCore.Qt.MouseButton.RightButton):
                painter = QtGui.QPainter(self.canvas)
                color = self.brushColor
                if event.buttons() & QtCore.Qt.MouseButton.RightButton:
                    color = QtCore.Qt.GlobalColor.white
                    #painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Clear)
                pen = QtGui.QPen(color, self.brushSize, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin)
                pos = self.mapToScene(event.pos())
                painter.setPen(pen)
                painter.drawLine(self.last_point, pos)
                painter.end()
                self.last_point = pos
            
            self.viewport().update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.draw_enabled:
            if event.button() in (QtCore.Qt.MouseButton.LeftButton, QtCore.Qt.MouseButton.RightButton):
                self.drawing = False
                self.last_point = QtCore.QPoint()
                self.record_history()
                self.maskModified.emit()
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        if self.draw_enabled:
            if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                delta = event.angleDelta().y() / 20
                self.brushSize += delta
                self.brushSize = max(1, min(self.brushSize, 256))
                self.viewport().update()
                event.accept()
                return

        super().wheelEvent(event)
    
    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        # draw mask
        painter = QtGui.QPainter(self.viewport())
        painter.setTransform(self.viewportTransform())
        painter.setOpacity(0.9)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Multiply)
        #painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Darken)
        painter.drawPixmap(self.canvas.rect(), self.canvas)
        painter.end()

        # draw a transparent circle around the cursor
        if self.draw_enabled:
            painter = QtGui.QPainter(self.viewport())
            painter.setCompositionMode(QtGui.QPainter.CompositionMode.RasterOp_NotSourceXorDestination)
            draw_width = self.brushSize * self.transform().m11()
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 63), draw_width, QtCore.Qt.PenStyle.SolidLine, QtCore.Qt.PenCapStyle.RoundCap, QtCore.Qt.PenJoinStyle.RoundJoin))
            painter.drawPoint(self.mapFromGlobal(QtGui.QCursor.pos()))
            painter.end()

    def keyPressEvent(self, event):
        if self.draw_enabled:
            if len(self.history) > 0:
                if event.key() == QtCore.Qt.Key.Key_Z and event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
                    if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
                        self.redo()
                    else:
                        self.undo()
                    self.viewport().update()

        super().keyPressEvent(event)
    
    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.canvas = self.history[self.history_index].copy()
            self.maskModified.emit()
            self.viewport().update()

    def redo(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.canvas = self.history[self.history_index].copy()
            self.maskModified.emit()
            self.viewport().update()

    def record_history(self):
        self.history = self.history[:self.history_index+1]
        self.history.append(self.canvas.copy())
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self.history_index = len(self.history) - 1

    def setPhoto(self, pixmap=None):
        super().setPhoto(pixmap)
        self.canvas = QtGui.QPixmap(pixmap.size())
        self.canvas.fill(QtCore.Qt.GlobalColor.white)
        self.history = [self.canvas.copy()]
        self.viewport().update()
    
    def setMask(self, mask):
        if mask is None:
            mask = QtGui.QPixmap(self._photo.pixmap().size())
            mask.fill(QtCore.Qt.GlobalColor.white)
        self.canvas = mask
        self.history = [self.canvas.copy()]
        self.viewport().update()
    
    def getMask(self):
        return self.canvas
    
    def invert_mask(self):
        painter = QtGui.QPainter(self.canvas)
        painter.setCompositionMode(QtGui.QPainter.CompositionMode.CompositionMode_Difference)
        painter.fillRect(self.canvas.rect(), QtCore.Qt.GlobalColor.white)
        painter.end()
        self.viewport().update()
        self.record_history()
    
    def setDrawEnabled(self, enabled):
        self.draw_enabled = enabled
        self.viewport().update()
