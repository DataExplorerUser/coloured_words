wrap.py
```
from typing import Iterable, List, Tuple


class RectWrappingCollection:
    def _get_lines(self) -> [List[Tuple[int, float, float, float]], float, float]:
        cum_width = 0
        cum_space = 0
        cum_total_width = 0
        last_min_space = 0
        max_height = 0
        line = []

        for i, (width, height, min_space) in enumerate(zip(self._widths, self._heights, self._min_spaces)):

            if (cum_total_width + width > self._wrap) or i == self.count:
                yield line, max_height, cum_total_width, cum_width
                cum_width = 0
                cum_space = 0
                last_min_space = 0
                max_height = 0
                line = []
            space = max(min_space, last_min_space)
            cum_space += space
            cum_width += width
            cum_total_width = cum_width + cum_space
            max_height = max(height, max_height)
            last_min_space = min_space
            line.append((i, width, height, space))
        yield line, max_height, cum_total_width, cum_width

    def _process_lines(self):
        y0 = 0
        for i, (line, max_height, cum_total_width, cum_width) in enumerate(self._get_lines()):
            if self._line_fixed_height:
                y0 += self._line_fixed_height * self._line_height
            else:
                y0 += max_height * self._line_height

            x0 = 0
            ov_space = None
            if self._text_align == 1:
                x0 = (self._wrap - cum_total_width) / 2.0
            if self._text_align == 2:
                x0 = self._wrap - cum_total_width
            if self._text_align == 3:
                ov_space = (self._wrap - cum_width) / len(line)

            for j, (k, width, height, space) in enumerate(line):
                y1 = y0-height
                yield (x0, y1)
                x0 += width + (ov_space or space)

    def set_wrap(self, value):
        self._wrap = value

    def set_line_fixed_height(self, value):
        self._line_fixed_height = value

    def set_line_height(self, value):
        self._line_height = value

    def set_align(self, value):
        self._text_align = value

    def get_sizes(self):
        yield from self._process_lines()

    @property
    def count(self) -> int:
        return len(self._widths)

    def __init__(self,
                 wrap: float = -1,
                 widths: Iterable[float] = None,
                 heights: Iterable[float] = None,
                 min_spaces: Iterable[float] = None,
                 line_fixed_height: float = 0,
                 line_height: float = 1.2,
                 text_align: int = 0,
                 default_min_space: float = 10.0,
                 ):
        self._wrap: float = wrap
        self._widths: List[float] = list(widths) if widths else []
        self._heights: List[float] = list(heights) if heights else []
        self._min_spaces: List[float] = list(min_spaces) if min_spaces else []

        self._line_fixed_height = line_fixed_height
        self._line_height = line_height
        self._text_align = text_align

        self._min_spaces: List[float] = []
        if min_spaces:
            self._min_spaces = list(min_spaces)
        else:
            if self.count:
                self._min_spaces = [[default_min_space] * self.count]

        self.default_min_space: float = default_min_space

    def add_rect(self, width: float, height: float, min_space: float = None):
        self._widths.append(width)
        self._heights.append(height)
        self._min_spaces.append(min_space if min_space else self.default_min_space)
```

