
import math

SIDES = 5  # pentagon


def _ring(radius, y, sides=SIDES, rotation_offset=math.pi / 2):
    
    pts = []
    for i in range(sides):
        theta = rotation_offset + (2 * math.pi * i / sides)
        x = radius * math.cos(theta)
        z = radius * math.sin(theta)
        pts.append((x, y, z))
    return pts


class PentagonCup:
    

    def __init__(self, height=2.0, outer_radius=1.0, wall_ratio=0.82, base_thickness=0.18):
        self.height = height
        self.outer_radius = outer_radius
        self.inner_radius = outer_radius * wall_ratio
        self.base_thickness = base_thickness

        y_bottom = -height / 2
        y_base_top = y_bottom + base_thickness
        y_top = height / 2

        # Rings
        self.outer_bottom = _ring(self.outer_radius, y_bottom)
        self.outer_top = _ring(self.outer_radius, y_top)
        self.inner_bottom = _ring(self.inner_radius, y_base_top)
        self.inner_top = _ring(self.inner_radius, y_top)

        self._build_faces()

    
    def _quad_strip(self, ring_a, ring_b):
        """Build quads (as vertex tuples) connecting two same-size rings."""
        n = len(ring_a)
        faces = []
        for i in range(n):
            j = (i + 1) % n
            faces.append((ring_a[i], ring_a[j], ring_b[j], ring_b[i]))
        return faces

    def _fan(self, ring, center, flip=False):
        n = len(ring)
        faces = []
        for i in range(n):
            j = (i + 1) % n
            if flip:
                faces.append((center, ring[j], ring[i]))
            else:
                faces.append((center, ring[i], ring[j]))
        return faces

    def _build_faces(self):
        faces = []

        faces += self._quad_strip(self.outer_bottom, self.outer_top)

        faces += self._quad_strip(self.inner_top, self.inner_bottom)

        faces += self._quad_strip(self.inner_bottom, self.outer_bottom)

        base_center = (0.0, self.outer_bottom[0][1], 0.0)
        faces += self._fan(self.outer_bottom, base_center, flip=True)

        floor_center = (0.0, self.inner_bottom[0][1], 0.0)
        faces += self._fan(self.inner_bottom, floor_center, flip=False)

        faces += self._quad_strip(self.outer_top, self.inner_top)

        self.faces = faces

    @staticmethod
    def _face_normal(face):
        
        ax, ay, az = face[0]
        bx, by, bz = face[1]
        cx, cy, cz = face[2]
        u = (bx - ax, by - ay, bz - az)
        v = (cx - ax, cy - ay, cz - az)
        nx = u[1] * v[2] - u[2] * v[1]
        ny = u[2] * v[0] - u[0] * v[2]
        nz = u[0] * v[1] - u[1] * v[0]
        length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
        return (nx / length, ny / length, nz / length)

    def iter_faces_with_normals(self):
        for face in self.faces:
            yield face, self._face_normal(face)

   
    def cavity_y_range(self):
        
        y_floor = self.inner_bottom[0][1]
        y_rim = self.inner_top[0][1]
        return y_floor, y_rim

    def liquid_surface_polygon(self, fill_fraction):
        
        fill_fraction = max(0.0, min(1.0, fill_fraction))
        y_floor, y_rim = self.cavity_y_range()
        y = y_floor + fill_fraction * (y_rim - y_floor)
        
        radius = self.inner_radius * 0.985
        return _ring(radius, y)

    def liquid_wall_faces(self, fill_fraction):
       
        fill_fraction = max(0.0, min(1.0, fill_fraction))
        if fill_fraction <= 0.0:
            return []
        y_floor, y_rim = self.cavity_y_range()
        y = y_floor + fill_fraction * (y_rim - y_floor)
        radius = self.inner_radius * 0.985
        bottom_ring = _ring(radius, y_floor + 1e-4)
        top_ring = _ring(radius, y)
        return self._quad_strip(bottom_ring, top_ring)


class LiquidState:

    FILL_RATE = 1.2          
    SPILL_ANGLE = math.radians(20)    
    MIN_POUR_RATE = 0.6      
    MAX_POUR_RATE = 2.2     
    def __init__(self):
        self.level = 0.0
        self.pouring = False

    def fill(self, pinch_active, dt):
        if pinch_active and self.level < 1.0:
            self.level = min(1.0, self.level + self.FILL_RATE * dt)

    def update_pour(self, tilt_angle_rad, dt):
        tilt = abs(tilt_angle_rad)
        if tilt > self.SPILL_ANGLE and self.level > 0.0:
            span = max(1e-4, (math.pi / 2) - self.SPILL_ANGLE)
            t = min(1.0, (tilt - self.SPILL_ANGLE) / span)
            rate = self.MIN_POUR_RATE + (self.MAX_POUR_RATE - self.MIN_POUR_RATE) * t
            self.level = max(0.0, self.level - rate * dt)
            self.pouring = self.level > 0.0
        else:
            self.pouring = False

    def reset(self):
        self.level = 0.0
        self.pouring = False
