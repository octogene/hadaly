# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import os
from functools import partial

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.garden.magnet import Magnet
from kivy.garden.filechooserthumbview import FileChooserThumbView
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.config import Config
from PIL import Image as ImagePIL
from kivy.graphics.opengl import GL_MAX_TEXTURE_SIZE, glGetIntegerv
from kivy.factory import Factory


class FileThumbView(BoxLayout):
    app = ObjectProperty(None)

    def show_thumbnail(self):
        self.thumb_grid.clear_widgets()
        s = [item for item in self.file_chooser.files if item.endswith(('.png', '.jpg', '.jpeg'))]
        for item in s:
            thumb_src = self.app.create_thumbnail(item)
            thumb = ThumbnailButton(source=thumb_src.encode('utf-8'),
                                    keep_ratio=True,
                                    size_hint=(None, None),
                                    original_src=item.encode('utf-8'))
            self.thumb_grid.add_widget(thumb)


class ThumbView(FileChooserThumbView):
    pass


class ThumbnailButton(ButtonBehavior, Image):
    original_src = StringProperty(None)


class Slide(BoxLayout):
    app = ObjectProperty(None)
    img_src = StringProperty(None)
    thumb_src = StringProperty(None)
    artist = StringProperty('')
    title = StringProperty('')
    year = StringProperty('')
    real_size = ObjectProperty(None)
    texture_size = ObjectProperty(None)
    info_panel = BooleanProperty(False)

    def get_slide_info(self):
        return {'img_src': self.img_src,
                'thumb_src': self.thumb_src,
                'artist': self.artist,
                'title': self.title,
                'year': self.year,
                'texture_size': self.texture_size
                }

    def update_texture_size(self):
        im = ImagePIL.open(os.path.join(self.app.tempdir, self.img_src))
        self.texture_size = im.size
        return im.size

    def on_img_src(self, *args):
        Logger.debug('Editor: img_src updated for {title}'.format(title=self.title))
        max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0]
        try:
            im = ImagePIL.open(self.img_src)
            if max(im.size) > max_texture_size:
                Logger.debug('Application : image too big for max texture size ! Resizing...')
                size = self.app.resize(im.size, (max_texture_size, max_texture_size))
                im.thumbnail(size, ImagePIL.ANTIALIAS)
                im.save(self.img_src)
        except IOError:
            Logger.debug('Editor: {img_src} is not a valid filename.'.format(img_src=self.img_src))

    def show_info_panel(self):
        if self.info_panel:
            self.info_panel = False
            self.remove_widget(self.children[0])
        elif not self.info_panel:
            self.info_panel = True
            info_panel = Factory.SlideInfo(id='info_panel')
            info_panel.artist.text = self.artist
            info_panel.title.text = self.title
            info_panel.year.text = self.year
            self.add_widget(info_panel)


class SlideInfoDialog(Popup):
    slide = ObjectProperty(None)
    app = ObjectProperty(None)

    def on_validate(self):
        if self.slide.parent:
            # Update with the index of DraggableSlide in grid_layout.
            self.app.update_presentation('update', self.slide.parent.parent.children.index(self.slide.parent), None)
        else:
            self.slide.update_texture_size()
            self.app.add_slide(self.slide)
        self.dismiss()


# Class based on @tshirtman drag'n drop example.
class DraggableSlide(Magnet):
    img = ObjectProperty(None, allownone=True)
    app = ObjectProperty(None)
    old_index = NumericProperty(None)
    new_index = NumericProperty(None)
    no_slides = NumericProperty(None)

    def on_img(self, *args):
        self.clear_widgets()

        if self.img:
            Clock.schedule_once(lambda *x: self.add_widget(self.img), 0)

    def create_clock(self, touch, *args):
        callback = partial(self.single_tap, touch)
        Clock.schedule_once(callback, Config.getint('postproc', 'double_tap_time') / 1000)
        touch.ud['event'] = callback

    def delete_clock(self, touch, *args):
        # TODO: Fix touch_up passing through when popup dismissed.
        try:
            Clock.unschedule(touch.ud['event'])
        except KeyError:
            Logger.exception(
                'Application: Touch up passed through and unscheduled clock event could not be unscheduled. A bug...')

    def on_touch_down(self, touch, *args):
        if self.collide_point(*touch.pos):
            if touch.is_touch:
                self.create_clock(touch)
            if touch.is_double_tap:
                self.delete_clock(touch)
                popup = SlideInfoDialog(slide=self.img)
                popup.open()

        return super(DraggableSlide, self).on_touch_down(touch)

    def single_tap(self, touch, *args):
        if self.collide_point(*touch.pos):
            grid_layout = self.app.root.current_screen.slides_view.grid_layout
            # Get position of current slide and number of slides
            for index, value in enumerate(grid_layout.children):
                if self == value:
                    self.old_index = index
                    self.no_slides = len(grid_layout.children)

            touch.grab(self)
            self.remove_widget(self.img)
            self.app.root.current_screen.add_widget(self.img)
            self.center = touch.pos
            self.img.center = touch.pos
            return True

        return super(DraggableSlide, self).on_touch_down(touch)

    def on_touch_move(self, touch, *args):
        grid_layout = self.app.root.current_screen.slides_view.grid_layout

        if touch.grab_current == self:

            self.img.center = touch.pos
            if grid_layout.collide_point(*touch.pos):
                grid_layout.remove_widget(self)

                for i, c in enumerate(grid_layout.children):
                    if c.collide_point(*touch.pos):
                        grid_layout.add_widget(self, i)
                        self.new_index = i
                        break
                else:
                    grid_layout.add_widget(self)
            # Remove slide if dropped out of grid_layout.
            else:
                if self.parent == grid_layout:
                    grid_layout.remove_widget(self)

                self.center = touch.pos

    def on_touch_up(self, touch, *args):
        grid_layout = self.app.root.current_screen.slides_view.grid_layout

        if self.collide_point(*touch.pos):
            self.delete_clock(touch)

        if touch.grab_current == self:
            if any(touch.dpos) == 0:
                if grid_layout.collide_point(*touch.pos):
                    grid_layout.remove_widget(self)
                    grid_layout.add_widget(self, self.old_index)
                else:
                    grid_layout.add_widget(self)
            # Delete entry in app.presentation if DraggableSlide removed.
            elif len(grid_layout.children) < self.no_slides:
                self.app.update_presentation('rm', self.old_index, self.new_index)

            # Move entry in app.presentation accordingly to DraggableSlide move.
            elif any(touch.dpos) > 0 and self.old_index != self.new_index and self.new_index is not None:
                self.app.update_presentation('mv', self.old_index, self.new_index)

            self.app.root.current_screen.remove_widget(self.img)
            self.add_widget(self.img)
            touch.ungrab(self)
            return True

        return super(DraggableSlide, self).on_touch_up(touch, *args)
