import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from src.models import FlyInData, Drone
import math


WIDTH = 1920 # 3840
HEIGHT = 1080 # 2160
MID_WIDTH = WIDTH / 2
MID_HEIGHT = HEIGHT / 2

class GraphicsEngine:
    def __init__(self, data: FlyInData, drones: list[Drone]) -> None:
        pygame.init()
        self.width = WIDTH
        self.height = HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.data = data
        self.get_hub_size()
        self.drones = drones
        self.load_assets()


    def get_hub_size(self):
        """
        hubs_raw_data: List of (x, y) tuples from your project data
        padding: pixels to keep away from the screen edge
        """
        # 1. Find the bounds of the raw data
        raw_x = [h.coords[0] for h in self.data.hubs.values()]
        raw_y = [h.coords[1] for h in self.data.hubs.values()]

        min_x, max_x = min(raw_x), max(raw_x)
        min_y, max_y = min(raw_y), max(raw_y)
        mid_x, mid_y = (max_x + min_x) / 2, (max_y + min_y) / 2


        # 2. Calculate the "width" and "height" of the data area
        data_width = max_x - min_x + 2
        data_height = max_y - min_y + 2

        # 4. Determine scale (keeping aspect ratio)
        self.scale = min(self.width / data_width, self.height / data_height)
        self.radius = int(self.scale / 4)
        self.connection_width = self.radius // 4
        # 5. Transform each point
        for hub in self.data.hubs.values():
            # Shift to 0, scale it, then move it to the center of screen
            new_x = MID_WIDTH + (hub.coords[0] - mid_x) * self.scale
            new_y = MID_HEIGHT - (hub.coords[1] - mid_y) * self.scale
            hub.graphic_coords = (int(new_x), int(new_y))

    def load_assets(self) -> None:
        drone_original = pygame.image.load("assets/drone.png").convert()
        drone_original.set_colorkey(drone_original.get_at((0, 0)))
        width = 3 * self.radius
        ratio = drone_original.get_height() / drone_original.get_width()
        height = int(width * ratio)
        self.drone_img = pygame.transform.scale(drone_original, (width, height))
        for drone in self.drones:
            drone.drone_graphics = self.drone_img.get_rect(center=self.data.hubs[self.data.start].graphic_coords)

    def render(self):
        self.screen.fill((20, 20, 25)) # Dark navy background

        # 1. Draw Connections first (Lines)
        # Assuming your data has a list of connections (hub_id1, hub_id2)
        for connection in self.data.connections:
            start_id, end_id = connection.hubs
            start_pos = self.data.hubs[start_id].graphic_coords
            end_pos = self.data.hubs[end_id].graphic_coords
            pygame.draw.line(self.screen, (70, 70, 80), start_pos, end_pos, self.connection_width)

        # 2. Draw Hubs (Circles)
        for hub in self.data.hubs.values():
            pygame.draw.circle(self.screen, hub.color_data.rgb, hub.graphic_coords, self.radius)
        for drone in self.drones:
            self.screen.blit(self.drone_img, drone.drone_graphics)

        pygame.display.flip()