demo.py
```
from wrap import RectWrappingCollection
import dearpygui.dearpygui as dpg

import random

dpg.create_context()

text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
txt_values = text.split(' ')
txt_values = [i for i in txt_values[:-1]] + [txt_values[-1]]

ta = [RectWrappingCollection(text_align=0)]

with dpg.font_registry():
    f_font0 = dpg.add_font("Whitney-Light.ttf", 27, tag="f_27")
    f_font1 = dpg.add_font("FiraCode-Medium.otf", 15, tag="f_15")
dpg.create_viewport()


# width, height, channels, data = dpg.load_image("path/to/Somefile.png")
def add_and_load_image(image_path, parent=None):
    width, height, channels, data = dpg.load_image(image_path)

    with dpg.texture_registry() as reg_id:
        texture_id = dpg.add_static_texture(width, height, data, parent=reg_id)

    if parent is None:
        return dpg.add_image(texture_id)
    else:
        return dpg.add_image(texture_id, parent=parent)


with dpg.window(width=640, height=800):
    with dpg.group() as g:
        def update_pos(widget):
            pos = list(ta[0].get_sizes())

            offset_x, offset_y = dpg.get_item_pos(widget)
            for i, rect in enumerate(dpg.get_item_children(widget, 1)):
                x, y = pos[i]
                dpg.set_item_pos(rect, (offset_x + x, offset_y + y))


        def set_wrap(value, widget):
            dpg.set_value('w0', value)
            ta[0].set_wrap(value)
            update_pos(widget)


        def set_line_fixed_height(value, widget):
            dpg.set_value('w_line_fixed_height_text', value if value != 0 else '(auto/adaptive)')
            ta[0].set_line_fixed_height(value)
            update_pos(widget)


        def set_line_height(value, widget):
            print(value)
            ta[0].set_line_height(value)
            update_pos(widget)


        def set_align(value, widget):
            values = {'left': 0, 'center': 1, 'right': 2, 'justified': 3}
            ta[0].set_align(values[value])
            update_pos(widget)


        w_wrap_control = dpg.add_drag_float(
            label="wrap width",
            default_value=400,
            max_value=600,
            callback=lambda s, a, u: set_wrap(a, 'rich_container')
        )
        w_line_fixed_height_control = dpg.add_drag_float(
            label="line fixed height (px)",
            default_value=0,
            max_value=50,
            speed=0.5,
            callback=lambda s, a, u: set_line_fixed_height(a, 'rich_container')
        )
        w_line_fixed_height_text = dpg.add_text(dpg.get_value(w_line_fixed_height_control),
                                                tag='w_line_fixed_height_text')
        w_line_height_control = dpg.add_drag_float(
            label="line height",
            default_value=1.2,
            max_value=4,
            speed=0.01,
            callback=lambda s, a, u: set_line_height(a, 'rich_container')
        )

        w_align_control = dpg.add_radio_button(
            ("left", "center", "right", "justified"),
            label="align",
            default_value="left",
            callback=lambda s, a, u: set_align(a, 'rich_container'),
            horizontal=True,
        )

        with dpg.group(tag='rich_container') as rich_container:
            last_font = None

            # Everything below is random play adding widgets, looping from the word list
            for i, word in enumerate(txt_values):
                random.seed(i)
                font = f_font0 if random.randint(0, 10) % 10 else f_font1

                color = None
                if font != last_font:
                    last_font = font
                    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 255)
                text_widget = dpg.add_text(
                    word,
                    pos=(0, 0),
                    parent=rich_container,
                    tag=f'ft_{i}',
                    color=color,

                )
                if font:
                    dpg.bind_item_font(text_widget, font)

                if i == 8:
                    # Adding a emoji
                    img = add_and_load_image('line32.png', parent=rich_container)


                # Just a callback for the button
                def update_both():
                    set_align('justified', 'rich_container')
                    dpg.set_value(w_align_control, 'justified')


                # Adding a button
                if i == 15:
                    dpg.add_button(
                        label="Click me",
                        callback=update_both,
                    )
            # /
            
            # add_rects loops the cointainer children, reading their sizes and 'mapping' their stack index when its added
            def add_rects():
                for i, widget in enumerate(dpg.get_item_children(rich_container, 1)):
                    if dpg.get_item_type(widget) == 'mvAppItemType::mvText':
                        font = dpg.get_item_font(widget)
                        ta[0].add_rect(
                            *dpg.get_text_size(
                                dpg.get_value(widget),
                                font=font
                            )
                        )
                    else:
                        ta[0].add_rect(*dpg.get_item_rect_size(widget))
                set_wrap(dpg.get_value(w_wrap_control), 'rich_container')
                set_line_fixed_height(dpg.get_value(w_line_fixed_height_control), 'rich_container')
                set_line_height(dpg.get_value(w_line_height_control), 'rich_container')
                set_align(dpg.get_value(w_align_control), 'rich_container')


            dpg.set_frame_callback(3, add_rects)

        w0 = dpg.add_text(dpg.get_value(w_wrap_control), tag='w0')

dpg.setup_dearpygui()
dpg.show_viewport()

dpg.show_debug()
dpg.show_item_registry()

dpg.start_dearpygui()
dpg.destroy_context()
```
