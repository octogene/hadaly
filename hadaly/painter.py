# -*- coding: utf-8 -*-
from __future__ import division, unicode_literals

import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.vector import Vector
from kivy.properties import StringProperty, DictProperty, BooleanProperty


class Painter(Widget):
    tools = DictProperty({'arrow': {'color': (1, 0, 1, 1), 'thickness': 0.4},
                          'line': {'color': (1, 1, 1, 1), 'thickness': 0.4},
                          'eraser': {'thickness': 0.4}
                          })
    current_tool = StringProperty('arrow')
    locked = BooleanProperty(False)

    def on_touch_down(self, touch):
        if not self.locked and self.collide_point(*touch.pos):
            touch.grab(self)
            color = self.tools[self.current_tool]['color']
            thickness = self.tools[self.current_tool]['thickness']
            with self.canvas:
                Color(*color, mode='rgba')
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=thickness, cap='round', joint='miter')
                touch.ud['arrowhead'] = Line(width=thickness, cap='square', joint='miter')
                touch.ud['initial_pos'] = touch.pos
        else:
            return False

        return super(Painter, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.locked and self.collide_point(*touch.pos):
            try:
                touch.ud['line'].points = [touch.ox, touch.oy, touch.x, touch.y]
            except KeyError:
                pass
        else:
            return False

        return super(Painter, self).on_touch_move(touch)

    def arrowhead(self, start, end):
        '''
        start : list of points (x, y) for the start of the arrow.
        end : list of points (x, y) for the end of the arrow.

        return : list of points for each line forming the arrow head.
        '''
        # TODO: Adjust arrowhead size according to line thickness.
        A = Vector(start)
        B = Vector(end)
        h = 5 * math.sqrt(3)
        w = 5
        U = (B - A) / Vector(B - A).length()
        V = Vector(-U.y, U.x)
        v1 = B - h * U + w * V
        v2 = B - h * U - w * V
        return (v1, v2)

    def on_touch_up(self, touch):
        if not self.locked and touch.grab_current == self and self.collide_point(*touch.pos):
            try:
                arrowhead = self.arrowhead(touch.ud['initial_pos'], touch.pos)
            except KeyError:
                pass
            except ZeroDivisionError:
                pass
            else:
                touch.ud['arrowhead'].points += arrowhead[0]
                touch.ud['arrowhead'].points += (touch.x, touch.y)
                touch.ud['arrowhead'].points += arrowhead[1]
                touch.ungrab(self)
        else:
            return False

        return super(Painter, self).on_touch_up(touch)

    def on_size(self, *kwargs):
        # TODO: Update every drawing according to size.
        self.canvas.clear()
