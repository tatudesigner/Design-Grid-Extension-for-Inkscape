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

class ResponsiveGrid(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--grid_type", type=str, default="columns", help="Grid Type: Columns or Rows")
        pars.add_argument("--columns", type=int, default=12, help="Number of columns/rows")
        pars.add_argument("--column_width", type=float, default=50, help="Width of each column/row (px)")
        pars.add_argument("--gutter", type=float, default=20, help="Gutter width (px)")
        pars.add_argument("--padding_width", type=float, default=10, help="Width of padding columns (px)")
        pars.add_argument("--fill_color", type=inkex.Color, default=inkex.Color("#ff00801a"), help="Fill color of the grid")

    def effect(self):
        canvas_width, canvas_height = self.get_canvas_dimensions()
        grid_type = self.options.grid_type
        count, size, gutter, padding_width, fill_color = self.get_user_parameters()

        if not self.validate_parameters(count, size, gutter, padding_width):
            inkex.errormsg("Invalid parameters. Please check your inputs.")
            return

        margin = self.calculate_margin(canvas_width if grid_type == "columns" else canvas_height, count, size, gutter)
        self.remove_existing_grid()
        
        if grid_type == "columns":
            self.create_columns_grid(count, size, gutter, padding_width, fill_color, margin, canvas_height)
        elif grid_type == "rows":
            self.create_rows_grid(count, size, gutter, padding_width, fill_color, margin, canvas_width)

    def get_canvas_dimensions(self):
        """Retrieve the canvas dimensions in pixels."""
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

    def calculate_margin(self, canvas_size, count, size, gutter):
        """Calculate the margin for centering the grid."""
        total_size = (count * size) + (gutter * (count - 1))
        return (canvas_size - total_size) / 2

    def remove_existing_grid(self):
        """Remove existing grid layers from the SVG."""
        grids = self.svg.xpath('//svg:g[@inkscape:label="Responsive Grid"]', namespaces=inkex.NSS)
        for grid in grids:
            grid.getparent().remove(grid)

    def create_columns_grid(self, count, width, gutter, padding_width, fill_color, margin, canvas_height):
        """Create a responsive columns grid."""
        grid_group = Layer()
        grid_group.set('inkscape:label', 'Responsive Grid')
        grid_group.set('sodipodi:insensitive', 'true')

        x = margin
        for _ in range(count):
            column = self.create_rectangle(x, 0, width, canvas_height, fill_color)
            grid_group.append(column)
            x += width + gutter

        self.svg.append(grid_group)

    def create_rows_grid(self, count, height, gutter, padding_width, fill_color, margin, canvas_width):
        """Create a responsive rows grid."""
        grid_group = Layer()
        grid_group.set('inkscape:label', 'Responsive Grid')
        grid_group.set('sodipodi:insensitive', 'true')

        y = margin
        for _ in range(count):
            row = self.create_rectangle(0, y, canvas_width, height, fill_color)
            grid_group.append(row)
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
    ResponsiveGrid().run()
