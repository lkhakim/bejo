import os
import math
import random
import threading
import queue
import time

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame

pygame.init()

SCREEN_W, SCREEN_H = 420, 540
MIN_W, MIN_H = 320, 420
BG_COLOR = (248, 248, 252)

NOTO_FONT = None
for name in ["segoeui", "arial", "notosans", "dejavusans"]:
    try:
        NOTO_FONT = pygame.font.SysFont(name, 16, bold=False)
        break
    except:
        pass
if NOTO_FONT is None:
    NOTO_FONT = pygame.font.Font(None, 22)

_EMOJI_MAP_RAW = {
    # smileys
    0x1f600: "happy", 0x1f601: "happy", 0x1f602: "happy",
    0x1f603: "happy", 0x1f604: "happy", 0x1f605: "happy",
    0x1f606: "happy", 0x1f607: "happy", 0x1f608: "angry",
    0x1f609: "happy", 0x1f60a: "happy", 0x1f60b: "happy",
    0x1f60c: "cool", 0x1f60d: "love", 0x1f60e: "cool",
    0x1f60f: "cool", 0x1f610: "neutral", 0x1f611: "neutral",
    0x1f612: "thinking", 0x1f613: "thinking", 0x1f614: "thinking",
    0x1f615: "thinking", 0x1f616: "thinking", 0x1f617: "love",
    0x1f618: "love", 0x1f619: "love", 0x1f61a: "love",
    0x1f61b: "happy", 0x1f61c: "happy", 0x1f61d: "happy",
    0x1f61e: "sad", 0x1f61f: "sad", 0x1f620: "angry",
    0x1f621: "angry", 0x1f622: "sad", 0x1f623: "thinking",
    0x1f624: "angry", 0x1f625: "sad", 0x1f626: "surprised",
    0x1f627: "surprised", 0x1f628: "surprised", 0x1f629: "surprised",
    0x1f62a: "sad", 0x1f62b: "sad", 0x1f62c: "surprised",
    0x1f62d: "sad", 0x1f62e: "surprised", 0x1f62f: "surprised",
    0x1f630: "surprised", 0x1f631: "surprised", 0x1f632: "surprised",
    0x1f633: "thinking", 0x1f634: "neutral", 0x1f635: "thinking",
    0x1f636: "neutral", 0x1f637: "cool", 0x1f642: "happy",
    0x1f643: "happy", 0x1f644: "thinking",
    # supplemental
    0x1f910: "thinking", 0x1f911: "happy", 0x1f912: "thinking",
    0x1f913: "thinking", 0x1f914: "thinking", 0x1f915: "thinking",
    0x1f916: "thinking", 0x1f917: "love", 0x1f918: "cool",
    0x1f919: "happy", 0x1f91a: "happy", 0x1f91b: "happy",
    0x1f91c: "happy", 0x1f91d: "happy", 0x1f91e: "cool",
    0x1f91f: "cool", 0x1f920: "cool", 0x1f921: "happy",
    0x1f922: "thinking", 0x1f923: "happy", 0x1f924: "thinking",
    0x1f925: "thinking", 0x1f926: "thinking", 0x1f927: "happy",
    0x1f928: "thinking", 0x1f929: "love", 0x1f92a: "cool",
    0x1f92b: "thinking", 0x1f92c: "angry", 0x1f92d: "surprised",
    0x1f92e: "surprised", 0x1f92f: "thinking",
    # hearts
    0x2764: "love", 0x1f49b: "love", 0x1f49c: "love",
    0x1f49d: "love", 0x1f49e: "love", 0x1f49f: "love",
    0x1f5a4: "love", 0x1f90d: "love", 0x1f90e: "love",
    0x1f90f: "cool",
    # gestures
    0x1f44d: "happy", 0x1f44e: "sad", 0x1f44f: "celebrate",
    0x1f4af: "cool", 0x1f4aa: "cool",
    # celebration
    0x1f389: "celebrate", 0x1f38a: "celebrate", 0x1f388: "celebrate",
}

def emoji_to_expression(text):
    for ch in text:
        cp = ord(ch)
        if cp in _EMOJI_MAP_RAW:
            return _EMOJI_MAP_RAW[cp]
    return None

