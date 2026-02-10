import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from src.models import FlyInData
import math


WIDTH=3840
HEIGHT=2160

class GraphicsEngine:
    def __init__(self, data: FlyInData) -> None:
        pygame.init()
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.data = data
        self.get_hub_size()
        self.get_dynamic_radius()
        # self.load_assets()

    def get_hub_size(self, padding=100):
        """
        hubs_raw_data: List of (x, y) tuples from your project data
        padding: pixels to keep away from the screen edge
        """
        # 1. Find the bounds of the raw data
        raw_x = [h.coords[0] for h in self.data.hubs.values()]
        raw_y = [h.coords[1] for h in self.data.hubs.values()]

        min_x, max_x = min(raw_x), max(raw_x)
        min_y, max_y = min(raw_y), max(raw_y)

        # 2. Calculate the "width" and "height" of the data area
        data_width = max_x - min_x if max_x != min_x else 1
        data_height = max_y - min_y if max_y != min_y else 1

        # 3. Calculate available screen space
        screen_w = self.width - (padding * 2)
        screen_h = self.height - (padding * 2)

        # 4. Determine scale (keeping aspect ratio)
        self.scale = min(screen_w / data_width, screen_h / data_height)

        # 5. Transform each point
        for hub in self.data.hubs.values():
            # Shift to 0, scale it, then move it to the center of screen
            new_x = padding + (hub.coords[0] - min_x) * self.scale
            new_y = padding + (hub.coords[1] - min_y) * self.scale
            hub.graphic_coords = (int(new_x), int(new_y))


    def get_dynamic_radius(self):
        coords = [h.graphic_coords for h in self.data.hubs.values()]
        if len(coords) < 2:
            return int(self.height * 0.02)

        min_dist = float('inf')
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = math.dist(coords[i], coords[j])
                if d < min_dist:
                    min_dist = d
        self.radius = max(5, int(self.scale * min_dist * 0.3))

    def load_assets(self) -> None:
        drone_original = pygame.image.load("assets/drone.png").convert()
        drone_original.set_colorkey(drone_original.get_at((0, 0)))

        width = 3 * self.radius
        ratio = drone_original.get_height() / drone_original.get_width()
        height = int(width * ratio)

        self.drone_img = pygame.transform.scale(drone_original, (width, height))

    def render(self):
        self.screen.fill((20, 20, 25)) # Dark navy background

        # 1. Draw Connections first (Lines)
        # Assuming your data has a list of connections (hub_id1, hub_id2)
        for connection in self.data.connections:
            start_id, end_id = connection.hubs
            start_pos = self.data.hubs[start_id].graphic_coords
            end_pos = self.data.hubs[end_id].graphic_coords
            pygame.draw.line(self.screen, (70, 70, 80), start_pos, end_pos, 20)

        # 2. Draw Hubs (Circles)
        for hub in self.data.hubs.values():
            # Draw a glow/shadow
            # pygame.draw.circle(self.screen, (0, 255, 255, 50), hub.graphic_coords, 100 + 4)
            # Draw the actual hub
            pygame.draw.circle(self.screen, (0, 200, 255), hub.graphic_coords, 50)

        pygame.display.flip()
