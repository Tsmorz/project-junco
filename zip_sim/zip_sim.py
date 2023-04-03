import argparse
import math
import os
import random
import sys
import subprocess
import struct

# Suppress hello from pygame so that stdout is clean
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame  # noqa

# The time step of the simulation. 60Hz is chosen to work well on most displays that are 60Hz.
DT_SEC = 1 / 60.0

# The visualizer may be sped up or slowed down (CPU cycles permitting)
VISUALIZER_RATES = [m / DT_SEC for m in (0.0625, 0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0)]
INITIAL_VISUALIZER_RATE_INDEX = 4
# How fast to poll the UI when paused, since it's no longer coupled to the sim rate.
PAUSED_RATE = 30

# The world size in meters. It's a bit weird because the world wraps around itself. The world's coordinate system is
# always considered to be in the positive quadrant (coordinates in the world frame are always >= 0).
WORLD_WIDTH = 50.0
WORLD_LENGTH = 2000.0

# Scale is the size of each graphical pixel, in meters. This number is hardcoded into the artwork, and can't be easily
# changed.
SCALE = 0.1
# Sreen width must match world width for things to render properly, since the world is narrow enough to visually wrap.
SCREEN_WIDTH = round(WORLD_WIDTH / SCALE)
# Screen height is fairly arbitrary. It's chosen to fit on most modern resolutions.
SCREEN_HEIGHT = 700
# How far ahead the camera follows the vehicle. If 0, the zip will be in the center of the screen.
CAMERA_AHEAD_M = 20.0

# Pre-computed to make calculations faster
WORLD_WIDTH_HALF = WORLD_WIDTH / 2.0
WORLD_LENGTH_HALF = WORLD_LENGTH / 2.0
SCREEN_WIDTH_HALF = SCREEN_WIDTH // 2
SCREEN_HEIGHT_HALF = SCREEN_HEIGHT // 2

# How long it takes for the package to "fall" and hit the ground after being released.
PACKAGE_FALL_SEC = 0.5

# The coordinates of the recovery system. The simulation ends after the vehicle crosses the X coordinate.
# The vehicle is considered "recovered" if it's within the Y bounds.
RECOVERY_X = WORLD_LENGTH - 5
RECOVERY_Y_MIN = 7.5
RECOVERY_Y_MAX = WORLD_WIDTH - 7.5

NUM_DELIVERY_SITES = 10
TYPICAL_NUM_TREES = 20
MAX_NUM_TREES = 100

# The vehicle always moves with constant forward airspeed. Its groundspeed varies based on the wind.
VEHICLE_AIRSPEED = 30.0
MAX_WINDSPEED_M_S = 20.0

# Coordinates to keep generated delivery sites within.
DELIVERY_SITE_X_BOUNDS = (100.0, WORLD_LENGTH - 100.0)  # Avoid distribution center
DELIVERY_SITE_Y_BOUNDS = (-WORLD_WIDTH_HALF + 5.0, WORLD_WIDTH_HALF - 5.0)  # Avoid wrap-around
# Minimum distance between delivery sites
MIN_DELIVERY_DISTANCE = 100.0

TREE_X_BOUNDS = (50.0, WORLD_LENGTH - 50.0)  # Avoid distribution center
# Minimum distance from trees to delivery sites. Trees are allowed to overlap.
MIN_TREE_DISTANCE = 10.0

# The max distance the lidar works to. Any ray that travels farther will be reported as 0.
LIDAR_MAX_DISTANCE = 255

# The angles to sweep the lidar across.
LIDAR_ANGLES = [(i - 15.0) * math.pi / 180 for i in range(0, 31)]  # -15 to +15 degrees, 1 degree steps.

DELIVERY_SITE_RADIUS = 5.0
DELIVERY_SITE_LIDAR_RADIUS = 0.5

