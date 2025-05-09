# Copyright (C) 2024 Tatudesigner <heriton.agoncalves@gmail.com>
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import inkex
from inkex import Layer, Rectangle

# Unit conversions
CONVERSIONS = {
    'in': 96.0,
    'pt': 1.3333333333333333,
    'px': 1.0,
    'mm': 3.779527559055118,
    'cm': 37.79527559055118,
    'm': 3779.527559055118,
    'km': 3779527.559055118,
    'Q': 0.94488188976378,
    'pc': 16.0,
    'yd': 3456.0,
    'ft': 1152.0,
    '': 1.0,  # Default px
}

class DesignGrid(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--grid_type", type=str, default="columns", help="Grid Type: Columns or Rows")
        pars.add_argument("--columns", type=int, default=12, help="Number of columns/rows")
        pars.add_argument("--column_width", type=float, default=50, help="Width of each column/row (px)")
        pars.add_argument("--gutter", type=float, default=16, help="Gutter width (px)")
        pars.add_argument("--padding_width", type=float, default=10, help="Width of padding columns (px)")
        pars.add_argument("--fill_color", type=inkex.Color, default=inkex.Color("#ff00661a"), help="Fill color of the grid")

        # Add the margin argument
        pars.add_argument("--margin", type=float, default=0, help="Margin from page edges (px)")

        # Corrected: Use inkex.Boolean for boolean type
        pars.add_argument("--stretch_grid", type=inkex.Boolean, default=False, help="Stretch grid to page edges")

    def effect(self):
        page_width, page_height = self.get_page_dimensions()
        grid_type = self.options.grid_type
        count, size, gutter, padding_width, fill_color = self.get_user_parameters()
        margin = self.options.margin  # Get the user-defined margin

        if not self.validate_parameters(count, size, gutter, padding_width):
            inkex.errormsg("Invalid parameters. Please check your inputs.")
            return

        # No longer calculate margin here, use user-defined value
        # margin = self.calculate_margin(page_width if grid_type == "columns" else page_height, count, size, gutter)
        grid_number = self.get_next_grid_number()

        if grid_type == "columns":
            # Pass user-defined margin
            self.create_columns_grid(count, size, gutter, padding_width, fill_color, margin, page_height, page_width, grid_number)
        elif grid_type == "rows":
            # Pass user-defined margin
            self.create_rows_grid(count, size, gutter, padding_width, fill_color, margin, page_width, page_height, grid_number)

    def get_page_dimensions(self):
        """Retrieve the page dimensions in pixels."""
        pixel_conversion_factor = CONVERSIONS[self.svg.unit]
        return (
            self.svg.viewbox_width * pixel_conversion_factor,
            self.svg.viewbox_height * pixel_conversion_factor
        )

    def get_user_parameters(self):
        """Retrieve user-defined parameters."""
        return (
            self.options.columns,
            self.options.column_width,
            self.options.gutter,
            self.options.padding_width,
            self.options.fill_color
        )

    def validate_parameters(self, count, size, gutter, padding_width):
        """Validate input parameters."""
        return count > 0 and size > 0 and gutter >= 0 and padding_width >= 0

    def calculate_margin(self, page_size, count, size, gutter):
        """Calculate the margin for centering the grid."""
        total_size = (count * size) + (gutter * (count - 1))
        return (page_size - total_size) / 2

    def get_next_grid_number(self):
        """Determine the next grid number based on existing grids."""
        existing_grids = self.svg.xpath('//svg:g[starts-with(@inkscape:label, "Grid ")]', namespaces=inkex.NSS)
        numbers = [
            int(grid.get('inkscape:label').split(' ')[1])
            for grid in existing_grids
            if grid.get('inkscape:label').split(' ')[1].isdigit()
        ]
        return max(numbers, default=0) + 1

    def create_columns_grid(self, count, width, gutter, padding_width, fill_color, margin, page_height, page_width, grid_number):
        """Create a responsive columns grid."""
        grid_group = Layer()
        grid_group.set('inkscape:label', f'Grid {grid_number}')
        grid_group.set('sodipodi:insensitive', 'true')

        # Calculate margin for centering if stretch_grid is disabled
        if not self.options.stretch_grid:
            total_width = (count * width) + (gutter * (count - 1))
            margin = (page_width - total_width) / 2

        x = margin  # Initialize x with the (potentially calculated) margin
        available_width = page_width - (margin * 2)  # Subtract margins from both sides

        # Adjust column width if stretch_grid is enabled
        if self.options.stretch_grid:
            available_width -= (gutter * (count - 1))  # Subtract total gutter width
            width = available_width / count  # Calculate new column width
            # x remains the user-defined margin

        for i in range(count):
            # Create the main column
            column = self.create_rectangle(x, 0, width, page_height, fill_color)
            grid_group.append(column)

            # Create padding rectangles
            if padding_width > 0:
                left_padding = self.create_rectangle(x, 0, padding_width, page_height, fill_color)
                right_padding = self.create_rectangle(x + width - padding_width, 0, padding_width, page_height, fill_color)
                grid_group.append(left_padding)
                grid_group.append(right_padding)

            x += width + gutter

        self.svg.append(grid_group)

    def create_rows_grid(self, count, height, gutter, padding_width, fill_color, margin, page_width, page_height, grid_number):
        """Create a responsive rows grid."""
        grid_group = Layer()
        grid_group.set('inkscape:label', f'Grid {grid_number}')
        grid_group.set('sodipodi:insensitive', 'true')

        # Calculate margin for centering if stretch_grid is disabled
        if not self.options.stretch_grid:
            total_height = (count * height) + (gutter * (count - 1))
            margin = (page_height - total_height) / 2

        y = margin  # Initialize y with the (potentially calculated) margin
        available_height = page_height - (margin * 2)  # Subtract margins from both sides

        # Adjust row height if stretch_grid is enabled
        if self.options.stretch_grid:
            available_height -= (gutter * (count - 1))  # Subtract total gutter height
            height = available_height / count  # Calculate new row height
            # y remains the user-defined margin

        for _ in range(count):
            # Create the main row
            row = self.create_rectangle(0, y, page_width, height, fill_color)
            grid_group.append(row)

            # Create padding rectangles
            if padding_width > 0:
                top_padding = self.create_rectangle(0, y, page_width, padding_width, fill_color)
                bottom_padding = self.create_rectangle(0, y + height - padding_width, page_width, padding_width, fill_color)
                grid_group.append(top_padding)
                grid_group.append(bottom_padding)

            y += height + gutter

        self.svg.append(grid_group)

    def create_rectangle(self, x, y, width, height, fill_color):
        """Create a single rectangle."""
        rect = Rectangle()
        rect.set("x", str(x / CONVERSIONS[self.svg.unit]))
        rect.set("y", str(y / CONVERSIONS[self.svg.unit]))
        rect.set("width", str(width / CONVERSIONS[self.svg.unit]))
        rect.set("height", str(height / CONVERSIONS[self.svg.unit]))
        rect.set("style", f"fill:{fill_color.to_rgb()};fill-opacity:{fill_color.alpha};stroke:none")
        return rect

if __name__ == '__main__':
    DesignGrid().run()