EXPRESSION_CONFIG = {
    "neutral": {
        "color": (78, 197, 237),
        "anim": "bob",
        "eye": "normal",
        "mouth": "smile",
        "arm": "rest",
        "blush": True,
        "particles": [],
        "speed": 1.0,
    },
    "happy": {
        "color": (78, 230, 180),
        "anim": "bounce",
        "eye": "squint",
        "mouth": "big_smile",
        "arm": "wave",
        "blush": True,
        "particles": ["sparkle"],
        "speed": 1.5,
    },
    "thinking": {
        "color": (255, 204, 77),
        "anim": "slow_bob",
        "eye": "looking_up",
        "mouth": "pursed",
        "arm": "chin",
        "blush": False,
        "particles": ["question"],
        "speed": 0.6,
    },
    "processing": {
        "color": (102, 204, 102),
        "anim": "vibrate",
        "eye": "normal",
        "mouth": "neutral",
        "arm": "rest",
        "blush": False,
        "particles": ["dot"],
        "speed": 2.0,
    },
    "celebrate": {
        "color": (255, 215, 0),
        "anim": "bounce",
        "eye": "wide",
        "mouth": "open_smile",
        "arm": "both_up",
        "blush": True,
        "particles": ["confetti"],
        "speed": 2.0,
    },
    "angry": {
        "color": (240, 100, 100),
        "anim": "shake",
        "eye": "angry",
        "mouth": "frown",
        "arm": "rest",
        "blush": False,
        "particles": ["anger"],
        "speed": 2.5,
    },
    "sad": {
        "color": (150, 180, 210),
        "anim": "droop",
        "eye": "sad",
        "mouth": "frown",
        "arm": "rest",
        "blush": False,
        "particles": ["tear"],
        "speed": 0.5,
    },
    "surprised": {
        "color": (255, 230, 100),
        "anim": "jump",
        "eye": "wide",
        "mouth": "open",
        "arm": "both_up",
        "blush": False,
        "particles": ["exclaim"],
        "speed": 1.8,
    },
    "love": {
        "color": (255, 150, 180),
        "anim": "sway",
        "eye": "squint",
        "mouth": "big_smile",
        "arm": "hug",
        "blush": True,
        "particles": ["heart"],
        "speed": 1.2,
    },
    "cool": {
        "color": (100, 200, 255),
        "anim": "bob",
        "eye": "half_closed",
        "mouth": "smirk",
        "arm": "rest",
        "blush": False,
        "particles": ["sparkle"],
        "speed": 0.8,
    },
}

PARTICLE_LIFETIME = 2.0


