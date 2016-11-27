# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals, absolute_import

import os
from functools import partial

from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.properties import (StringProperty, ObjectProperty,
                             NumericProperty, BooleanProperty, DictProperty)
from .magnet import Magnet
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.config import Config
from PIL import Image
from kivy.graphics.opengl import GL_MAX_TEXTURE_SIZE, glGetIntegerv
from kivy.factory import Factory
from kivy.metrics import dp


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
        im = Image.open(os.path.join(self.app.tempdir, self.img_src))
        self.texture_size = im.size
        return im.size

    def on_img_src(self, *args):
        Logger.debug('Editor: img_src updated for {title}'.format(title=self.title))
        max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0]
        try:
            im = Image.open(self.img_src)
            if max(im.size) > max_texture_size:
                Logger.debug('Editor : image too big for max texture size ! Resizing...')
                size = self.app.resize(im.size, (max_texture_size, max_texture_size))
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(self.img_src)
        except IOError:
            Logger.debug('Editor: {img_src} is not a valid filename.'.format(img_src=self.img_src))

    def rm_info_panel(self, *args):
        self.app.root.current_screen.remove_widget(args[0])
        self.info_panel = False

    def show_info_panel(self, pos):
        if not self.info_panel:
            self.info_panel = True

            info_panel = Factory.SlideInfo(id='info_panel')
            Clock.schedule_once(partial(self.rm_info_panel, info_panel), 3)
            # info_panel.font = ''.join((str(int(self.parent.height / 10)), 'sp'))
            info_panel.artist.text = self.artist
            info_panel.title.text = self.title
            info_panel.year.text = self.year
            info_panel.pos = self.to_window(*(pos[0], pos[1] - dp(20)))
            self.app.root.current_screen.add_widget(info_panel)


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
    transitions = DictProperty({'x': 'out_expo',
                                'y': 'in_sine',
                                'size': 'out_elastic'})
    duration = NumericProperty(0.5)

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
                'Editor: Touch up passed through and unscheduled clock event could not be unscheduled. A bug...')

    def on_touch_down(self, touch, *args):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.delete_clock(touch)
                popup = SlideInfoDialog(slide=self.img)
                popup.open()
            else:
                self.create_clock(touch)

        return super(DraggableSlide, self).on_touch_down(touch)

    def single_tap(self, touch, *args):
        grid_layout = self.app.root.current_screen.slides_view.grid_layout
        # Get position of current slide and number of slides
        for index, value in enumerate(grid_layout.children):
            if self == value:
                self.old_index = index
                self.no_slides = len(grid_layout.children)

        touch.grab(self)
        self.remove_widget(self.img)
        self.app.root.current_screen.add_widget(self.img)
        self.center = self.to_window(*touch.pos)
        self.img.center = touch.pos

        return super(DraggableSlide, self).on_touch_down(touch)

    def on_touch_move(self, touch, *args):
        grid_layout = self.app.root.current_screen.slides_view.grid_layout

        if touch.grab_current == self:
            self.img.center = self.to_window(*touch.pos)
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

                self.center = self.to_window(*touch.pos)

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
                self.app.root.current_screen.slides_view.modified = ['rm', (self.old_index, self.new_index), self.img.title]
            # Move entry in app.presentation accordingly to DraggableSlide move.
            elif any(touch.dpos) > 0 and self.old_index != self.new_index and self.new_index is not None:
                self.app.root.current_screen.slides_view.modified = ['mv', (self.old_index, self.new_index), self.img.title]

            self.app.presentation.slides = [child.img.get_slide_info() for child in grid_layout.children]

            self.app.root.current_screen.remove_widget(self.img)
            self.img.center = self.to_local(*touch.pos)
            self.add_widget(self.img)
            touch.ungrab(self)
            return True

        return super(DraggableSlide, self).on_touch_up(touch)