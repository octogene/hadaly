# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, absolute_import

from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Matrix
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.popup import Popup
from kivy.uix.button import ButtonBehavior
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, DictProperty, ListProperty, NumericProperty
from kivy.logger import Logger
from kivy.utils import platform
from kivy.uix.colorpicker import ColorPicker
import threading

class ViewerScreen(Screen):
    app = ObjectProperty(None)
    dialog = ObjectProperty(None)
    slides = ListProperty(None)
    stop = threading.Event()

    def on_pre_enter(self, *args):
        if not self.dialog:
            self.dialog = Factory.SlidesDialog()
            self.start_loading_slides(self.app.presentation.slides)
            if not platform == 'android':
                Logger.info('Viewer : Adapting carousel to platform ({platform})'.format(platform=platform))
                self.carousel.scroll_timeout = 2

    def start_loading_slides(self, value):
        threading.Thread(target=self.loading_slides, args=(value,)).start()

    def loading_slides(self, value):
        [self.carousel.add_widget(SlideBox(slide=slide)) for slide in reversed(value)]
        [self.dialog.grid.add_widget(Factory.SlideButton(source=slide['thumb_src'], keep_ratio=True, )) for slide in reversed(value)]
        self.app.root.get_screen('editor').slides_view.bind(modified=self.update_slides)

    def update_slides(self, instance, value):
        c_index = list(reversed(range(len(self.carousel.slides))))
        if value[0] == 'mv':
            self.carousel.slides.insert(c_index[value[1][1]],
                                        self.carousel.slides.pop(c_index[value[1][0]]))
        elif value[0] == 'rm':
            self.carousel.slides.pop(c_index[value.modified[1][0]])
        elif value[0] == 'add':
            pass

class TouchActionArea(FloatLayout):

    def on_touch_down(self, touch):

        if self.collide_point(*touch.pos) and touch.is_double_tap and len(self.app.presentation.slides) > 0:
            try:
                child = [child for child in self.children if child.collide_point(*touch.pos)][0]
            except IndexError:
                Logger.debug('Viewer: No TouchActionArea child touched.')
                return
            if child.name == 'center':
                if len(self.app.root.current_screen.box.children) < 2:
                        Logger.info('Viewer: Switching to compare mode.')
                        self.parent.dialog.to_switch = False
                        self.parent.dialog.title = _('Compare to...')
                        self.parent.dialog.open()
                else:
                    self.app.compare_slide(action='rm')
                    touch.ungrab(self)
                return True

            elif child.name == 'ltop':
                self.app.root.current = 'editor'
                return True
            elif child.name == 'rtop':
                pass
            elif child.name == 'lbottom':
                pass
            elif child.name == 'rbottom':
                self.parent.dialog.to_switch = True
                self.parent.dialog.title = _('Switch to...')
                self.parent.dialog.open()
                return False

        return super(TouchActionArea, self).on_touch_down(touch)

class ImgFullZoom(Image):
    pass

class SlideBox(BoxLayout, StencilView):
    slide = DictProperty(None)

    def on_touch_down(self, touch):

        if not self.collide_point(*touch.pos):
            return False

        return super(SlideBox, self).on_touch_down(touch)

    def on_touch_up(self, touch):

        if not touch.grab_current == self:
            return False

        return super(SlideBox, self).on_touch_down(touch)

    def on_size(self, *args):

        self.gui_layout.slide_info.font = ''.join((str(int(self.height / 45)), 'sp'))

    def get_caption(self):

        artist = self.slide['artist'].decode('utf-8')
        title = ''.join(('[i]', self.slide['title'].decode('utf-8'), '[/i]'))
        year = self.slide['year']

        caption = ' - '.join((artist, title, year))

        return caption