# Make the tree a little bit smaller for collisions than it is visible. This gives the pilot some margin. It also
# makes a fair amount of intuitive sense since a real tree is rounded, and a zip's wing would probably survive a light
# scraping on some branches.
TREE_COLLISION_RADIUS = 2.0
TREE_LIDAR_RADIUS = 3.0

# Structs used to pack/unpack the API messages
# milliseconds [2 bytes]
# wind_x [4 bytes]
# wind_y [4 bytes]
# recovery_x error [2 bytes]
# recovery_y error [1 byte]
# 31 lidar samples [31 bytes]
TELEMETRY_STRUCT = struct.Struct(">Hhffb31B")
COMMAND_STRUCT = struct.Struct(">fB3s")

# Return codes for why the simulation ended
RECOVERED = 0
PARALANDED = 1
CRASHED = 2
SIM_QUIT = 3


def load_image(name):
    return pygame.image.load(os.path.join(os.path.dirname(__file__), "art", name))


class Entity():
    __slots__ = ["position"]

    def __init__(self, position):
        x, y = position
        self.position = (x % WORLD_LENGTH, y % WORLD_WIDTH)

    def move(self, delta):
        v_x, v_y = delta
        self.position = ((self.position[0] + v_x) % WORLD_LENGTH, (self.position[1] + v_y) % WORLD_WIDTH)

    def distance_to(self, position):
        delta_x = abs(self.position[0] - position[0])
        delta_y = abs(self.position[1] - position[1])
        if delta_x > WORLD_LENGTH_HALF:
            delta_x = WORLD_LENGTH - delta_x
        if delta_y > WORLD_WIDTH_HALF:
            delta_y = WORLD_WIDTH - delta_y
        return math.sqrt(delta_x * delta_x + delta_y * delta_y)


class Camera(Entity):
    __slots__ = ["_scale_inv"]

    def __init__(self, position, scale=SCALE):
        super().__init__(position)
        self._scale_inv = 1.0 / scale

    def project(self, position):
        """ Projects a point in world coordinates to points in camera pixel space. """
        camera_x, camera_y = self.position
        # world Y / screen X gets wrapped asymmetrically because it gets projected twice
        projected_x = round(-((position[1] - camera_y) % WORLD_WIDTH) * self._scale_inv + SCREEN_WIDTH_HALF)
        # World X / screen Y gets wrapped symmetrically since it's assumed no object will visually wrap
        projected_y = round(-(((position[0] - camera_x) + WORLD_LENGTH_HALF) % WORLD_LENGTH - WORLD_LENGTH_HALF) *
                            self._scale_inv + SCREEN_HEIGHT_HALF)
        # Things are expected to readily wrap in the world y axis / screen x axis, and be visible in
        # multiple places at once.
        return ((projected_x, projected_y), (projected_x + SCREEN_WIDTH, projected_y))

    def scale(self, distance):
        return distance * self._scale_inv


class Package(Entity):
    __slots__ = ["_velocity", "_fall_duration"]

    _parachute_image = load_image("package_parachute.png")
    _package_image = load_image("package.png")

    def __init__(self, position, velocity, fall_duration=PACKAGE_FALL_SEC):
        super().__init__(position)
        self._velocity = velocity
        self._fall_duration = fall_duration

    def update(self, dt):
        dt = min(dt, self._fall_duration)
        self._fall_duration -= dt
        self.move((dt * self._velocity[0], dt * self._velocity[1]))

    def draw(self, camera, surface):
        for projected_pos in camera.project(self.position):
            if self._fall_duration > 0:
                surface.blit(self._parachute_image, (projected_pos[0] - 4, projected_pos[1] - 4))

            else:
                surface.blit(self._package_image, (projected_pos[0] - 4, projected_pos[1] - 4))


