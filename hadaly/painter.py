# -*- coding: utf-8 -*-

import math
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.vector import Vector
from kivy.properties import StringProperty, DictProperty, BooleanProperty, BoundedNumericProperty, ListProperty


class Painter(Widget):
    tools = DictProperty({'arrow': {'color': (1, 1, 1, 1), 'thickness': 0.5},
                          'line': {'color': (1, 1, 1, 1), 'thickness': 0.5},
                          'freeline': {'color': (1, 1, 1, 1), 'thickness': 0.5},
                          'eraser': {'thickness': 0.4}
                          })
    current_tool = StringProperty('arrow')
    thickness = BoundedNumericProperty(1, min=0.5, max=10, errorvalue=0.5)
    color = ListProperty((1, 1, 1, 1))
    locked = BooleanProperty(False)

    def on_thickness(self, instance, value):
        self.thickness = value

    def on_color(self, instance, value):
        self.color = value

    def on_touch_down(self, touch):
        if not self.locked and self.collide_point(*touch.pos):
            touch.grab(self)
            with self.canvas:
                Color(*self.color, mode='rgba')
                touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.thickness, cap='round', joint='miter')
                if self.current_tool == 'arrow':
                    touch.ud['arrowhead'] = Line(width=self.thickness, cap='square', joint='miter')
                touch.ud['initial_pos'] = touch.pos
        else:
            return False

        return super(Painter, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if not self.locked and self.collide_point(*touch.pos):
            try:
                if self.current_tool == 'freeline':
                    touch.ud['line'].points += [touch.x, touch.y]
                else:
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
        h = 10 * math.sqrt(3)
        w = 10
        U = (B - A) / Vector(B - A).length()
        V = Vector(-U.y, U.x)
        v1 = B - h * U + w * V
        v2 = B - h * U - w * V
        return (v1, v2)

    def on_touch_up(self, touch):
        if not self.locked and touch.grab_current == self and \
                self.collide_point(*touch.pos) and self.current_tool == 'arrow':
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
