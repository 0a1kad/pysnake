import pygame
import random
import math
import sys
import wave
import io
import struct

# Initialize Pygame & Mixer for Audio
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)
pygame.font.init()

# Resolution Setup & Fullscreen
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pysnake.io")

# Theme Colors & Constants
BG_COLOR = (12, 15, 24)
GRID_COLOR = (22, 28, 42)
WHITE = (255, 255, 255)
BLACK = (10, 10, 15)
BORDER_COLOR = (231, 76, 60)
RED = (231, 76, 60)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
YELLOW = (241, 196, 15)

# Expanded Customization Options
COLOR_PALETTE = [
    ("Emerald Green", (46, 204, 113)),
    ("Neon Cyan", (52, 152, 219)),
    ("Crimson Red", (231, 76, 60)),
    ("Royal Purple", (155, 89, 182)),
    ("Solar Yellow", (241, 196, 15)),
    ("Blaze Orange", (230, 126, 34)),
    ("Hot Pink", (255, 105, 180)),
    ("Electric Lime", (124, 252, 0)),
    ("Deep Indigo", (75, 0, 130)),
    ("Turquoise", (64, 224, 208))
]

FACE_STYLES = ["Standard", "Cute", "Angry", "Cyclops", "Shades", "Winking", "Laser Eyes"]
PATTERN_STYLES = ["Solid", "Striped", "Glow Rings", "Polka Dots", "Neon Spine"]

# Fonts
FONT_TITLE = pygame.font.SysFont("Trebuchet MS", 86, bold=True)
FONT_SUBTITLE = pygame.font.SysFont("Trebuchet MS", 34, bold=True)
FONT_MENU = pygame.font.SysFont("Segoe UI", 26, bold=True)
FONT_HUD = pygame.font.SysFont("Segoe UI", 26, bold=True)
FONT_HELP = pygame.font.SysFont("Segoe UI", 24, bold=True)

# World Size
WORLD_WIDTH = 3500
WORLD_HEIGHT = 3500

# Global Settings
settings = {
    "graphics": "High",       # Low, Medium, High, Ultra
    "refresh_rate": 60,       # 60, 120, 240, 0 (Unlimited)
    "fps_counter": True,
    "motion_blur": "Off",     # Off, Low, Medium, High
    "sensitivity": 50,        # 0 to 100
    "sfx_volume": 80          # 0 to 100
}

# Player Customization Settings
player_style = {
    "color_idx": 0,
    "face_idx": 0,
    "pattern_idx": 0
}

# Procedural Sound Generators
def generate_click_sound():
    sample_rate = 22050
    duration = 0.04
    num_samples = int(sample_rate * duration)
    rest = io.BytesIO()
    w = wave.open(rest, 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sample_rate)
    data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        val = int(20000 * math.sin(2 * math.pi * 1000 * t) * (1 - i / num_samples))
        val = max(-32768, min(32767, val))
        data.extend(struct.pack('<h', val))
    w.writeframes(data)
    w.close()
    rest.seek(0)
    return pygame.mixer.Sound(rest)

def generate_pop_sound():
    sample_rate = 22050
    duration = 0.06
    num_samples = int(sample_rate * duration)
    rest = io.BytesIO()
    w = wave.open(rest, 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sample_rate)
    data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        freq = 700 - t * 6000
        val = int(25000 * math.sin(2 * math.pi * max(150, freq) * t) * (1 - i / num_samples))
        val = max(-32768, min(32767, val))
        data.extend(struct.pack('<h', val))
    w.writeframes(data)
    w.close()
    rest.seek(0)
    return pygame.mixer.Sound(rest)

def generate_crash_sound():
    sample_rate = 22050
    duration = 0.15
    num_samples = int(sample_rate * duration)
    rest = io.BytesIO()
    w = wave.open(rest, 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sample_rate)
    data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        val = int(28000 * (random.random() * 2 - 1) * math.exp(-t * 15))
        val = max(-32768, min(32767, val))
        data.extend(struct.pack('<h', val))
    w.writeframes(data)
    w.close()
    rest.seek(0)
    return pygame.mixer.Sound(rest)

def generate_boom_sound():
    sample_rate = 22050
    duration = 0.35
    num_samples = int(sample_rate * duration)
    rest = io.BytesIO()
    w = wave.open(rest, 'w')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(sample_rate)
    data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        val = int(20000 * math.sin(2 * math.pi * 70 * t) * math.exp(-t * 7) + 10000 * (random.random() * 2 - 1) * math.exp(-t * 10))
        val = max(-32768, min(32767, val))
        data.extend(struct.pack('<h', val))
    w.writeframes(data)
    w.close()
    rest.seek(0)
    return pygame.mixer.Sound(rest)

SOUND_CLICK = generate_click_sound()
SOUND_POP = generate_pop_sound()
SOUND_CRASH = generate_crash_sound()
SOUND_BOOM = generate_boom_sound()

def play_sfx(sound):
    vol = (settings["sfx_volume"] / 100.0)
    sound.set_volume(vol)
    sound.play()