class Circle(Entity):
    __slots__ = ["radius"]

    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius

    def contains(self, position):
        delta_x = abs(self.position[0] - position[0])
        delta_y = abs(self.position[1] - position[1])
        if delta_x > WORLD_LENGTH_HALF:
            delta_x = WORLD_LENGTH - delta_x
        if delta_y > WORLD_WIDTH_HALF:
            delta_y = WORLD_WIDTH - delta_y
        return delta_x * delta_x + delta_y * delta_y < self.radius * self.radius


class Zip(Circle):
    __slots__ = []
    _image = load_image("zip.png")

    def __init__(self):
        super().__init__(position=(0.0, 0.0), radius=1.6)

    def get_velocity(self, lateral_airspeed, windspeed_vector):
        return (VEHICLE_AIRSPEED + windspeed_vector[0], lateral_airspeed + windspeed_vector[1])

    def update(self, dt, lateral_airspeed, windspeed_vector):
        v_x, v_y = self.get_velocity(lateral_airspeed, windspeed_vector)
        self.move((dt * v_x, dt * v_y))

    def draw(self, camera, surface):
        for projected_pos in camera.project(self.position):
            surface.blit(self._image, (projected_pos[0] - 16, projected_pos[1] - 16))


class DeliverySite(Circle):
    __slots__ = []
    _image = load_image("delivery_site.png")

    def __init__(self, position):
        super().__init__(position, radius=DELIVERY_SITE_RADIUS)

    def draw(self, camera, surface):
        for projected_pos in camera.project(self.position):
            surface.blit(self._image, (projected_pos[0] - 64, projected_pos[1] - 64))

    def make_lidar_object(self):
        return Circle(self.position, radius=DELIVERY_SITE_LIDAR_RADIUS)


class Tree(Circle):
    __slots__ = []
    _image = load_image("tree.png")

    def __init__(self, position):
        super().__init__(position, radius=TREE_COLLISION_RADIUS)

    def draw(self, camera, surface):
        for projected_pos in camera.project(self.position):
            surface.blit(self._image, (projected_pos[0] - 32, projected_pos[1] - 32))

    def make_lidar_object(self):
        return Circle(self.position, radius=TREE_LIDAR_RADIUS)


class Wind():
    __slots__ = ["_speed", "_direction"]

    def __init__(self):
        self._speed = random.uniform(0.0, MAX_WINDSPEED_M_S)
        self._direction = random.uniform(0.0, 2 * math.pi)

    def update(self, dt):
        # TODO: Scale sigma?
        self._speed = max(0.0, min(MAX_WINDSPEED_M_S, self._speed + random.gauss(0.0, dt * 10)))
        self._direction = (self._direction + random.gauss(0.0, dt)) % (2 * math.pi)

    @property
    def vector(self):
        return (self._speed * math.cos(self._direction), self._speed * math.sin(self._direction))


class Terrain():
    __slots__ = []
    _image = load_image("terrain.png")

    def draw(self, camera, surface):
        # There's probably a better way to do this, but as long as it works...
        for x in range(0, int(WORLD_LENGTH), 100):
            for projected_pos in camera.project((x, 0.0)):
                surface.blit(self._image, (projected_pos[0] - 250, projected_pos[1] - 1000))


