class UnitManager:
    def __init__(self):
        self.units = []

    def add_unit(self, unit_params):
        self.units.append(unit_params)

    def get_units(self):
        return self.units

    def get_unit(self, index):
        return self.units[index]

    def update_unit(self, index, new_params):
        self.units[index] = new_params

    def delete_unit(self, index):
        if 0 <= index < len(self.units):
            del self.units[index]

    def reset(self):
        self.units = []

    def get_all_units(self):
        return self.get_units()

    def get_unit_color(self, unit_id):
        for unit in self.units:
            if unit["id"] == unit_id:
                return unit.get("color", "#CCCCCC")  # default gray
        return "#CCCCCC"

    def get_bounds(self):
        x_vals = []
        y_vals = []

        for unit in self.units:
            geometry = unit.get("geometry", [])
            for point in geometry:
                x_vals.append(point[0])
                y_vals.append(point[1])

        if not x_vals or not y_vals:
            return (0, 1, 0, 1)  # fallback bounds

        return (min(x_vals), max(x_vals), min(y_vals), max(y_vals))
