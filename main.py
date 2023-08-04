import os
import sys

from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtCore import *
from PySide6.QtGui import *
import PySide6.QtGui
from PySide6.QtWidgets import *

import send2trash

from photo_view import PhotoView, MaskDrawPhotoView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Dataset Tool 🎨")
        
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        # Header

        self.header_layout = QHBoxLayout()
        self.layout.addLayout(self.header_layout)

        self.image_title = QLabel()
        self.image_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_layout.addWidget(self.image_title)

        self.trash_button = QPushButton("🗑️")
        self.trash_button.clicked.connect(self.delete_image)
        self.trash_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.trash_button.setMaximumSize(40, 40)
        self.trash_button.setShortcut(QKeySequence("Delete"))
        self.trash_button.setToolTip("Delete image")
        self.trash_button.setStyleSheet("background-color: red")
        self.header_layout.addWidget(self.trash_button)

        # Mode selection

        # self.radio_button_layout = QHBoxLayout()
        # self.layout.addLayout(self.radio_button_layout)
        # self.mode_buttons = []

        # self.caption_mode_button = QPushButton()
        # self.caption_mode_button.setCheckable(True)
        # self.caption_mode_button.setText("📰")
        # self.caption_mode_button.setToolTip('Enable Caption Editing')
        # self.caption_mode_button.clicked.connect(partial(self.select_mode, "caption", self.caption_mode_button))
        # self.radio_button_layout.addWidget(self.caption_mode_button)
        # self.mode_buttons.append(self.caption_mode_button)

        # self.mask_mode_button = QPushButton()
        # self.mask_mode_button.setCheckable(True)
        # self.mask_mode_button.setText("🎨")
        # self.mask_mode_button.setToolTip('Enable Mask Editing')
        # self.mask_mode_button.clicked.connect(partial(self.select_mode, "mask", self.mask_mode_button))
        # self.radio_button_layout.addWidget(self.mask_mode_button)
        # self.mode_buttons.append(self.mask_mode_button)

        # self.radio_button_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding))

        # Image view

        self.image_view = MaskDrawPhotoView()
        self.image_view.maskModified.connect(self.on_mask_modified)
        self.layout.addWidget(self.image_view)

        self.allow_autosave = True

        # Image annotations
        
        self.image_caption = QPlainTextEdit()
        self.image_caption.setPlaceholderText("A photograph of a ...")
        self.image_caption.setMaximumHeight(92)
        self.image_caption.textChanged.connect(self.on_caption_changed)
        self.layout.addWidget(self.image_caption)

        self.image_tags = QPlainTextEdit()
        self.image_tags.setPlaceholderText("vector art, red highlights, ...")
        self.image_tags.setMaximumHeight(76)
        self.image_tags.textChanged.connect(self.on_tags_changed)
        self.layout.addWidget(self.image_tags)

        self.create_annotation_button_layout = QHBoxLayout()
        self.layout.addLayout(self.create_annotation_button_layout)

        self.create_caption_button = QPushButton("Add Caption 📝")
        self.create_caption_button.clicked.connect(self.create_caption)
        self.create_caption_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.create_annotation_button_layout.addWidget(self.create_caption_button)

        self.create_tags_button = QPushButton("Add Tags 🏷️")
        self.create_tags_button.clicked.connect(self.create_tags)
        self.create_tags_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.create_annotation_button_layout.addWidget(self.create_tags_button)

        # Navigation

        self.layout.addItem(QSpacerItem(0, 10))

        self.nav_button_layout = QHBoxLayout()
        self.layout.addLayout(self.nav_button_layout)

        self.prev_button = QPushButton("Previous (Ctrl+Left)")
        self.prev_button.setShortcut(QKeySequence("Ctrl+Left"))
        self.prev_button.clicked.connect(self.prev_image)
        self.prev_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.prev_button.setMinimumHeight(40)
        self.nav_button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("Next (Ctrl+Right)")
        self.next_button.setShortcut(QKeySequence("Ctrl+Right"))
        self.next_button.clicked.connect(self.next_image)
        self.next_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.next_button.setMinimumHeight(40)
        self.nav_button_layout.addWidget(self.next_button)

        # Menu bar

        self.menu_bar = QMenuBar()
        self.setMenuBar(self.menu_bar)

        self.file_menu = QMenu("File", self)
        self.menu_bar.addMenu(self.file_menu)
        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.triggered.connect(self.open_folder)
        self.file_menu.addAction(self.open_folder_action)

        self.set_image_index_action = QAction("Select Image Index", self)
        self.set_image_index_action.setShortcut(QKeySequence("Ctrl+I"))
        self.set_image_index_action.triggered.connect(self.set_image_index)
        self.file_menu.addAction(self.set_image_index_action)

        self.mask_menu = QMenu("Mask", self)
        self.menu_bar.addMenu(self.mask_menu)

        self.clear_mask_action = QAction("Clear Mask", self)
        #self.clear_mask_action.setShortcut(QKeySequence("Ctrl+M"))
        self.clear_mask_action.triggered.connect(partial(self.image_view.setMask, None))
        self.mask_menu.addAction(self.clear_mask_action)

        self.invert_mask_action = QAction("Invert Mask", self)
        self.invert_mask_action.setShortcut(QKeySequence("Ctrl+Shift+M"))
        self.invert_mask_action.triggered.connect(self.image_view.invert_mask)
        self.mask_menu.addAction(self.invert_mask_action)

        self.images = []
        self.current_image = 0

        #self.select_mode("caption", self.caption_mode_button)  # reset to consistent state
        self.open_folder("./example_dataset")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.BackButton:
            self.prev_image()
            event.accept()
            return
        elif event.button() == Qt.MouseButton.ForwardButton:
            self.next_image()
            event.accept()
            return
        super().mousePressEvent(event)

    def open_folder(self, path=None):
        folder_path = path if path else QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.images = []
            self.current_image = 0
            for file_name in os.listdir(folder_path):
                if file_name.endswith(('.png', '.jpg', '.jpeg')):
                    self.images.append(os.path.join(folder_path, file_name))
            self.display_image()

    def select_mode(self, mode, button):
        checked = button.isChecked()
        if not checked:
            mode = None
        for other_button in self.mode_buttons:
            if other_button != button:
                other_button.setChecked(False)
        if mode == "caption":
            self.caption_mode_button.setChecked(True)
        elif mode == "mask":
            self.mask_mode_button.setChecked(True)
        self.create_caption_button.setEnabled(mode == "caption")
        self.create_tags_button.setEnabled(mode == "caption")
        self.image_caption.setEnabled(mode == "caption")
        self.image_tags.setEnabled(mode == "caption")
        self.image_view.setDrawEnabled(mode == "mask")

    def display_image(self):
        if not self.images:
            return
        self.allow_autosave = False
        pixmap = QPixmap(self.images[self.current_image])
        image_name = os.path.basename(self.images[self.current_image])
        image_filesize_text = sizeof_fmt(os.path.getsize(self.images[self.current_image]))
        if pixmap.isNull():
            self.image_view.setPhoto(None)
            self.image_title.setText(f"{image_name}\nError loading image    {image_filesize_text}")
        else:
            self.image_view.setPhoto(pixmap)
            aspect_text = aspect_fmt(pixmap.width(), pixmap.height())
            size_text = f"{pixmap.width()}x{pixmap.height()}"
            self.image_title.setText(f"{image_name}    ({self.current_image + 1}/{len(self.images)})\n{size_text} {aspect_text}    {image_filesize_text}")

        mask_file = os.path.join(os.path.join(os.path.dirname(self.images[self.current_image]), "mask/"), os.path.basename(self.images[self.current_image]))
        if os.path.exists(mask_file):
            self.image_view.setMask(QPixmap(mask_file))
        self.display_annotations()
        self.allow_autosave = True

    def display_annotations(self):
        if not self.images:
            return
        self.allow_autosave = False
        self.image_caption.setVisible(False)
        self.image_caption.setPlainText("")
        self.create_caption_button.setVisible(True)
        self.image_tags.setVisible(False)
        self.image_tags.setPlainText("")
        self.create_tags_button.setVisible(True)
        for ext in (".txt", ".caption"):
            caption_file = os.path.splitext(self.images[self.current_image])[0] + ext
            if os.path.exists(caption_file):
                with open(caption_file) as f:
                    self.image_caption.setPlainText(f.read())
                    self.image_caption.setVisible(True)
                    self.create_caption_button.setVisible(False)
                    break
        for ext in (".tag", ".tags"):
            caption_file = os.path.splitext(self.images[self.current_image])[0] + ext
            if os.path.exists(caption_file):
                with open(caption_file) as f:
                    self.image_tags.setPlainText(f.read())
                    self.image_tags.setVisible(True)
                    self.create_tags_button.setVisible(False)
                    break
        self.allow_autosave = True

    def set_image_index(self):
        index, ok = QInputDialog.getInt(self, "Set Current Image Index", "Index:", self.current_image, 0, len(self.images) - 1)
        if ok:
            self.current_image = index + 1
            self.display_image()

    def create_caption(self):
        if not self.images:
            return
        caption_file = os.path.splitext(self.images[self.current_image])[0] + ".txt"
        if not os.path.exists(caption_file):
            with open(caption_file, "w") as f:
                f.write("")
        self.display_annotations()
    
    def on_caption_changed(self):
        # doc_height = min(max(self.image_caption.document().size().height(), 2), 5)
        # text_row_height = self.image_caption.fontMetrics().height()
        
        # content_margin = self.image_caption.contentsMargins().top() + self.image_caption.contentsMargins().bottom()
        # #print(doc_height, text_row_height, content_margin)
        # print(self.image_caption.contentsMargins().top(), self.image_caption.contentsMargins().bottom())
        # self.image_caption.setFixedHeight(doc_height * text_row_height + content_margin)
    
        if not self.images or not self.allow_autosave:
            return
        caption_file = os.path.splitext(self.images[self.current_image])[0] + ".txt"
        with open(caption_file, "w") as f:
            f.write(self.image_caption.toPlainText())
    
    def create_tags(self):
        if not self.images:
            return
        caption_file = os.path.splitext(self.images[self.current_image])[0] + ".tag"
        if not os.path.exists(caption_file):
            with open(caption_file, "w") as f:
                f.write("")
        self.display_annotations()

    def on_tags_changed(self):
        if not self.images or not self.allow_autosave:
            return
        caption_file = os.path.splitext(self.images[self.current_image])[0] + ".tag"
        with open(caption_file, "w") as f:
            f.write(self.image_tags.toPlainText())
    
    def on_mask_modified(self):
        if not self.images or not self.allow_autosave:
            return
        image_dir = os.path.dirname(self.images[self.current_image])
        mask_dir = os.path.join(image_dir, "mask/")
        mask_file = os.path.join(mask_dir, os.path.basename(self.images[self.current_image]))
        mask = self.image_view.getMask()
        # check if mask is total transparency
        # TODO so we can delete it if it's empty
        #mask.toImage
        if not os.path.exists(mask_dir):
            os.makedirs(mask_dir)
        mask.save(mask_file)

    def next_image(self):
        if not self.images:
            return
        self.current_image = self.current_image + 1
        if self.current_image >= len(self.images):
            self.current_image = 0
            QApplication.beep()
        self.display_image()

    def prev_image(self):
        if not self.images:
            return
        self.current_image = self.current_image - 1
        if self.current_image < 0:
            self.current_image = len(self.images) - 1
            QApplication.beep()
        self.display_image()

    def delete_image(self):
        if not self.images:
            return
        paths = [
            self.images[self.current_image],
            os.path.splitext(self.images[self.current_image])[0] + ".txt",
            os.path.splitext(self.images[self.current_image])[0] + ".tag",
        ]
        for path in paths:
            if not os.path.exists(path):
                continue
            normalized_path = os.path.normpath(path)
            print(f"Deleting {normalized_path}")
            
            send2trash.send2trash(normalized_path)
        self.images.pop(self.current_image)
        self.current_image = min(self.current_image, len(self.images) - 1)
        self.display_image()


def sizeof_fmt(num, suffix="B") -> str:
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def aspect_fmt(width, height) -> str:
    aspect = width / height
    common_ratios = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5), (9, 16), (9, 21), (10, 16)]
    common_ratios = [*common_ratios, *((r[1], r[0]) for r in common_ratios)]
    closest_ratio = min(common_ratios, key=lambda r: abs(r[0] / r[1] - aspect))
    aspect_text = f"({closest_ratio[0]}:{closest_ratio[1]})"
    # check if the closest ratio is close enough to the actual ratio
    if abs(closest_ratio[0] / closest_ratio[1] - aspect) > 0.05:
        if aspect > 1:
            closest_ratio = (closest_ratio[0], closest_ratio[0] / aspect)
        else:
            closest_ratio = (closest_ratio[1] * aspect, closest_ratio[1])
            
        aspect_text = f"(~{closest_ratio[0]}:{closest_ratio[1]:.2f})"
    return aspect_text


def run_app():
    QImageReader.setAllocationLimit(1024)
    sys.argv += ["-platform", "windows:darkmode=2"]
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    run_app()