def cast_lidar_ray(angle, circles):
    # First, find all circles the ray collides with by seeing if the ray's minimum distance is within the circle radius.
    # A line may be parameterized as ax + by + c = 0.
    # The shortest distance between a point (x, y) and a line is equal to:
    # |ax + by + c| / sqrt(a*a + b*b)
    # Since the ray starts at the origin, c is zero. The values of a and b depend on the sin and cosine of the angle,
    # which has the nice property of lying on the unit circle.
    a = math.sin(angle)
    b = -math.cos(angle)
    distance = LIDAR_MAX_DISTANCE + 1
    for o in circles:
        if o[0] * o[0] + o[1] * o[1] <= o[2] * o[2]:
            return 0  # We're inside the object. Pretend that the lidar is blind.
        # Negating c seems to make the code produce the right result, but I don't really understand why.
        signed_c = -(a * o[0] + b * o[1])
        # Because of wraparound, we want the y position that minimizes distance. We need to know the number of
        # wraps so that we can translate the circle appropriately
        num_wraps = round(signed_c / (b * WORLD_WIDTH))
        # Negating c seems to make the code produce the right result, but I don't really understand why.
        signed_c -= num_wraps * b * WORLD_WIDTH
        if abs(signed_c) < o[2]:
            # The ray intersects with this circle. We need to find that point of intersection.
            # We can now think of the circle being at the origin, and the line being offset by c.
            gnarly_math = math.sqrt(o[2] * o[2] - signed_c * signed_c)
            # Translate the final result back to the circle's position
            x = a * signed_c + b * gnarly_math + o[0]
            y = b * signed_c - a * gnarly_math + o[1] + num_wraps * WORLD_WIDTH
            d = math.sqrt(x*x + y*y)
            if d < distance:
                distance = round(d)
    return distance if distance <= LIDAR_MAX_DISTANCE else 0