class Orb:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.color = color if color else random.choice([c[1] for c in COLOR_PALETTE])
        
        roll = random.random()
        if roll < 0.60:
            self.radius = 4
            self.value = 1
        elif roll < 0.90:
            self.radius = 6
            self.value = 3
        else:
            self.radius = 9
            self.value = 7

        self.base_radius = self.radius

    def draw(self, surf, cam_x, cam_y, graphics):
        sx = self.x - cam_x
        sy = self.y - cam_y
        if -40 < sx < WIDTH + 40 and -40 < sy < HEIGHT + 40:
            pulse = math.sin(pygame.time.get_ticks() * 0.004 + self.x) * 1.5
            current_radius = max(3, int(self.base_radius + pulse))
            
            if graphics in ["High", "Ultra"]:
                glow_surf = pygame.Surface((current_radius * 6, current_radius * 6), pygame.SRCALPHA)
                glow_alpha = 100 if graphics == "Ultra" else 70
                pygame.draw.circle(glow_surf, (*self.color, glow_alpha), (current_radius * 3, current_radius * 3), current_radius * 2.2)
                surf.blit(glow_surf, (sx - current_radius * 3, sy - current_radius * 3))

            pygame.draw.circle(surf, self.color, (int(sx), int(sy)), current_radius)
            if graphics == "Ultra":
                pygame.draw.circle(surf, WHITE, (int(sx - 1), int(sy - 1)), max(1, current_radius // 3))

class Snake:
    def __init__(self, x, y, name="Player", is_bot=False, color=(46, 204, 113), face="Standard", pattern="Solid"):
        self.x = x
        self.y = y
        self.name = name
        self.is_bot = is_bot
        self.color = color
        self.face = face
        self.pattern = pattern
        self.angle = random.uniform(0, math.pi * 2)
        self.target_angle = self.angle
        self.turn_speed = 0.09
        self.speed = 4.5
        self.radius = 15
        self.length = 22
        
        self.segments = []
        for i in range(self.length):
            self.segments.append((x - math.cos(self.angle) * i * 6.5, y - math.sin(self.angle) * i * 6.5))
            
        self.score = 0
        self.alive = True
        self.ai_timer = 0

    def update(self, dt, snakes, orbs):
        if not self.alive:
            return

        if self.is_bot:
            self.ai_timer += dt * 60
            danger = False
            for other in snakes:
                if other == self or not other.alive: continue
                for seg in other.segments[::2]:
                    dist = math.hypot(self.x - seg[0], self.y - seg[1])
                    if dist < 140:
                        avoid_angle = math.atan2(self.y - seg[1], self.x - seg[0])
                        self.target_angle = avoid_angle + random.uniform(-0.5, 0.5)
                        danger = True
                        break
                if danger: break

            if not danger:
                closest_orb = None
                min_dist = 450
                for orb in orbs:
                    dist = math.hypot(self.x - orb.x, self.y - orb.y)
                    if dist < min_dist:
                        min_dist = dist
                        closest_orb = orb
                
                if closest_orb:
                    self.target_angle = math.atan2(closest_orb.y - self.y, closest_orb.x - self.x)
                elif self.ai_timer > random.randint(30, 70):
                    self.ai_timer = 0
                    self.target_angle += random.uniform(-1.5, 1.5)
            
            margin = 200
            if self.x < margin: self.target_angle = 0
            elif self.x > WORLD_WIDTH - margin: self.target_angle = math.pi
            elif self.y < margin: self.target_angle = math.pi / 2
            elif self.y > WORLD_HEIGHT - margin: self.target_angle = -math.pi / 2
        else:
            mx, my = pygame.mouse.get_pos()
            dx = mx - (WIDTH // 2)
            dy = my - (HEIGHT // 2)
            if dx != 0 or dy != 0:
                self.target_angle = math.atan2(dy, dx)

        sens_val = settings["sensitivity"]
        sens_multiplier = 0.3 + 3.2 * ((sens_val / 100.0) ** 1.8)
        effective_turn_speed = self.turn_speed * sens_multiplier

        angle_diff = (self.target_angle - self.angle + math.pi) % (2 * math.pi) - math.pi
        turn_step = effective_turn_speed * (dt * 60.0)
        self.angle += max(-turn_step, min(turn_step, angle_diff))

        move_dist = self.speed * (dt * 60.0)
        self.x += math.cos(self.angle) * move_dist
        self.y += math.sin(self.angle) * move_dist

        if self.x < 0 or self.x > WORLD_WIDTH or self.y < 0 or self.y > WORLD_HEIGHT:
            self.alive = False
            return

        self.segments[0] = (self.x, self.y)
        spacing = 6.5
        for i in range(1, len(self.segments)):
            prev = self.segments[i-1]
            curr = self.segments[i]
            dx = curr[0] - prev[0]
            dy = curr[1] - prev[1]
            dist = math.hypot(dx, dy)
            if dist > spacing:
                angle_seg = math.atan2(dy, dx)
                self.segments[i] = (prev[0] + math.cos(angle_seg) * spacing, prev[1] + math.sin(angle_seg) * spacing)

        target_length = 22 + int(self.score / 3)
        while len(self.segments) < target_length:
            self.segments.append(self.segments[-1])
        while len(self.segments) > target_length:
            self.segments.pop()

    def draw(self, surf, cam_x, cam_y, graphics):
        if not self.alive:
            return

        for i in range(len(self.segments) - 1, -1, -1):
            sx, sy = self.segments[i][0] - cam_x, self.segments[i][1] - cam_y
            if -60 < sx < WIDTH + 60 and -60 < sy < HEIGHT + 60:
                r = int(self.radius * (1 - i * 0.0015))
                r = max(r, 6)
                
                seg_color = self.color
                if self.pattern == "Striped" and i % 3 == 0:
                    seg_color = WHITE
                elif self.pattern == "Glow Rings" and i % 4 == 0:
                    seg_color = (min(255, self.color[0] + 70), min(255, self.color[1] + 70), min(255, self.color[2] + 70))
                elif self.pattern == "Polka Dots" and i % 2 == 0:
                    seg_color = YELLOW
                elif self.pattern == "Neon Spine" and i % 5 == 0:
                    seg_color = RED
                
                if graphics == "Ultra":
                    glow_s = pygame.Surface((r * 3, r * 3), pygame.SRCALPHA)
                    pygame.draw.circle(glow_s, (*seg_color, 70), (r * 1.5, r * 1.5), r * 1.3)
                    surf.blit(glow_s, (int(sx - r * 1.5), int(sy - r * 1.5)))

                pygame.draw.circle(surf, seg_color, (int(sx), int(sy)), r)
                pygame.draw.circle(surf, BLACK, (int(sx), int(sy)), r, 2)

                if graphics == "Ultra":
                    pygame.draw.circle(surf, (255, 255, 255, 180), (int(sx - r * 0.3), int(sy - r * 0.3)), max(2, r // 3))

        hx, hy = self.segments[0][0] - cam_x, self.segments[0][1] - cam_y
        self.draw_face(surf, hx, hy)

    def draw_face(self, surf, hx, hy):
        style = self.face
        angle = self.angle

        if style == "Cyclops":
            ex = hx + math.cos(angle) * 7
            ey = hy + math.sin(angle) * 7
            pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 6)
            pygame.draw.circle(surf, BLACK, (int(ex), int(ey)), 3)

        elif style == "Shades":
            ox = math.cos(angle + math.pi/2) * 6
            oy = math.sin(angle + math.pi/2) * 6
            fx = hx + math.cos(angle) * 6
            fy = hy + math.sin(angle) * 6
            pygame.draw.line(surf, BLACK, (int(fx + ox * 1.3), int(fy + oy * 1.3)), (int(fx - ox * 1.3), int(fy - oy * 1.3)), 7)
            pygame.draw.circle(surf, WHITE, (int(fx + ox * 0.7), int(fy + oy * 0.7)), 2)
            pygame.draw.circle(surf, WHITE, (int(fx - ox * 0.7), int(fy - oy * 0.7)), 2)

        elif style == "Angry":
            for side in [0.6, -0.6]:
                ex = hx + math.cos(angle + side) * 7
                ey = hy + math.sin(angle + side) * 7
                pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 5)
                pygame.draw.circle(surf, RED, (int(ex), int(ey)), 2)
                eb_start_x = ex - math.cos(angle + side + 0.5) * 5
                eb_start_y = ey - math.sin(angle + side + 0.5) * 5
                eb_end_x = ex + math.cos(angle + side + 0.5) * 5
                eb_end_y = ey + math.sin(angle + side + 0.5) * 5
                pygame.draw.line(surf, BLACK, (int(eb_start_x), int(eb_start_y)), (int(eb_end_x), int(eb_end_y)), 3)

        elif style == "Cute":
            for side in [0.6, -0.6]:
                ex = hx + math.cos(angle + side) * 7
                ey = hy + math.sin(angle + side) * 7
                pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 6)
                pygame.draw.circle(surf, BLACK, (int(ex), int(ey)), 4)
                pygame.draw.circle(surf, WHITE, (int(ex - 1.5), int(ey - 2)), 2)
                pygame.draw.circle(surf, WHITE, (int(ex + 1), int(ey + 1)), 1)

        elif style == "Winking":
            ex1 = hx + math.cos(angle + 0.6) * 6
            ey1 = hy + math.sin(angle + 0.6) * 6
            pygame.draw.circle(surf, WHITE, (int(ex1), int(ey1)), 4)
            pygame.draw.circle(surf, BLACK, (int(ex1), int(ey1)), 2)

            ex2 = hx + math.cos(angle - 0.6) * 6
            ey2 = hy + math.sin(angle - 0.6) * 6
            wx1 = ex2 - math.cos(angle) * 3
            wy1 = ey2 - math.sin(angle) * 3
            wx2 = ex2 + math.cos(angle) * 3
            wy2 = ey2 + math.sin(angle) * 3
            pygame.draw.line(surf, BLACK, (int(wx1), int(wy1)), (int(wx2), int(wy2)), 2)

        elif style == "Laser Eyes":
            for side in [0.6, -0.6]:
                ex = hx + math.cos(angle + side) * 6
                ey = hy + math.sin(angle + side) * 6
                pygame.draw.circle(surf, RED, (int(ex), int(ey)), 4)
                lx = ex + math.cos(angle) * 25
                ly = ey + math.sin(angle) * 25
                pygame.draw.line(surf, RED, (int(ex), int(ey)), (int(lx), int(ly)), 4)

        else:
            for side in [0.6, -0.6]:
                ex = hx + math.cos(angle + side) * 6
                ey = hy + math.sin(angle + side) * 6
                pygame.draw.circle(surf, WHITE, (int(ex), int(ey)), 4)
                pygame.draw.circle(surf, BLACK, (int(ex), int(ey)), 2)

class Game:
    def __init__(self):
        self.state = "MENU"
        self.return_state = "MENU"
        self.clock = pygame.time.Clock()
        self.player = None
        self.bots = []
        self.orbs = []
        self.final_score = 0
        self.menu_orbs = [Orb(random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)) for _ in range(45)]
        self.dragging_sens = False
        self.dragging_sfx = False
        
        self.menu_flow_snake = Snake(1400, 540, is_bot=True, color=(52, 152, 219), face="Cute", pattern="Glow Rings")
        self.menu_flow_snake.speed = 3.0

    def reset_game(self):
        p_color = COLOR_PALETTE[player_style["color_idx"]][1]
        p_face = FACE_STYLES[player_style["face_idx"]]
        p_pattern = PATTERN_STYLES[player_style["pattern_idx"]]

        self.player = Snake(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, name="Player", is_bot=False, color=p_color, face=p_face, pattern=p_pattern)
        
        self.bots = []
        for i in range(14):
            bx = random.randint(300, WORLD_WIDTH - 300)
            by = random.randint(300, WORLD_HEIGHT - 300)
            bcolor = random.choice([c[1] for c in COLOR_PALETTE])
            bface = random.choice(FACE_STYLES)
            bpat = random.choice(PATTERN_STYLES)
            self.bots.append(Snake(bx, by, name=f"Bot_{i+1}", is_bot=True, color=bcolor, face=bface, pattern=bpat))
        
        self.orbs = []
        for _ in range(400):
            ox = random.randint(30, WORLD_WIDTH - 30)
            oy = random.randint(30, WORLD_HEIGHT - 30)
            self.orbs.append(Orb(ox, oy))

    def run(self):
        running = True
        while running:
            fps_target = settings["refresh_rate"]
            
            if fps_target > 0:
                dt = self.clock.tick(fps_target) / 1000.0
            else:
                dt = self.clock.tick(1000) / 1000.0

            if dt > 0.1: 
                dt = 0.1

            if self.state == "PLAYING":
                pygame.event.set_grab(True)
            else:
                pygame.event.set_grab(False)

            if self.state == "MENU":
                running = self.handle_menu(dt)
            elif self.state == "CUSTOMIZE":
                running = self.handle_customize()
            elif self.state == "SETTINGS":
                running = self.handle_settings()
            elif self.state == "HELP":
                running = self.handle_help()
            elif self.state == "PAUSE":
                running = self.handle_pause()
            elif self.state == "PLAYING":
                running = self.handle_playing(dt)
            elif self.state == "GAME_OVER":
                running = self.handle_game_over()

        pygame.quit()
        sys.exit()

    def draw_button(self, text, rect, hovered, primary=True):
        col_main = (41, 128, 185) if primary else (75, 85, 100)
        col_hover = (52, 152, 219) if primary else (95, 105, 120)
        color = col_hover if hovered else col_main
        
        draw_rect = rect.inflate(6, 6) if hovered else rect
        
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 5
        pygame.draw.rect(screen, (8, 10, 16), shadow_rect, border_radius=14)

        pygame.draw.rect(screen, color, draw_rect, border_radius=14)
        pygame.draw.rect(screen, (255, 255, 255, 140), draw_rect, 2, border_radius=14)
        
        txt_surf = FONT_MENU.render(text, True, WHITE)
        screen.blit(txt_surf, txt_surf.get_rect(center=draw_rect.center))

    def draw_world(self, cam_x, cam_y):
        blur_alpha_map = {"Off": 0, "Low": 220, "Medium": 140, "High": 80}
        blur_alpha = blur_alpha_map.get(settings["motion_blur"], 0)

        if blur_alpha > 0:
            blur_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            blur_surf.fill((*BG_COLOR, blur_alpha))
            screen.blit(blur_surf, (0, 0))
        else:
            screen.fill(BG_COLOR)
        
        if settings["graphics"] != "Low":
            grid_size = 100
            start_x = int(cam_x // grid_size) * grid_size - cam_x
            start_y = int(cam_y // grid_size) * grid_size - cam_y
            for x in range(int(start_x), WIDTH, grid_size):
                line_col = (28, 36, 54) if settings["graphics"] == "Ultra" else GRID_COLOR
                pygame.draw.line(screen, line_col, (x, 0), (x, HEIGHT), 1 if settings["graphics"] != "Ultra" else 2)
            for y in range(int(start_y), HEIGHT, grid_size):
                line_col = (28, 36, 54) if settings["graphics"] == "Ultra" else GRID_COLOR
                pygame.draw.line(screen, line_col, (0, y), (WIDTH, y), 1 if settings["graphics"] != "Ultra" else 2)

        bx1, by1 = 0 - cam_x, 0 - cam_y
        border_rect = pygame.Rect(bx1, by1, WORLD_WIDTH, WORLD_HEIGHT)
        pygame.draw.rect(screen, BORDER_COLOR, border_rect, 8 if settings["graphics"] == "Ultra" else 6)

    def handle_menu(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 220 <= mx <= 520 and 410 <= my <= 475:
                    play_sfx(SOUND_CLICK)
                    self.reset_game()
                    self.state = "PLAYING"
                elif 220 <= mx <= 520 and 495 <= my <= 560:
                    play_sfx(SOUND_CLICK)
                    self.return_state = "MENU"
                    self.state = "CUSTOMIZE"
                elif 220 <= mx <= 520 and 580 <= my <= 645:
                    play_sfx(SOUND_CLICK)
                    self.return_state = "MENU"
                    self.state = "SETTINGS"
                elif 220 <= mx <= 520 and 665 <= my <= 730:
                    play_sfx(SOUND_CLICK)
                    self.state = "HELP"
                elif 220 <= mx <= 520 and 750 <= my <= 815:
                    play_sfx(SOUND_CLICK)
                    return False

        screen.fill(BG_COLOR)

        for orb in self.menu_orbs:
            orb.draw(screen, 0, 0, "Ultra")

        t = pygame.time.get_ticks() * 0.002
        self.menu_flow_snake.target_angle = math.sin(t) * 1.5 + math.cos(t * 0.5) * 0.8
        self.menu_flow_snake.update(dt, [], [])
        if self.menu_flow_snake.x < 800 or self.menu_flow_snake.x > 2400 or self.menu_flow_snake.y < 200 or self.menu_flow_snake.y > 1200:
            self.menu_flow_snake.x = 1400
            self.menu_flow_snake.y = 540
            self.menu_flow_snake.segments = [(1400 - i * 10, 540) for i in range(25)]
        self.menu_flow_snake.draw(screen, 0, 0, "Ultra")

        float_offset = math.sin(pygame.time.get_ticks() * 0.003) * 8
        title_surf = FONT_TITLE.render("Pysnake.io", True, COLOR_PALETTE[player_style["color_idx"]][1])
        screen.blit(title_surf, (220, int(185 + float_offset)))
        
        sub_surf = FONT_SUBTITLE.render("Evolve. Consume. Dominate.", True, WHITE)
        screen.blit(sub_surf, (220, int(280 + float_offset)))

        mx, my = pygame.mouse.get_pos()
        buttons = [
            ("Play", 410),
            ("Customize Snake", 495),
            ("Settings", 580),
            ("How to Play", 665),
            ("Exit", 750)
        ]
        for text, y in buttons:
            rect = pygame.Rect(220, y, 300, 65)
            self.draw_button(text, rect, rect.collidepoint(mx, my))

        pygame.display.flip()
        return True

    def handle_pause(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "PLAYING"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 810 <= mx <= 1110 and 420 <= my <= 485:
                    play_sfx(SOUND_CLICK)
                    self.state = "PLAYING"
                elif 810 <= mx <= 1110 and 505 <= my <= 570:
                    play_sfx(SOUND_CLICK)
                    self.return_state = "PAUSE"
                    self.state = "CUSTOMIZE"
                elif 810 <= mx <= 1110 and 590 <= my <= 655:
                    play_sfx(SOUND_CLICK)
                    self.return_state = "PAUSE"
                    self.state = "SETTINGS"
                elif 810 <= mx <= 1110 and 675 <= my <= 740:
                    play_sfx(SOUND_CLICK)
                    self.state = "MENU"

        # Draw current game view underneath dimmed
        if self.player and self.player.alive:
            cam_x = self.player.x - WIDTH // 2
            cam_y = self.player.y - HEIGHT // 2
            self.draw_world(cam_x, cam_y)
            for orb in self.orbs:
                orb.draw(screen, cam_x, cam_y, settings["graphics"])
            for bot in self.bots:
                bot.draw(screen, cam_x, cam_y, settings["graphics"])
            self.player.draw(screen, cam_x, cam_y, settings["graphics"])
        else:
            screen.fill(BG_COLOR)

        # Semi-transparent pause overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 15, 24, 180))
        screen.blit(overlay, (0, 0))

        title_surf = FONT_TITLE.render("Game Paused", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 280)))

        mx, my = pygame.mouse.get_pos()
        buttons = [
            ("Resume", 420),
            ("Customize Snake", 505),
            ("Settings", 590),
            ("Main Menu", 675)
        ]
        for text, y in buttons:
            rect = pygame.Rect(810, y, 300, 65)
            self.draw_button(text, rect, rect.collidepoint(mx, my))

        pygame.display.flip()
        return True

    def handle_help(self):
        back_rect = pygame.Rect(WIDTH // 2 - 125, 780, 250, 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if back_rect.collidepoint(mx, my):
                    play_sfx(SOUND_CLICK)
                    self.state = "MENU"

        screen.fill(BG_COLOR)

        title_surf = FONT_TITLE.render("How to Play", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 170)))

        card_rect = pygame.Rect(WIDTH // 2 - 475, 260, 950, 480)
        pygame.draw.rect(screen, (18, 22, 34), card_rect, border_radius=20)
        pygame.draw.rect(screen, (52, 152, 219), card_rect, 3, border_radius=20)

        instructions = [
            ("STEERING", "Move your mouse across the screen to guide your snake."),
            ("CONSUME", "Eat small (1pt), medium (3pts), and large (7pts) orbs to grow longer."),
            ("COMBAT", "Crash your snake's head into another snake's body to eliminate them."),
            ("SCORING", "Eliminated snakes drop glowing score orbs across the world."),
            ("DANGER", "Avoid hitting the outer red boundary walls or other snakes!")
        ]

        for idx, (heading, desc) in enumerate(instructions):
            y_pos = card_rect.y + 55 + idx * 78
            head_surf = FONT_HELP.render(f"• {heading}:", True, (52, 152, 219))
            desc_surf = FONT_HELP.render(desc, True, WHITE)
            screen.blit(head_surf, (card_rect.x + 50, y_pos))
            screen.blit(desc_surf, (card_rect.x + 230, y_pos))

        mx, my = pygame.mouse.get_pos()
        self.draw_button("Back", back_rect, back_rect.collidepoint(mx, my), primary=False)

        pygame.display.flip()
        return True

    def handle_customize(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 1050 <= mx <= 1350 and 385 <= my <= 445:
                    play_sfx(SOUND_CLICK)
                    player_style["color_idx"] = (player_style["color_idx"] + 1) % len(COLOR_PALETTE)
                elif 1050 <= mx <= 1350 and 475 <= my <= 535:
                    play_sfx(SOUND_CLICK)
                    player_style["face_idx"] = (player_style["face_idx"] + 1) % len(FACE_STYLES)
                elif 1050 <= mx <= 1350 and 565 <= my <= 625:
                    play_sfx(SOUND_CLICK)
                    player_style["pattern_idx"] = (player_style["pattern_idx"] + 1) % len(PATTERN_STYLES)
                elif 860 <= mx <= 1060 and 740 <= my <= 800:
                    play_sfx(SOUND_CLICK)
                    # Update active player snake appearance immediately if in-game
                    if self.player:
                        self.player.color = COLOR_PALETTE[player_style["color_idx"]][1]
                        self.player.face = FACE_STYLES[player_style["face_idx"]]
                        self.player.pattern = PATTERN_STYLES[player_style["pattern_idx"]]
                    self.state = self.return_state

        screen.fill(BG_COLOR)
        
        title_surf = FONT_TITLE.render("Customize Snake", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 90)))

        preview_rect = pygame.Rect(WIDTH // 2 - 210, 160, 420, 165)
        pygame.draw.rect(screen, (16, 20, 32), preview_rect, border_radius=18)
        pygame.draw.rect(screen, (52, 152, 219), preview_rect, 3, border_radius=18)

        p_color = COLOR_PALETTE[player_style["color_idx"]][1]
        p_face = FACE_STYLES[player_style["face_idx"]]
        p_pattern = PATTERN_STYLES[player_style["pattern_idx"]]
        
        preview_snake = Snake(WIDTH // 2, 242, color=p_color, face=p_face, pattern=p_pattern)
        preview_snake.angle = math.sin(pygame.time.get_ticks() * 0.003) * 0.6
        preview_snake.segments[0] = (WIDTH // 2, 242)
        for i in range(1, len(preview_snake.segments)):
            preview_snake.segments[i] = (WIDTH // 2 - i * 14, 242)
        preview_snake.draw(screen, 0, 0, "Ultra")

        options = [
            ("Snake Color:", COLOR_PALETTE[player_style["color_idx"]][0], 385),
            ("Face Style:", FACE_STYLES[player_style["face_idx"]], 475),
            ("Body Pattern:", PATTERN_STYLES[player_style["pattern_idx"]], 565)
        ]

        mx, my = pygame.mouse.get_pos()
        for label, val, y in options:
            lbl_surf = FONT_MENU.render(label, True, WHITE)
            screen.blit(lbl_surf, (570, y + 14))

            btn_rect = pygame.Rect(1050, y, 300, 60)
            self.draw_button(val, btn_rect, btn_rect.collidepoint(mx, my))

        back_rect = pygame.Rect(860, 740, 200, 60)
        self.draw_button("Back", back_rect, back_rect.collidepoint(mx, my), primary=False)

        pygame.display.flip()
        return True

    def handle_settings(self):
        sens_slider_rect = pygame.Rect(1050, 595, 300, 10)
        sfx_slider_rect = pygame.Rect(1050, 695, 300, 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 1050 <= mx <= 1350 and 235 <= my <= 295:
                    play_sfx(SOUND_CLICK)
                    if settings["graphics"] == "Low": settings["graphics"] = "Medium"
                    elif settings["graphics"] == "Medium": settings["graphics"] = "High"
                    elif settings["graphics"] == "High": settings["graphics"] = "Ultra"
                    else: settings["graphics"] = "Low"
                elif 1050 <= mx <= 1350 and 320 <= my <= 380:
                    play_sfx(SOUND_CLICK)
                    if settings["refresh_rate"] == 60: settings["refresh_rate"] = 120
                    elif settings["refresh_rate"] == 120: settings["refresh_rate"] = 240
                    elif settings["refresh_rate"] == 240: settings["refresh_rate"] = 0
                    else: settings["refresh_rate"] = 60
                elif 1050 <= mx <= 1350 and 405 <= my <= 465:
                    play_sfx(SOUND_CLICK)
                    settings["fps_counter"] = not settings["fps_counter"]
                elif 1050 <= mx <= 1350 and 490 <= my <= 550:
                    play_sfx(SOUND_CLICK)
                    blur_levels = ["Off", "Low", "Medium", "High"]
                    curr_idx = blur_levels.index(settings["motion_blur"])
                    settings["motion_blur"] = blur_levels[(curr_idx + 1) % len(blur_levels)]
                elif sens_slider_rect.collidepoint(mx, my) or pygame.Rect(1040, 580, 320, 40).collidepoint(mx, my):
                    self.dragging_sens = True
                    settings["sensitivity"] = int(max(0, min(100, (mx - 1050) / 300 * 100)))
                elif sfx_slider_rect.collidepoint(mx, my) or pygame.Rect(1040, 680, 320, 40).collidepoint(mx, my):
                    self.dragging_sfx = True
                    settings["sfx_volume"] = int(max(0, min(100, (mx - 1050) / 300 * 100)))
                elif 860 <= mx <= 1060 and 785 <= my <= 845:
                    play_sfx(SOUND_CLICK)
                    self.state = self.return_state
            elif event.type == pygame.MOUSEBUTTONUP:
                self.dragging_sens = False
                self.dragging_sfx = False

        mx, my = pygame.mouse.get_pos()
        if self.dragging_sens:
            settings["sensitivity"] = int(max(0, min(100, (mx - 1050) / 300 * 100)))
        if self.dragging_sfx:
            settings["sfx_volume"] = int(max(0, min(100, (mx - 1050) / 300 * 100)))

        screen.fill(BG_COLOR)
        
        title_surf = FONT_TITLE.render("Settings", True, WHITE)
        screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, 130)))

        options = [
            ("Graphics Level:", settings["graphics"], 235),
            ("Refresh Rate:", f"{settings['refresh_rate']}Hz" if settings['refresh_rate'] > 0 else "Unlimited", 320),
            ("FPS Counter:", "ON" if settings["fps_counter"] else "OFF", 405),
            ("Motion Blur:", settings["motion_blur"], 490)
        ]

        for label, val, y in options:
            lbl_surf = FONT_MENU.render(label, True, WHITE)
            screen.blit(lbl_surf, (570, y + 14))

            btn_rect = pygame.Rect(1050, y, 300, 60)
            self.draw_button(val, btn_rect, btn_rect.collidepoint(mx, my))

        sens_lbl = FONT_MENU.render(f"Sensitivity: {settings['sensitivity']}", True, WHITE)
        screen.blit(sens_lbl, (570, 575))
        pygame.draw.rect(screen, (90, 100, 120), sens_slider_rect, border_radius=5)
        sens_fill = int(300 * (settings["sensitivity"] / 100.0))
        pygame.draw.rect(screen, (52, 152, 219), (1050, 595, sens_fill, 10), border_radius=5)
        sens_thumb = 1050 + sens_fill
        pygame.draw.circle(screen, WHITE, (sens_thumb, 600), 12)
        pygame.draw.circle(screen, BLACK, (sens_thumb, 600), 12, 2)

        sfx_lbl = FONT_MENU.render(f"SFX Volume: {settings['sfx_volume']}%", True, WHITE)
        screen.blit(sfx_lbl, (570, 675))
        pygame.draw.rect(screen, (90, 100, 120), sfx_slider_rect, border_radius=5)
        sfx_fill = int(300 * (settings["sfx_volume"] / 100.0))
        pygame.draw.rect(screen, (46, 204, 113), (1050, 695, sfx_fill, 10), border_radius=5)
        sfx_thumb = 1050 + sfx_fill
        pygame.draw.circle(screen, WHITE, (sfx_thumb, 700), 12)
        pygame.draw.circle(screen, BLACK, (sfx_thumb, 700), 12, 2)

        back_rect = pygame.Rect(860, 785, 200, 60)
        self.draw_button("Back", back_rect, back_rect.collidepoint(mx, my), primary=False)

        pygame.display.flip()
        return True

    def handle_playing(self, dt):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.state = "PAUSE"

        if not self.player.alive:
            for pseg in self.player.segments[::2]:
                self.orbs.append(Orb(pseg[0], pseg[1], self.player.color))
            self.final_score = self.player.score
            self.state = "GAME_OVER"
            return True

        self.player.update(dt, self.bots, self.orbs)

        for bot in self.bots:
            bot.update(dt, self.bots, self.orbs)
            if not bot.alive:
                for pseg in bot.segments[::2]:
                    self.orbs.append(Orb(pseg[0], pseg[1], bot.color))
                bx = random.randint(300, WORLD_WIDTH - 300)
                by = random.randint(300, WORLD_HEIGHT - 300)
                bcolor = random.choice([c[1] for c in COLOR_PALETTE])
                self.bots.remove(bot)
                self.bots.append(Snake(bx, by, name=bot.name, is_bot=True, color=bcolor, face=bot.face, pattern=bot.pattern))

        for orb in self.orbs[:]:
            if math.hypot(self.player.x - orb.x, self.player.y - orb.y) < self.player.radius + orb.radius:
                self.orbs.remove(orb)
                self.player.score += orb.value
                play_sfx(SOUND_POP)
                self.orbs.append(Orb(random.randint(30, WORLD_WIDTH - 30), random.randint(30, WORLD_HEIGHT - 30)))

        for bot in self.bots:
            for orb in self.orbs[:]:
                if math.hypot(bot.x - orb.x, bot.y - orb.y) < bot.radius + orb.radius:
                    self.orbs.remove(orb)
                    bot.score += orb.value
                    self.orbs.append(Orb(random.randint(30, WORLD_WIDTH - 30), random.randint(30, WORLD_HEIGHT - 30)))

        all_snakes = [self.player] + self.bots
        for snake in all_snakes:
            if not snake.alive: continue
            hx, hy = snake.segments[0]
            for other in all_snakes:
                if snake == other: continue
                for seg in other.segments[1:]:
                    if math.hypot(hx - seg[0], hy - seg[1]) < snake.radius + 4:
                        snake.alive = False
                        if snake == self.player:
                            play_sfx(SOUND_CRASH)
                        else:
                            play_sfx(SOUND_BOOM)
                        break
                if not snake.alive: break

        cam_x = self.player.x - WIDTH // 2
        cam_y = self.player.y - HEIGHT // 2

        self.draw_world(cam_x, cam_y)

        for orb in self.orbs:
            orb.draw(screen, cam_x, cam_y, settings["graphics"])

        for bot in self.bots:
            bot.draw(screen, cam_x, cam_y, settings["graphics"])
        self.player.draw(screen, cam_x, cam_y, settings["graphics"])

        score_surf = FONT_HUD.render(f"Score: {self.player.score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 35))
        pygame.draw.rect(screen, (25, 30, 45), score_rect.inflate(30, 16), border_radius=10)
        pygame.draw.rect(screen, WHITE, score_rect.inflate(30, 16), 2, border_radius=10)
        screen.blit(score_surf, score_rect)

        if settings["fps_counter"]:
            fps_val = int(self.clock.get_fps())
            fps_surf = FONT_HUD.render(f"FPS: {fps_val}", True, (241, 196, 15))
            screen.blit(fps_surf, (WIDTH - 160, 25))

        pygame.display.flip()
        return True

    def handle_game_over(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 810 <= mx <= 1110 and 520 <= my <= 580:
                    play_sfx(SOUND_CLICK)
                    self.reset_game()
                    self.state = "PLAYING"
                elif 810 <= mx <= 1110 and 600 <= my <= 660:
                    play_sfx(SOUND_CLICK)
                    self.state = "MENU"

        screen.fill(BG_COLOR)

        over_surf = FONT_TITLE.render("Game Over", True, BORDER_COLOR)
        screen.blit(over_surf, over_surf.get_rect(center=(WIDTH // 2, 280)))

        score_surf = FONT_SUBTITLE.render(f"Final Score: {self.final_score}", True, WHITE)
        screen.blit(score_surf, score_surf.get_rect(center=(WIDTH // 2, 390)))

        mx, my = pygame.mouse.get_pos()
        buttons = [("Play Again", 520), ("Main Menu", 600)]
        for text, y in buttons:
            rect = pygame.Rect(810, y, 300, 55)
            self.draw_button(text, rect, rect.collidepoint(mx, my))

        pygame.display.flip()
        return True

if __name__ == "__main__":
    game = Game()
    game.run()