class Particle:
    def __init__(self, ptype, x, y):
        self.ptype = ptype
        self.x = x
        self.y = y
        self.life = PARTICLE_LIFETIME
        self.max_life = PARTICLE_LIFETIME
        self.vx = random.uniform(-30, 30)
        self.vy = random.uniform(-60, -20)
        self.size = random.uniform(4, 10)
        self.angle = random.uniform(0, math.pi * 2)
        self.rot_speed = random.uniform(-3, 3)
        self.color = self._random_color()

    def _random_color(self):
        return (
            random.randint(200, 255),
            random.randint(100, 255),
            random.randint(100, 255),
        )

    def update(self, dt):
        self.life -= dt
        self.vy += 60 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.angle += self.rot_speed * dt

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return max(0, int(255 * (self.life / self.max_life)))

    def draw(self, screen, cx, cy):
        alpha = self.alpha
        if alpha <= 0:
            return
        px, py = int(self.x), int(self.y)
        if self.ptype in ("sparkle", "star"):
            sz = int(self.size)
            pts = []
            for i in range(4):
                a = self.angle + i * math.pi / 2
                pts.append((px + math.cos(a) * sz, py + math.sin(a) * sz))
            s = pygame.Surface((sz * 2 + 2, sz * 2 + 2), pygame.SRCALPHA)
            pygame.draw.polygon(s, (*self.color, alpha), [
                (sz, 0), (sz * 2, sz * 2), (sz, sz), (0, sz * 2)
            ])
            screen.blit(s, (px - sz, py - sz))
        elif self.ptype == "heart":
            s = pygame.Surface((20, 20), pygame.SRCALPHA)
            hx, hy = 10, 8
            pygame.draw.circle(s, (*self.color, alpha), (hx - 4, hy), 5)
            pygame.draw.circle(s, (*self.color, alpha), (hx + 4, hy), 5)
            pygame.draw.polygon(s, (*self.color, alpha), [
                (hx - 8, hy + 1), (hx + 8, hy + 1), (hx, hy + 12)
            ])
            screen.blit(s, (px - 10, py - 10))
        elif self.ptype == "confetti":
            s = pygame.Surface((int(self.size), int(self.size * 0.6)), pygame.SRCALPHA)
            s.fill((*self.color, alpha))
            rotated = pygame.transform.rotate(s, self.angle * 180 / math.pi)
            screen.blit(rotated, (px - rotated.get_width() // 2, py - rotated.get_height() // 2))
        elif self.ptype == "question":
            if NOTO_FONT:
                s = NOTO_FONT.render("?", True, (*self.color, alpha))
                s.set_alpha(alpha)
                screen.blit(s, (px - 8, py - 12))
        elif self.ptype == "exclaim":
            if NOTO_FONT:
                s = NOTO_FONT.render("!", True, (*self.color, alpha))
                s.set_alpha(alpha)
                screen.blit(s, (px - 6, py - 12))
        elif self.ptype == "anger":
            s = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.line(s, (255, 50, 50, alpha), (2, 0), (14, 14), 2)
            pygame.draw.line(s, (255, 50, 50, alpha), (14, 0), (2, 14), 2)
            screen.blit(s, (px - 8, py - 8))
        elif self.ptype == "tear":
            s = pygame.Surface((8, 12), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (100, 160, 255, alpha), (0, 0, 8, 12))
            screen.blit(s, (px - 4, py - 6))
        elif self.ptype == "dot":
            pygame.draw.circle(screen, (*self.color, alpha), (px, py), int(self.size))
        else:
            pygame.draw.circle(screen, (*self.color, alpha), (px, py), int(self.size))


class BejoDisplay:
    def __init__(self):
        self.cmd_queue = queue.Queue()
        self.running = True
        self.win_w, self.win_h = SCREEN_W, SCREEN_H
        self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption("Bejo AI — Tick Character")
        self.clock = pygame.time.Clock()

        self.status = "Siap Melayani, Bos!"
        self.expression = "neutral"
        self.config = EXPRESSION_CONFIG["neutral"]

        self.mood_color = list(self.config["color"])
        self.target_color = list(self.config["color"])

        self.blink_state = "open"
        self.blink_counter = 0.0
        self.anim_t = 0.0
        self.bounce_offset = 0.0
        self.shake_offset = 0.0
        self.head_tilt = 0.0
        self.arm_angle = 0.0
        self.particles = []
        self.particle_spawn_timer = 0.0

    def set_status(self, text: str):
        self.cmd_queue.put(("status", text))

    def set_expression(self, expr: str):
        self.cmd_queue.put(("expression", expr))

    def stop(self):
        self.cmd_queue.put(("stop", None))

    def poll_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.win_w = max(event.w, MIN_W)
                self.win_h = max(event.h, MIN_H)
                self.screen = pygame.display.set_mode((self.win_w, self.win_h), pygame.RESIZABLE)

    def process_commands(self):
        while not self.cmd_queue.empty():
            cmd, val = self.cmd_queue.get_nowait()
            if cmd == "status":
                self.status = val
            elif cmd == "expression":
                self.set_expression_state(val)
            elif cmd == "stop":
                self.running = False

    def set_expression_state(self, expr):
        if expr in EXPRESSION_CONFIG:
            self.expression = expr
            self.config = EXPRESSION_CONFIG[expr]
            self.target_color = list(self.config["color"])
            self.anim_t = 0.0

    def spawn_particles(self, count=1):
        cfg = self.config
        ptypes = cfg.get("particles", [])
        if not ptypes:
            return
        cx, cy = self.win_w // 2, min(self.win_h // 2 + 10, 300)
        for _ in range(count):
            ptype = random.choice(ptypes)
            px = cx + random.randint(-80, 80)
            py = cy - random.randint(40, 100)
            self.particles.append(Particle(ptype, px, py))

    def update_animation(self, dt):
        self.anim_t += dt
        speed = self.config.get("speed", 1.0)
        anim = self.config.get("anim", "bob")

        for i in range(3):
            diff = self.target_color[i] - self.mood_color[i]
            self.mood_color[i] += diff * dt * 4
            self.mood_color[i] = max(0, min(255, self.mood_color[i]))

        if anim == "bob":
            self.bounce_offset = math.sin(self.anim_t * 2.0 * speed) * 4
            self.shake_offset = 0
            self.head_tilt = math.sin(self.anim_t * 0.5) * 0.02
        elif anim == "bounce":
            self.bounce_offset = abs(math.sin(self.anim_t * 4.0 * speed)) * 12
            self.shake_offset = 0
            self.head_tilt = math.sin(self.anim_t * 2.0) * 0.03
        elif anim == "slow_bob":
            self.bounce_offset = math.sin(self.anim_t * 1.2 * speed) * 3
            self.shake_offset = 0
            self.head_tilt = 0.08 + math.sin(self.anim_t * 0.3) * 0.04
        elif anim == "vibrate":
            self.bounce_offset = 0
            self.shake_offset = math.sin(self.anim_t * 30 * speed) * 2
            self.head_tilt = 0
        elif anim == "shake":
            self.bounce_offset = 0
            self.shake_offset = math.sin(self.anim_t * 40 * speed) * 4 + math.cos(self.anim_t * 37 * speed) * 3
            self.head_tilt = 0
        elif anim == "droop":
            self.bounce_offset = -2 + math.sin(self.anim_t * 1.0) * 1
            self.shake_offset = 0
            self.head_tilt = 0.1
        elif anim == "jump":
            self.bounce_offset = abs(math.sin(self.anim_t * 6.0 * speed)) * 8
            self.shake_offset = 0
            self.head_tilt = math.sin(self.anim_t * 3.0) * 0.05
        elif anim == "sway":
            self.bounce_offset = math.sin(self.anim_t * 1.5 * speed) * 3
            self.shake_offset = math.sin(self.anim_t * 1.8 * speed) * 6
            self.head_tilt = math.sin(self.anim_t * 0.8) * 0.02
        else:
            self.bounce_offset = 0
            self.shake_offset = 0
            self.head_tilt = 0

        self.blink_counter += dt
        if self.blink_state == "open" and self.blink_counter > 3.0:
            self.blink_state = "closing"
            self.blink_counter = 0.0
        elif self.blink_state == "closing" and self.blink_counter > 0.05:
            self.blink_state = "closed"
            self.blink_counter = 0.0
        elif self.blink_state == "closed" and self.blink_counter > 0.1:
            self.blink_state = "opening"
            self.blink_counter = 0.0
        elif self.blink_state == "opening" and self.blink_counter > 0.05:
            self.blink_state = "open"
            self.blink_counter = 0.0

        self.particle_spawn_timer += dt
        if self.particle_spawn_timer > 0.15:
            self.particle_spawn_timer = 0.0
            self.spawn_particles(random.randint(1, 2))

        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

    def draw(self):
        self.screen.fill(BG_COLOR)
        cx = self.win_w // 2 + self.shake_offset
        cy = min(self.win_h // 2 + 10 + self.bounce_offset, 320)
        body_color = tuple(int(c) for c in self.mood_color)
        body_dark = tuple(max(0, c - 40) for c in body_color)
        is_right = [self.config.get("anim") in ("shake", "vibrate"), False]
        eye_mode = self.config.get("eye", "normal")
        mouth_mode = self.config.get("mouth", "smile")
        arm_mode = self.config.get("arm", "rest")
        show_blush = self.config.get("blush", False)

        shadow_surf = pygame.Surface((300, 30), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 30), (0, 0, 300, 30))
        self.screen.blit(shadow_surf, (cx - 150, cy + 160))

        def _ear(side, tilt):
            ex = cx + (-120 if side == "left" else 120)
            dy = tilt * 30
            pts = [(ex, cy - 90 + dy), (ex + (-50 if side == "left" else 50), cy - 110 + dy), (ex, cy - 20 + dy)]
            pygame.draw.polygon(self.screen, body_color, pts)
            inner = [(ex, cy - 70 + dy), (ex + (-30 if side == "left" else 30), cy - 90 + dy), (ex, cy - 30 + dy)]
            inner_color = (252, 161, 162)
            pygame.draw.polygon(self.screen, inner_color, inner)

        _ear("left", self.head_tilt)
        _ear("right", self.head_tilt)

        body_r = pygame.Rect(cx - 130, cy - 130, 260, 280)
        pygame.draw.ellipse(self.screen, body_color, body_r)

        feet_y = cy + 150
        for side in ("left", "right"):
            fx = cx + (-60 if side == "left" else 60)
            pygame.draw.ellipse(self.screen, body_dark, (fx - 40, feet_y, 80, 40))
            for tx in (-15, 0, 15):
                pygame.draw.circle(self.screen, (122, 115, 116), (fx + tx, feet_y + 30), 8)

        for side in ("left", "right"):
            ax = cx + (-110 if side == "left" else 110)
            arm_base_y = cy + 40
            waviness = math.sin(self.anim_t * 2.0) * 20 if side == "right" else 0
            if arm_mode == "rest":
                pygame.draw.ellipse(self.screen, (63, 160, 194), (ax - 30, arm_base_y, 60, 120))
            elif arm_mode == "wave":
                if side == "right":
                    pygame.draw.ellipse(self.screen, (63, 160, 194),
                                        (ax - 20, arm_base_y - 30 + waviness, 40, 100))
                else:
                    pygame.draw.ellipse(self.screen, (63, 160, 194), (ax - 30, arm_base_y, 60, 120))
            elif arm_mode == "chin":
                if side == "right":
                    pygame.draw.ellipse(self.screen, (63, 160, 194),
                                        (ax - 10, arm_base_y - 40, 40, 80))
                else:
                    pygame.draw.ellipse(self.screen, (63, 160, 194), (ax - 30, arm_base_y, 60, 120))
            elif arm_mode == "both_up":
                lift = 30 + abs(math.sin(self.anim_t * 4.0)) * 15
                pygame.draw.ellipse(self.screen, (63, 160, 194),
                                    (ax - 20, arm_base_y - lift, 40, 80))
            elif arm_mode == "hug":
                hug_offset = math.sin(self.anim_t * 1.5) * 10
                pygame.draw.ellipse(self.screen, (63, 160, 194),
                                    (ax - 30 + hug_offset, arm_base_y, 60, 100))
            for tx in (-8, 8):
                pygame.draw.circle(self.screen, (122, 115, 116), (fx + tx, cy + 170), 7) if side == "left" else None

            for tx in (-8, 8):
                finger_base = cy + 170
                if arm_mode == "chin":
                    finger_base = cy + 40
                elif arm_mode == "both_up":
                    finger_base = cy + 30
                pygame.draw.circle(self.screen, (122, 115, 116), (ax + tx, finger_base), 7)

        blink_offset = 0
        if self.blink_state == "closing":
            blink_offset = 20 * (1 - self.blink_counter / 0.05)
        elif self.blink_state == "closed":
            blink_offset = 20
        elif self.blink_state == "opening":
            blink_offset = 20 * (1 - self.blink_counter / 0.05)

        for ex in (-80, 80):
            ec = (cx + ex + (3 if ex > 0 else 0), cy - 5)
            eye_r = 55
            iris_r = 40
            pupil_r = 28
            highlight_r = 10

            if eye_mode in ("wide", "surprised"):
                eye_r = 60
                iris_r = 42
                pupil_r = 30
            elif eye_mode in ("squint", "happy"):
                eye_r = 50
                iris_r = 36
                pupil_r = 25
            elif eye_mode == "half_closed":
                eye_r = 50
                iris_r = 30
                pupil_r = 20
            elif eye_mode == "angry":
                eye_r = 48
                iris_r = 34
                pupil_r = 24

            if eye_mode == "looking_up":
                look_offset = -8
            elif eye_mode == "sad":
                look_offset = 5
            elif eye_mode == "angry":
                look_offset = 3
            else:
                look_offset = 0

            if blink_offset < 15:
                pygame.draw.circle(self.screen, (255, 255, 255), ec, eye_r)
                pygame.draw.circle(self.screen, (102, 59, 42), (ec[0], ec[1] + look_offset), iris_r)
                po = (ex // 80) * 4 + look_offset // 3
                pygame.draw.circle(self.screen, (31, 17, 11), (ec[0] + po, ec[1] + look_offset), pupil_r)
                pygame.draw.circle(self.screen, (255, 255, 255), (ec[0] - 18 + po, ec[1] - 18 + look_offset), highlight_r)

            if eye_mode == "angry" and blink_offset < 15:
                brow_y = ec[1] - eye_r - 5
                pygame.draw.line(self.screen, (40, 40, 50),
                                 (ec[0] - eye_r + 5, brow_y + 5),
                                 (ec[0] + eye_r - 5, brow_y - 5), 4)
            elif eye_mode == "sad" and blink_offset < 15:
                brow_y = ec[1] - eye_r - 5
                pygame.draw.line(self.screen, (40, 40, 50),
                                 (ec[0] - eye_r + 5, brow_y - 5),
                                 (ec[0] + eye_r - 5, brow_y + 5), 4)

        if show_blush:
            for bx in (-115, 115):
                s = pygame.Surface((50, 30), pygame.SRCALPHA)
                s.fill((255, 138, 138, 60))
                self.screen.blit(s, (cx + bx - 25, cy + 60))

        nose_outer = pygame.Rect(cx - 15, cy + 40, 30, 20)
        nose_inner = pygame.Rect(cx - 8, cy + 42, 16, 8)
        pygame.draw.ellipse(self.screen, (53, 72, 87), nose_outer)
        pygame.draw.ellipse(self.screen, (86, 110, 128), nose_inner)

        if mouth_mode == "smile":
            mouth_rect = (cx - 80, cy + 100, 160, 70)
            pygame.draw.arc(self.screen, (35, 66, 82), mouth_rect, 0.1, math.pi - 0.1, 5)
        elif mouth_mode == "big_smile":
            mouth_rect = (cx - 90, cy + 90, 180, 90)
            pygame.draw.arc(self.screen, (35, 66, 82), mouth_rect, 0.1, math.pi - 0.1, 5)
            for mc in [(cx - 85, cy + 98), (cx + 85, cy + 98)]:
                pygame.draw.circle(self.screen, (35, 66, 82), mc, 3)
        elif mouth_mode == "neutral":
            pygame.draw.line(self.screen, (35, 66, 82),
                             (cx - 30, cy + 135), (cx + 30, cy + 135), 4)
        elif mouth_mode == "frown":
            mouth_rect = (cx - 70, cy + 120, 140, 60)
            pygame.draw.arc(self.screen, (35, 66, 82), mouth_rect, math.pi + 0.1, -0.1, 5)
        elif mouth_mode == "open":
            pygame.draw.ellipse(self.screen, (35, 66, 82), (cx - 20, cy + 110, 40, 40))
            pygame.draw.ellipse(self.screen, (60, 40, 40), (cx - 14, cy + 118, 28, 28))
        elif mouth_mode == "open_smile":
            pygame.draw.ellipse(self.screen, (35, 66, 82), (cx - 30, cy + 105, 60, 50))
            pygame.draw.circle(self.screen, (200, 80, 80), (cx, cy + 120), 8)
            for mc in [(cx - 28, cy + 108), (cx + 28, cy + 108)]:
                pygame.draw.circle(self.screen, (35, 66, 82), mc, 4)
        elif mouth_mode == "pursed":
            pygame.draw.ellipse(self.screen, (35, 66, 82), (cx - 12, cy + 120, 24, 10))
        elif mouth_mode == "smirk":
            pygame.draw.arc(self.screen, (35, 66, 82), (cx - 60, cy + 100, 120, 70), 0.1, math.pi - 0.1, 5)
            pygame.draw.line(self.screen, (35, 66, 82),
                             (cx + 40, cy + 115), (cx + 60, cy + 120), 4)

        hat_y = cy - 130
        hat_w, hat_h = 250, 120
        hat_r = pygame.Rect(cx - hat_w // 2, hat_y, hat_w, hat_h)
        pygame.draw.ellipse(self.screen, (140, 88, 50), hat_r)

        for i in range(4):
            yo = hat_y + 15 + i * 22
            sx = cx - 100 + i * 12
            ex = cx + 80 - i * 10
            pygame.draw.line(self.screen, (74, 47, 27), (sx, yo), (ex, yo + 25), 3)
            pygame.draw.line(self.screen, (255, 208, 128),
                             (cx + 100 - i * 12, yo + 8), (cx - 80 + i * 10, yo + 30), 2)

        pygame.draw.ellipse(self.screen, (94, 58, 31),
                            (cx - hat_w // 2, hat_y + hat_h - 15, hat_w, 15))
        pygame.draw.line(self.screen, (255, 208, 128),
                         (cx - 110, hat_y + hat_h - 10), (cx + 110, hat_y + hat_h - 10), 2)

        for p in self.particles:
            p.draw(self.screen, cx, cy)

        if NOTO_FONT:
            name_color = (80, 80, 90)
            status_color = (120, 120, 130)
            name_surf = NOTO_FONT.render("Bejo AI", True, name_color)
            status_surf = NOTO_FONT.render(self.status, True, status_color)
            tw_n = name_surf.get_width()
            tw_s = status_surf.get_width()
            self.screen.blit(name_surf, (cx - tw_n // 2, self.win_h - 50))
            self.screen.blit(status_surf, (cx - tw_s // 2, self.win_h - 26))

    def tick(self):
        try:
            dt = self.clock.tick(30) / 1000.0
            self.poll_events()
            self.process_commands()
            self.update_animation(dt)
            self.draw()
            pygame.display.flip()
        except pygame.error:
            self.running = False
        return self.running