class SlideViewer(ScatterLayout):
    image = ObjectProperty(None)
    app = ObjectProperty(None)
    locked = BooleanProperty(False)
    painter = ObjectProperty(None)

    def on_touch_down(self, touch):
        # Scaling scatter with mousewheel based on touch position.
        if self.collide_point(*touch.pos) and touch.is_mouse_scrolling:

            scale = self.scale

            if touch.button == 'scrolldown':
                scale = self.scale * 1.1
            elif touch.button == 'scrollup':
                scale = max(0.1, self.scale * 0.9)

            rescale = scale * 1.0 / self.scale
            matrix = Matrix().scale(rescale, rescale, rescale)
            self.apply_transform(matrix, anchor=touch.pos)

            return False

        return super(SlideViewer, self).on_touch_down(touch)

    def on_scale(self, instance, value):
        if value > 1:
            if all(child.id != 'img_zoom' for child in self.parent.children):
                # TODO: Change thumbnail position and size based on config.
                thumb = ImgFullZoom(source=self.parent.parent.slide['thumb_src'],
                              id='img_zoom')

                if self.app.config.get('viewer', 'thumb_pos') == 'bottom left':
                    thumb.pos = [0, self.parent.height / 15]
                elif self.app.config.get('viewer', 'thumb_pos') == 'top left':
                    thumb.pos = [0, self.parent.height - thumb.texture_size[1]]
                elif self.app.config.get('viewer', 'thumb_pos') == 'top right':
                    thumb.pos = [self.parent.width - thumb.texture_size[0], self.parent.height - thumb.texture_size[1]]
                elif self.app.config.get('viewer', 'thumb_pos') == 'bottom right':
                    pass

                self.parent.add_widget(thumb)
        elif not all(child.id != 'img_zoom' for child in self.parent.children):
            try:
                img_zoom = [child for child in self.parent.children if child.id == 'img_zoom'][0]
                self.parent.remove_widget(img_zoom)
            except IndexError:
                Logger.debug('Viewer: No img_zoom to remove.')

    def lock(self):
        if not self.locked:
            Logger.info('Viewer: Locking Slide.')
            self.locked = True
            self.do_rotation = False
            self.do_scale = False
            self.do_translation = False
            self.slidebox.toolbar.add_widget(PainterToolBar(painter=self.painter,
                                                            paint_color=self.painter.tools[self.painter.current_tool][
                                                                'color']))
            self.app.root.get_screen('viewer').carousel.scroll_timeout = 20
            self.app.root.get_screen('viewer').carousel.scroll_distance = '50dp'
        elif self.locked:
            Logger.info('Viewer: Unlocking Slide.')
            self.locked = False
            self.do_scale = True
            self.do_translation = True
            self.do_rotation = True
            self.slidebox.toolbar.remove_widget(self.slidebox.toolbar.children[0])
            self.app.root.get_screen('viewer').carousel.scroll_timeout = 2
            self.app.root.get_screen('viewer').carousel.scroll_distance = '20dp'

    def on_locked(self, *args):
        self.slidebox.toolbar.lock_btn.text = {u'\uf13e': u'\uf023', u'\uf023': u'\uf13e'}[
            self.slidebox.toolbar.lock_btn.text]
        if self.painter:
            self.painter.locked = {True: False, False: True}[self.locked]

class PainterToolBar(BoxLayout):
    painter = ObjectProperty(None)
    paint_color = ListProperty((1, 1, 1, 1))
    thickness = NumericProperty(None)

    def show_color_picker(self):
        popup = Popup(title='Color Picker',
                      size_hint=(0.5, 0.5))
        color_picker = ColorPicker()
        color_picker.bind(color=self.on_color)
        popup.content = color_picker
        popup.open()

    def on_color(self, instance, value):
        self.paint_color = self.painter.tools[self.painter.current_tool]['color'] = value

    def on_thickness(self, instance, value):
        self.painter.tools[self.painter.current_tool]['thickness'] = value


class SlidesDialog(Popup):
    to_switch = BooleanProperty(False)


class SlideButton(ButtonBehavior, Image):
    app = ObjectProperty(None)

    def on_release(self):
        if self.parent.dialog.to_switch:
            current_index = self.parent.children.index(self)
            carousel_index = list(reversed(range(len(self.parent.children))))
            self.app.switch_slide(carousel_index[current_index])
        else:
            self.app.compare_slide(self.parent.children.index(self))