def cast_lidar(start_pos, objects):
    # Remove objects that are behind the vehicle, and shift the positions to be in the vehicle's frame
    relative_objects = [(o.position[0] - start_pos[0],
                         (o.position[1] - start_pos[1] + WORLD_WIDTH_HALF) % WORLD_WIDTH - WORLD_WIDTH_HALF,
                         o.radius) for o in objects if o.position[0] > start_pos[0]]
    return [cast_lidar_ray(angle, relative_objects) for angle in LIDAR_ANGLES]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='"8-bit" Zip Sim')
    parser.add_argument('pilot', nargs=argparse.REMAINDER, help='A pilot process to run')
    parser.add_argument('--headless', action="store_true", help='Run without visualization')
    visualizer_group = parser.add_argument_group("Visualization options")
    visualizer_group.add_argument('--chase-y', action="store_true", help='Have the camera follow the zip in the y axis')
    visualizer_group.add_argument('--show-lidar', action="store_true", help='Shows lidar in the visualization')
    visualizer_group.add_argument('--start-paused', action="store_true", help='Start the simulation paused')
    parser.add_argument('--seed', type=int, help='Seed to use for random number generation')
    args = parser.parse_args()

    random.seed(args.seed)
    headless = args.headless
    api_mode = len(args.pilot) > 0

    if api_mode:
        pilot = subprocess.Popen(args.pilot, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        loop_count = 0  # To count iterations to compute the telemetry timestamp

    if not headless:
        pygame.init()
        pygame.display.set_caption("Zip Sim")
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        clock = pygame.time.Clock()
        camera = Camera(position=(CAMERA_AHEAD_M, 0.0))
        distribution_center_image = load_image("distribution_center.png")
        terrain = Terrain()
        reticle_image = load_image("reticle.png")
        chase_y = args.chase_y
        show_lidar = args.show_lidar
        visualizer_paused = args.start_paused
        visualizer_rate_index = INITIAL_VISUALIZER_RATE_INDEX

    # Randomly generate delivery sites that aren't too close to each other.
    delivery_sites = []
    for _ in range(NUM_DELIVERY_SITES):
        while True:
            # Round the position to the nearest tenth of a meter. This keeps the sprites from jumping around while
            # drawing due to floating point round-off to the nearest pixel.
            site_pos = (round(random.uniform(*DELIVERY_SITE_X_BOUNDS) % WORLD_LENGTH, 1),
                        round(random.uniform(*DELIVERY_SITE_Y_BOUNDS) % WORLD_WIDTH, 1))
            if min((s.distance_to(site_pos) for s in delivery_sites),
                   default=MIN_DELIVERY_DISTANCE) >= MIN_DELIVERY_DISTANCE:
                delivery_sites.append(DeliverySite(site_pos))
                break

    # Randomly generate trees that aren't too close to delivery sites.
    trees = []
    tree_density = random.gauss(TYPICAL_NUM_TREES, MAX_NUM_TREES / 3)
    num_trees = round(min(MAX_NUM_TREES, tree_density) if tree_density >= TYPICAL_NUM_TREES
                      else random.triangular(0, TYPICAL_NUM_TREES, TYPICAL_NUM_TREES))
    for _ in range(num_trees):
        while True:
            # Round the position to the nearest tenth of a meter. This keeps the sprites from jumping around while
            # drawing due to floating point round-off to the nearest pixel.
            tree_pos = (round(random.uniform(*TREE_X_BOUNDS), 1),
                        round(random.uniform(0, WORLD_WIDTH), 1))
            if min((s.distance_to(tree_pos) for s in delivery_sites), default=MIN_TREE_DISTANCE) >= MIN_TREE_DISTANCE:
                trees.append(Tree(tree_pos))
                break
    # Trees can overlap, so sort them so they render over each other properly.
    trees.sort(key=lambda x: x.position[0], reverse=True)

    # A list of objects that reflect lidar points
    lidar_objects = [t.make_lidar_object() for t in trees] + [d.make_lidar_object() for d in delivery_sites]

    vehicle = Zip()

    # Set to an exit code when it's time to leave the main loop
    result = None

    wind = Wind()
    lateral_airspeed = 0.0
    # Used to de-bounce commands to drop a package
    was_package_dropped = False
    # Number of packages still in the zip
    num_packages = len(delivery_sites)
    # List of package objects that have been dropped
    dropped_packages = []

    while result is None:
        drop_package_commanded = False
        if api_mode:
            lidar_samples = cast_lidar(vehicle.position, lidar_objects)
            pilot.stdin.write(TELEMETRY_STRUCT.pack(int(loop_count * DT_SEC * 1e3) & 0xFFFF,
                                                    round(RECOVERY_X - vehicle.position[0]),
                                                    wind.vector[0],
                                                    wind.vector[1],
                                                    round((-vehicle.position[1] + WORLD_WIDTH_HALF) % WORLD_WIDTH -
                                                          WORLD_WIDTH_HALF),
                                                    *lidar_samples))
            pilot.stdin.flush()
            loop_count += 1
            cmd = pilot.stdout.read(COMMAND_STRUCT.size)
            if len(cmd) != COMMAND_STRUCT.size:
                result = CRASHED  # The pilot process must have exited
                break
            lateral_airspeed_input, drop_package_commanded_byte, _ = COMMAND_STRUCT.unpack(cmd)
            lateral_airspeed = max(-30.0, min(30.0, lateral_airspeed_input))
            drop_package_commanded = bool(drop_package_commanded_byte)
        elif not headless:
            keys = pygame.key.get_pressed()
            lateral_airspeed -= lateral_airspeed / 0.5 * DT_SEC
            if keys[pygame.K_LEFT]:
                lateral_airspeed = min(30.0, lateral_airspeed + DT_SEC * 200.0)
            if keys[pygame.K_RIGHT]:
                lateral_airspeed = max(-30.0, lateral_airspeed - DT_SEC * 200.0)
            if keys[pygame.K_SPACE]:
                drop_package_commanded = True

        vehicle.update(DT_SEC, lateral_airspeed, wind.vector)

        # Check for collisions with trees
        for t in trees:
            if t.contains(vehicle.position):
                result = CRASHED
                break

        for p in dropped_packages:
            p.update(DT_SEC)

        # Drop a package if commanded to. The package is dropped after updating physics so that we can
        # append it right on to the end of the dropped packages list. This adds some "realism" since a
        # real mechanism would release the package some time after being commanded to.
        if drop_package_commanded and not was_package_dropped and num_packages > 0:
            num_packages -= 1
            dropped_packages.append(Package(vehicle.position, vehicle.get_velocity(lateral_airspeed, wind.vector)))

        was_package_dropped = drop_package_commanded

        wind.update(DT_SEC)

        vehicle_x, vehicle_y = vehicle.position
        if vehicle_x >= RECOVERY_X:
            result = RECOVERED if vehicle_y <= RECOVERY_Y_MIN or vehicle_y >= RECOVERY_Y_MAX else PARALANDED
            break

        if not headless:
            # Update the camera to be fixed above the vehicle in the x axis.
            camera.position = (vehicle.position[0] + CAMERA_AHEAD_M, vehicle.position[1] if chase_y else 0.0)

            terrain.draw(camera, screen)
            # Draw distribution center
            for pos in camera.project((0, 0)):
                screen.blit(distribution_center_image, (pos[0] - 250, pos[1] - 100))

            for t in trees:
                t.draw(camera, screen)
            for s in delivery_sites:
                s.draw(camera, screen)
            for p in dropped_packages:
                p.draw(camera, screen)

            if show_lidar:
                # We could try to be clever and avoid casting the lidar twice if in API mode, but there's no real need
                # since we have plenty of CPU cycles when running in real-time.
                lidar_samples = cast_lidar(vehicle.position, lidar_objects)
                for angle, d in zip(LIDAR_ANGLES, lidar_samples):
                    x = d * math.cos(angle)
                    y = d * math.sin(angle)
                    for pos in camera.project(vehicle.position):
                        pygame.draw.line(screen, "red", pos, (round(pos[0] - camera.scale(y)),
                                                              round(pos[1] - camera.scale(x))))

            vehicle.draw(camera, screen)

            # Compute where a package would drop and draw a reticle there
            reticle = Entity(vehicle.position)
            reticle.move((v * PACKAGE_FALL_SEC for v in vehicle.get_velocity(lateral_airspeed, wind.vector)))
            for pos in camera.project(reticle.position):
                screen.blit(reticle_image, (pos[0] - 8, pos[1] - 8))

            pygame.display.flip()

            # This loop is a little gnarly since python lacks a do-while loop. We want to run at least once no
            # matter what, and run repeatedly if the simulation is paused.
            wait_for_step = True
            while wait_for_step:
                for e in pygame.event.get():
                    if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                        result = SIM_QUIT
                        wait_for_step = False
                        break
                    if e.type in [pygame.KEYDOWN]:
                        if e.key == pygame.K_p:
                            visualizer_paused = not visualizer_paused
                        if e.key == pygame.K_s and visualizer_paused:
                            wait_for_step = False
                            break  # Run another cycle before reading any more events
                        if e.key == pygame.K_COMMA:
                            visualizer_rate_index = max(0, visualizer_rate_index - 1)
                        if e.key == pygame.K_PERIOD:
                            visualizer_rate_index = min(len(VISUALIZER_RATES) - 1, visualizer_rate_index + 1)
                if wait_for_step:
                    # There's two things going on here. First, if single-stepped, we don't want to delay the loop.
                    # Otherwise, we want to delay the loop a consistent amount if paused, or at the time-warped rate if
                    # unpaused. This keeps the UI snappy while single-stepping.
                    if visualizer_paused:
                        clock.tick(PAUSED_RATE)
                    else:
                        clock.tick(VISUALIZER_RATES[visualizer_rate_index])
                        wait_for_step = False

    if not headless:
        pygame.quit()

    # Count delivered packages, looking for double deliveries
    package_count_by_site = {}
    for p in dropped_packages:
        # Make sure the package is at rest
        p.update(PACKAGE_FALL_SEC)
        for s in delivery_sites:
            if s.contains(p.position):
                try:
                    package_count_by_site[s] += 1
                except KeyError:
                    package_count_by_site[s] = 1

    if api_mode:
        pilot.stdin.close()
        pilot.stdout.close()
        pilot.wait()
    print("Deliveries: {}".format(len(package_count_by_site)))
    print("ZIPAA Violations: {}".format(sum((x - 1 for x in package_count_by_site.values() if x > 1))))
    sys.exit(result)
