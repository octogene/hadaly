# -*- coding: utf-8 -*-

from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Matrix
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image, AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.stencilview import StencilView
from kivy.uix.popup import Popup
from kivy.uix.button import ButtonBehavior
from kivy.factory import Factory
from kivy.properties import ObjectProperty, BooleanProperty, DictProperty, ListProperty, NumericProperty
from kivy.vector import Vector
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.colorpicker import ColorPicker



class ViewerScreen(Screen):
    app = ObjectProperty(None)
    dialog = ObjectProperty(None)

    def on_touch_down(self, touch, *args):
        bottom_right_corner = [(dp(self.size[0]) - dp(200), dp(200)), (dp(self.size[0]), 0)]
        top_left_corner = [(0, dp(self.size[1])), (dp(200), dp(self.size[1]) - dp(200))]
        top_right_corner = [(dp(self.size[0]) - dp(200), dp(self.size[1])), (dp(self.size[0]), dp(self.size[1]) - dp(200))]
        center = [(dp(200), dp(200)), (dp(self.size[0]) - dp(200), dp(self.size[1]) - dp(200))]
        if self.collide_point(*touch.pos):

            if Vector.in_bbox(touch.pos, bottom_right_corner[0], bottom_right_corner[1]) \
                    and touch.is_double_tap and len(self.app.presentation['slides']) > 0:

                self.dialog.to_switch = True
                self.dialog.title = _('Switch to...')
                self.dialog.open()
                return False

            elif Vector.in_bbox(touch.pos, top_left_corner[0], top_left_corner[1]) \
                    and touch.is_double_tap:

                self.app.root.current = 'editor'
                return True

            elif Vector.in_bbox(touch.pos, top_right_corner[0], top_right_corner[1]) \
                    and touch.is_double_tap and len(self.app.presentation['slides']) > 0:

                # TODO: Switch to toolbox mode.
                return False

            elif Vector.in_bbox(touch.pos, center[0], center[1]) \
                    and touch.is_double_tap and len(self.app.presentation['slides']) > 0:

                if len(self.box.children) < 2:
                    Logger.info('Application: Switching to compare mode.')
                    self.dialog.to_switch = False
                    self.dialog.title = _('Compare to...')
                    self.dialog.open()
                else:
                    self.app.compare_slide(action='rm')
                    touch.ungrab(self)

                return True

        return super(ViewerScreen, self).on_touch_down(touch)

    def on_pre_enter(self, *args):
        if not self.dialog:
            self.dialog = Factory.SlidesDialog()
        try:
            if not len(self.dialog.grid.children) == len(self.app.presentation['slides']):
                Logger.debug('Application: Clean \& reload carousel.')
                self.dialog.grid.clear_widgets()
                self.carousel.clear_widgets()

                for slide in reversed(self.app.presentation['slides']):
                    self.dialog.grid.add_widget(Factory.SlideButton(source=slide['thumb_src'],
                                                                    size_hint=(None, None),
                                                                    keep_ratio=True, ))
                    image = SlideBox(slide=slide)
                    self.carousel.add_widget(image)


        except KeyError as msg:
            Logger.debug('Application: Presentations seems empty. {msg}'.format(msg=msg))

    def update_carousel(self):
        self.dialog.grid.clear_widgets()
        self.carousel.clear_widgets()
        for slide in reversed(self.app.presentation['slides']):
            self.dialog.grid.add_widget(Factory.SlideButton(source=slide['thumb_src'],
                                                            size_hint=(None, None),
                                                            keep_ratio=True, ))
            image = SlideBox(slide=slide)
            self.carousel.add_widget(image)


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

        for child in self.float_layout.children:
            if child.id == 'img_zoom':
                child.size = (self.size[0] / 6, (self.size[0] / 6) / child.image_ratio)
                child.pos = [self.pos[0], 0.05 * dp(self.size[1])]

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
                scale = self.scale + 0.08
            elif touch.button == 'scrollup':
                scale = max(0.1, self.scale - 0.08)

            rescale = scale * 1.0 / self.scale
            matrix = Matrix().scale(rescale, rescale, rescale)
            self.apply_transform(matrix, anchor=touch.pos)

            self.check_slide_bbox()
            return False

        return super(SlideViewer, self).on_touch_down(touch)

    def on_transform_with_touch(self, touch):

        self.check_slide_bbox()

    def check_slide_bbox(self):
        if self.app.config.getint('viewer', 'thumb') == 1:
            img_point = (self.bbox[0][0] + self.bbox[1][0],
                         self.bbox[0][1] + self.bbox[1][1])
            parent_point = (self.parent.size[0] + self.parent.pos[0],
                            self.parent.size[1] + self.parent.pos[1])
            if not Vector.in_bbox(self.bbox[0],
                                  self.parent.pos,
                                  parent_point) or not Vector.in_bbox(img_point,
                                                                      self.parent.pos,
                                                                      parent_point):

                if all(child.id != 'img_zoom' for child in self.parent.children):
                    # TODO: Change thumbnail position and size based on config.
                    thumb = AsyncImage(source=self.image.source,
                                  id='img_zoom',
                                  size_hint=(None, None),
                                  keep_ratio=True,
                                  size=(self.parent.size[0] / 5,
                                        (self.parent.size[0] / 5) / self.image.image_ratio),
                                  pos=[0, 0.05 * self.parent.size[1]])
                    self.parent.add_widget(thumb)

            elif min(self.bbox[0]) > 0:
                for child in self.parent.children:
                    if child.id == 'img_zoom':
                        self.parent.remove_widget(child)

    def lock(self):
        if not self.locked:
            Logger.info('Application: Locking Slide.')
            self.locked = True
            self.do_rotation = False
            self.do_scale = False
            self.do_translation = False
            toolbar = PainterToolBar(painter=self.painter,
                                     paint_color=self.painter.tools[self.painter.current_tool]['color'],
                                     thickness=self.painter.thickness)
            self.painter.bind(thickness=toolbar.on_thickness)
            self.painter.bind(color=toolbar.on_paint_color)
            self.slidebox.toolbar.add_widget(toolbar)
            self.app.root.get_screen('viewer').carousel.scroll_timeout = 50
        elif self.locked:
            Logger.info('Application: Unlocking Slide.')
            self.locked = False
            self.do_scale = True
            self.do_translation = True
            self.do_rotation = True
            self.slidebox.toolbar.remove_widget(self.slidebox.toolbar.children[0])
            self.app.root.get_screen('viewer').carousel.scroll_timeout = 200

    def on_locked(self, *args):
        self.slidebox.toolbar.lock_btn.text = {u'\uf13e': u'\uf023', u'\uf023': u'\uf13e'}[
            self.slidebox.toolbar.lock_btn.text]
        if self.painter:
            self.painter.locked = {True: False, False: True}[self.locked]


class PainterToolBar(BoxLayout):
    painter = ObjectProperty(None)
    paint_color = ListProperty((1, 1, 1, 1))
    thickness = NumericProperty(0.5)

    def show_color_picker(self, current_color):
        popup = Popup(title='Color Picker',
                      size_hint=(0.5, 0.5))
        color_picker = ColorPicker(color=current_color)
        color_picker.bind(color=self.on_paint_color)
        popup.content = color_picker
        popup.open()

    def on_paint_color(self, instance, value):
        self.paint_color = value
        self.painter.color = value

    def on_thickness(self, instance, value):
        self.thickness = value
        self.painter.thickness = value


class SlidesDialog(Popup):
    to_switch = BooleanProperty(False)


class SlideButton(ButtonBehavior, Image):
    app = ObjectProperty(None)

    def on_release(self):
        if self.parent.dialog.to_switch:
            current_index = self.parent.children.index(self)
            carousel_index = list(reversed(xrange(len(self.parent.children))))
            self.app.switch_slide(carousel_index[current_index])
        else:
            self.app.compare_slide(self.parent.children.index(self))
