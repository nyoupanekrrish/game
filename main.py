# -*- coding: utf-8 -*-
import pygame
import random
import math
import sys
import json
import os
from pygame import gfxdraw

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 1100, 700
GROUND_HEIGHT = 120
BLACK = (8, 8, 14)
DARK_GRAY = (22, 22, 34)
GRAY = (55, 55, 70)
LIGHT_GRAY = (120, 120, 135)
WHITE = (245, 245, 255)
RED = (235, 55, 75)
ORANGE = (255, 165, 30)
BLUE = (60, 140, 255)
GREEN = (60, 220, 130)
FIRE_COLORS = [(255, 100, 0), (255, 50, 0), (255, 150, 0), (255, 210, 60)]
# New accent colors for UI
CYAN      = (0, 220, 255)
GOLD      = (255, 215, 0)
PURPLE    = (150, 80, 255)
PINK      = (255, 100, 180)
UI_DARK   = (12, 12, 22, 210)   # glassmorphism panel bg
UI_BORDER = (80, 100, 200, 160) # glassmorphism border

# Fonts - prefer bundled professional fonts then fall back to system sans-serif
def load_preferred_font(path_list, size):
    for p in path_list:
        try:
            if os.path.exists(p):
                return pygame.font.Font(p, size)
        except Exception:
            continue
    # Try popular system fonts
    for name in ["Segoe UI", "Arial", "Helvetica", "Sans"]:
        try:
            f = pygame.font.SysFont(name, size)
            if f:
                return f
        except Exception:
            continue
    # Ultimate fallback
    return pygame.font.Font(None, size)

# Title: prefer a clear, professional sans-serif (e.g., Inter/Roboto/Segoe)
FONT_TITLE = load_preferred_font([
    "fonts/Inter-Bold.ttf",
    "fonts/Roboto-Bold.ttf",
    "fonts/Orbitron-Bold.ttf"
], 64)
FONT_LARGE = load_preferred_font(["fonts/Inter-SemiBold.ttf", "fonts/Orbitron-Medium.ttf"], 48)
FONT_MEDIUM = load_preferred_font(["fonts/Inter-Regular.ttf", "fonts/Orbitron-Regular.ttf"], 36)
FONT_SMALL = load_preferred_font(["fonts/Inter-Regular.ttf", "fonts/Orbitron-Regular.ttf"], 28)
FONT_TINY = load_preferred_font(["fonts/Inter-Regular.ttf", "fonts/Orbitron-Regular.ttf"], 20)

# Game name
GAME_NAME = "JUMPING ENGINEER"

# ── UI Drawing Helpers ──────────────────────────────────────────────────────

def draw_outlined_text(surface, text, font, x, y, color, outline_color=(0,0,0),
                       outline=2, center=False):
    """Render text with a pixel-perfect outline + soft drop-shadow."""
    rendered = font.render(text, True, color)
    if center:
        x = x - rendered.get_width() // 2
        y = y - rendered.get_height() // 2
    # Drop shadow
    shadow = font.render(text, True, (0, 0, 0))
    shadow.set_alpha(120)
    surface.blit(shadow, (x + outline + 1, y + outline + 1))
    # Outline
    for dx in range(-outline, outline + 1):
        for dy in range(-outline, outline + 1):
            if dx == 0 and dy == 0:
                continue
            out = font.render(text, True, outline_color)
            surface.blit(out, (x + dx, y + dy))
    # Main text
    surface.blit(rendered, (x, y))
    return rendered


def draw_glass_panel(surface, rect, bg_color=(12, 12, 24), bg_alpha=200,
                     border_color=(80, 100, 220), border_alpha=180,
                     border_radius=20, border_width=2):
    """Draw a frosted-glass style rounded panel."""
    # Background fill
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*bg_color, bg_alpha), (0, 0, rect.width, rect.height),
                     border_radius=border_radius)
    # Inner lighter top strip (glass highlight)
    high = pygame.Surface((rect.width - 8, rect.height // 3), pygame.SRCALPHA)
    high.fill((255, 255, 255, 18))
    panel.blit(high, (4, 4))
    surface.blit(panel, rect.topleft)
    # Border
    border_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(border_surf, (*border_color, border_alpha),
                     (0, 0, rect.width, rect.height),
                     border_width, border_radius=border_radius)
    surface.blit(border_surf, rect.topleft)


def draw_vignette(surface, width, height, strength=140):
    """Subtle dark vignette around edges."""
    vig = pygame.Surface((width, height), pygame.SRCALPHA)
    for r in range(min(width, height) // 2, 0, -6):
        alpha = int(strength * (1 - r / (min(width, height) / 2)))
        pygame.draw.rect(vig, (0, 0, 0, max(0, min(255, alpha))),
                         (width // 2 - r, height // 2 - r, r * 2, r * 2),
                         border_radius=r)
    surface.blit(vig, (0, 0))

class Particle:
    def __init__(self, x, y, particle_type="fire"):
        self.x = x
        self.y = y
        self.type = particle_type
        self.original_x = x
        
        if particle_type == "fire":
            self.size = random.randint(8, 15)
            self.color = random.choice(FIRE_COLORS)
            self.speed_x = random.uniform(-1.5, 1.5)
            self.speed_y = random.uniform(-5, -2)
            self.lifetime = random.randint(30, 50)
            self.gravity = 0.15
            self.fade_speed = random.uniform(0.1, 0.3)
        elif particle_type == "spark":
            self.size = random.randint(2, 4)
            self.color = random.choice([(255, 255, 200), (255, 200, 100), WHITE])
            self.speed_x = random.uniform(-3, 3)
            self.speed_y = random.uniform(-4, 0)
            self.lifetime = random.randint(20, 40)
            self.gravity = 0.2
            self.fade_speed = random.uniform(0.15, 0.25)
        elif particle_type == "smoke":
            self.size = random.randint(10, 20)
            self.color = (100, 100, 100, 150)
            self.speed_x = random.uniform(-0.5, 0.5)
            self.speed_y = random.uniform(-1, -0.5)
            self.lifetime = random.randint(60, 100)
            self.gravity = 0.02
            self.fade_speed = random.uniform(0.05, 0.1)
    
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        
        if self.type == "fire":
            self.size = max(0, self.size - self.fade_speed)
        elif self.type == "spark":
            self.size = max(0, self.size - self.fade_speed * 1.5)
        elif self.type == "smoke":
            self.size = min(self.size + 0.1, 25)
        
        self.lifetime -= 1
    
    def draw(self, screen):
        if self.size > 0:
            if self.type == "fire":
                # Fire particles with glow effect
                pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), 
                                           int(self.size), self.color)
                pygame.gfxdraw.aacircle(screen, int(self.x), int(self.y), 
                                      int(self.size), self.color)
                
                # Inner glow
                inner_color = (min(255, self.color[0] + 50), 
                             min(255, self.color[1] + 50), 
                             min(255, self.color[2] + 50))
                pygame.gfxdraw.filled_circle(screen, int(self.x), int(self.y), 
                                           int(self.size * 0.6), inner_color)
            elif self.type == "spark":
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                                 int(self.size))
            elif self.type == "smoke":
                s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(s, self.color, (int(self.size), int(self.size)), int(self.size))
                screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

class FireText:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.particles = []
        self.alpha = 255
        self.fade_in = True
        self.active = True
        self.frame = 0
        
        # Create initial fire particles along text path
        self.create_fire_particles()
    
    def create_fire_particles(self):
        # Create particles along where text would be
        for i in range(len(self.text) * 10):
            offset_x = random.randint(-200, 200)
            offset_y = random.randint(-50, 50)
            self.particles.append(Particle(self.x + offset_x, self.y + offset_y, "fire"))
    
    def update(self):
        self.frame += 1
        
        # Update alpha for fade in/out
        if self.fade_in:
            self.alpha = min(255, self.alpha + 5)
            if self.alpha == 255:
                self.fade_in = False
        elif self.frame > 180:  # Show for 3 seconds then fade out
            self.alpha = max(0, self.alpha - 3)
            if self.alpha == 0:
                self.active = False
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0 or particle.size <= 0:
                self.particles.remove(particle)
        
        # Add new particles occasionally
        if self.frame % 2 == 0 and self.active:
            for _ in range(3):
                offset_x = random.randint(-200, 200)
                offset_y = random.randint(-30, 30)
                self.particles.append(Particle(self.x + offset_x, self.y + offset_y, "fire"))
    
    def draw(self, screen):
        # Draw particles first
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw text with fire effect
        if self.alpha > 0:
            # Create multiple layers for fire effect
            colors = [
                (255, 50, 0, self.alpha),    # Dark red
                (255, 100, 0, self.alpha),   # Red-orange
                (255, 150, 0, self.alpha),   # Orange
                (255, 200, 50, self.alpha),  # Yellow-orange
            ]
            
            # Draw text with offset for fire effect
            for i, color in enumerate(colors):
                offset = i * 0.5
                # Main text
                text_surface = FONT_TITLE.render(self.text, True, color[:3])
                text_surface.set_alpha(color[3])
                screen.blit(text_surface, 
                          (self.x - text_surface.get_width()//2 + offset, 
                           self.y - text_surface.get_height()//2 + offset))

def draw_heart(surface, x, y, size, color, outline=False):
    # Smooth parametric heart scaled to `size`.
    cx = x + size / 2
    cy = y + size / 3
    pts = []
    for deg in range(0, 361, 8):
        t = math.radians(deg)
        tx = 16 * math.sin(t) ** 3
        ty = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        sx = cx + (tx * (size / 32.0))
        sy = cy - (ty * (size / 32.0))
        pts.append((int(sx), int(sy)))

    if outline:
        if len(pts) >= 3:
            pygame.gfxdraw.aapolygon(surface, pts, color)
            pygame.gfxdraw.polygon(surface, pts, color)
    else:
        if len(pts) >= 3:
            pygame.gfxdraw.filled_polygon(surface, pts, color)
            pygame.gfxdraw.aapolygon(surface, pts, color)

class GlowButton:
    def __init__(self, text, x, y, width=200, height=60, image_path=None, is_menu_button=False, game=None):
        self.text = text
        self.rect = pygame.Rect(x - width//2, y, width, height)
        self.color = (70, 130, 230)
        self.hover_color = (90, 150, 255)
        self.glow_intensity = 0
        self.hover = False
        self.clicked = False
        self.image = None
        self.hover_image = None
        self.use_image = False
        self.is_menu_button = is_menu_button
        self.game = game
        self.hover_sound_played = False
        
        # Load image if provided
        if image_path and os.path.exists(image_path):
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width - 10, height - 10))
                self.use_image = True
                
                # For menu buttons, try to load hover image
                if is_menu_button:
                    hover_path = image_path.replace(".png", "glow.png")
                    if os.path.exists(hover_path):
                        try:
                            self.hover_image = pygame.image.load(hover_path).convert_alpha()
                            self.hover_image = pygame.transform.scale(self.hover_image, (width - 10, height - 10))
                        except:
                            pass
            except:
                pass
    
    def update(self, mouse_pos):
        prev_hover = self.hover
        self.hover = self.rect.collidepoint(mouse_pos)
        
        # Play sound on hover for menu buttons
        if self.hover and not prev_hover and self.is_menu_button and self.game:
            self.game.play_sound("click")
        
        # Smooth transitions for hover state
        if self.hover:
            self.glow_intensity = min(self.glow_intensity + 0.08, 1.0)
        else:
            self.glow_intensity = max(self.glow_intensity - 0.06, 0.0)
    
    def is_clicked(self, mouse_pos, mouse_click):
        if self.rect.collidepoint(mouse_pos) and mouse_click:
            self.clicked = True
            # Play pick sound for menu buttons on click
            if self.is_menu_button and self.game:
                self.game.play_sound("pick")
            return True
        return False
    
    def draw(self, screen):
        # Draw image button - simple for menu buttons, with glow for in-game buttons
        if self.use_image and self.image:
            # Determine which image to display
            display_image = self.image
            if self.is_menu_button and self.hover and self.hover_image:
                display_image = self.hover_image
            
            img_x = self.rect.centerx - display_image.get_width() // 2
            img_y = self.rect.centery - display_image.get_height() // 2
            
            # Menu buttons: just display image directly
            if self.is_menu_button:
                screen.blit(display_image, (img_x, img_y))
            else:
                # In-game buttons (jump, shield): draw with circular crystal button effect
                center_x = self.rect.centerx
                center_y = self.rect.centery
                radius = self.rect.width // 2
                
                # Outer white transparent circle (glow effect)
                glow_surface = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
                
                # Create gradient-like glow with multiple circles
                for i in range(15, 0, -1):
                    alpha = int(40 * (1 - i / 15))
                    pygame.draw.circle(glow_surface, (255, 255, 255, alpha), (radius + 10, radius + 10), radius + i)
                
                screen.blit(glow_surface, (center_x - radius - 10, center_y - radius - 10))
                
                # Main white semi-transparent circle (crystal effect)
                crystal_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(crystal_surface, (255, 255, 255, 60), (radius, radius), radius)
                pygame.draw.circle(crystal_surface, (255, 255, 255, 120), (radius, radius), radius, 3)
                
                screen.blit(crystal_surface, (center_x - radius, center_y - radius))
                screen.blit(display_image, (img_x, img_y))
        else:
            # ── Premium rectangular button ──────────────────────────────────
            t = self.glow_intensity  # 0.0 idle → 1.0 hover

            # 1. Deep drop shadow
            shadow = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (0, 0, 0, 100),
                             (6, 6, self.rect.width, self.rect.height), border_radius=16)
            screen.blit(shadow, (self.rect.x - 6, self.rect.y - 6))

            # 2. Gradient-like body: two layers (dark base + lighter top half)
            base_col = (int(25 + 35 * t), int(35 + 60 * t), int(80 + 80 * t))
            body = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(body, (*base_col, 245),
                             (0, 0, self.rect.width, self.rect.height), border_radius=16)
            # Top-half lighter strip (simulates gradient)
            top = pygame.Surface((self.rect.width - 6, self.rect.height // 2), pygame.SRCALPHA)
            top.fill((255, 255, 255, int(30 + 20 * t)))
            body.blit(top, (3, 3))
            screen.blit(body, self.rect.topleft)

            # 3. Animated neon glow border (brighter on hover)
            border_alpha = int(120 + 135 * t)
            glow_color = (int(60 + 120 * t), int(140 + 80 * t), 255)
            border_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            # Outer glow when hovered
            if t > 0.01:
                glow_rect = pygame.Rect(-int(4 * t), -int(4 * t),
                                        self.rect.width + int(8 * t),
                                        self.rect.height + int(8 * t))
                glow_s = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_s, (*glow_color, int(80 * t)),
                                 (0, 0, self.rect.width + 20, self.rect.height + 20),
                                 border_radius=20)
                screen.blit(glow_s, (self.rect.x - 10, self.rect.y - 10))
            pygame.draw.rect(border_surf, (*glow_color, border_alpha),
                             (0, 0, self.rect.width, self.rect.height), 2, border_radius=16)
            screen.blit(border_surf, self.rect.topleft)

            # 4. Outlined text with hover scale
            scale = 1.0 + 0.07 * t
            txt_color = (int(200 + 55 * t), int(220 + 35 * t), 255)
            outline_col = (0, int(20 * t), int(60 * t))
            txt_base = FONT_SMALL.render(self.text, True, txt_color)
            txt_w = int(txt_base.get_width() * scale)
            txt_h = int(txt_base.get_height() * scale)
            txt_surf = pygame.transform.smoothscale(txt_base, (txt_w, txt_h))
            # Outline (rendered separately at original size, then scaled)
            out_base = FONT_SMALL.render(self.text, True, (0, 0, 30))
            out_surf = pygame.transform.smoothscale(out_base, (txt_w, txt_h))
            txt_x = int(self.rect.centerx - txt_w // 2)
            txt_y = int(self.rect.centery - txt_h // 2)
            for odx, ody in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                screen.blit(out_surf, (txt_x + odx, txt_y + ody))
            screen.blit(txt_surf, (txt_x, txt_y))

    def set_center(self, x, y):
        self.rect.center = (x, y)

class Player:
    def __init__(self):
        # Player properties
        self.x = 200
        self.y = HEIGHT - GROUND_HEIGHT - 120
        self.width = 90
        self.height = 120
        self.velocity_y = 0
        self.jumping = False
        self.lives = 3
        self.score = 0
        self.speed = 8
        self.base_speed = 8
        
        # Animation states
        self.state = "running"
        self.frame_index = 0
        self.animation_speed = 0.15
        self.hurt_timer = 0
        self.death_animation_complete = False
        self.invincible = False
        self.invincible_timer = 0
        
        # Double jump mechanics
        self.double_jump_available = True
        self.double_jump_cooldown = 600  # 10 seconds (60 FPS * 10)
        self.double_jump_cooldown_timer = 0
        self.can_double_jump = False  # Can only use double jump once per air session
        
        # Shield mechanics
        self.shield_active = False
        self.shield_duration = 300  # 5 seconds duration
        self.shield_timer = 0
        self.shield_cooldown = 600  # 10 seconds cooldown
        self.shield_cooldown_timer = 0
        self.shield_available = True
        
        # Load animations
        self.load_animations()
        
        # Current image
        self.image = self.animations["running"][0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
    
    def load_animations(self):
        self.animations = {
            "running": [],
            "jumping": [],
            "hurt": [],
            "dying": []
        }
        
        # Try to load actual images
        try:
            # Running animation
            run_frames = ["Run1.png", "Run2.png", "Run3.png"]
            for frame in run_frames:
                if os.path.exists(frame):
                    img = pygame.image.load(frame).convert_alpha()
                    img = pygame.transform.scale(img, (90, 120))
                    self.animations["running"].append(img)
            
            # Jumping animation
            jump_frames = ["Jump1.png", "Jump2.png", "Jump3.png", "Jump4.png"]
            for frame in jump_frames:
                if os.path.exists(frame):
                    img = pygame.image.load(frame).convert_alpha()
                    img = pygame.transform.scale(img, (90, 120))
                    self.animations["jumping"].append(img)
            
            # Hurt animation
            if os.path.exists("hurt.jpg"):
                hurt_img = pygame.image.load("hurt.jpg").convert_alpha()
                hurt_img = pygame.transform.scale(hurt_img, (90, 120))
                self.animations["hurt"].append(hurt_img)
            
            # Dying animation
            die_frames = ["Die1.png", "Die2.png", "Die3.png"]
            for frame in die_frames:
                if os.path.exists(frame):
                    img = pygame.image.load(frame).convert_alpha()
                    img = pygame.transform.scale(img, (90, 120))
                    self.animations["dying"].append(img)
        except:
            pass
        
        # Create placeholders for any missing animations
        if not self.animations["running"]:
            for i in range(3):
                surf = pygame.Surface((90, 120), pygame.SRCALPHA)
                color = BLUE if i % 2 == 0 else (60, 110, 200)
                pygame.draw.rect(surf, color, (0, 0, 90, 120))
                self.animations["running"].append(surf)
        
        if not self.animations["jumping"]:
            for i in range(4):
                surf = pygame.Surface((90, 120), pygame.SRCALPHA)
                pygame.draw.rect(surf, (80, 140, 240), (0, 0, 90, 120))
                self.animations["jumping"].append(surf)
        
        if not self.animations["hurt"]:
            surf = pygame.Surface((90, 120), pygame.SRCALPHA)
            pygame.draw.rect(surf, RED, (0, 0, 90, 120))
            self.animations["hurt"].append(surf)
        
        if not self.animations["dying"]:
            for i in range(3):
                surf = pygame.Surface((90, 120), pygame.SRCALPHA)
                gray = 150 - i * 30
                pygame.draw.rect(surf, (gray, gray, gray), (0, 0, 90, 120))
                self.animations["dying"].append(surf)
    
    def jump(self):
        # Regular jump from ground
        if not self.jumping and self.state not in ["hurt", "dying", "dead"]:
            self.velocity_y = -20
            self.jumping = True
            self.can_double_jump = True  # Enable double jump after leaving ground
            self.state = "jumping"
            self.frame_index = 0
    
    def double_jump(self):
        # Double jump while in air (only if available and can be used)
        if self.jumping and self.can_double_jump and self.double_jump_available and self.state not in ["hurt", "dying", "dead"]:
            self.velocity_y = -20  # Same strength as regular jump
            self.can_double_jump = False  # Can only double jump once per air session
            self.double_jump_available = False
            self.double_jump_cooldown_timer = self.double_jump_cooldown
            return True
        return False
    
    def activate_shield(self):
        # Activate shield protection
        if self.shield_available and self.state not in ["hurt", "dying", "dead"]:
            self.shield_active = True
            self.shield_timer = self.shield_duration
            self.shield_available = False
            self.shield_cooldown_timer = self.shield_cooldown
            # Play shield sound
            if hasattr(self, 'game'):
                self.game.play_sound("shield")
            return True
        return False
    
    def update(self):
        # Gravity
        if self.jumping:
            self.velocity_y += 1
            self.y += self.velocity_y
            
            # Land on ground
            if self.y >= HEIGHT - GROUND_HEIGHT - self.height:
                self.y = HEIGHT - GROUND_HEIGHT - self.height
                self.jumping = False
                self.can_double_jump = False  # Reset double jump when landing
                if self.state != "hurt" and self.state != "dying":
                    self.state = "running"
        
        # Update double jump cooldown
        if self.double_jump_cooldown_timer > 0:
            self.double_jump_cooldown_timer -= 1
        elif not self.double_jump_available:
            self.double_jump_available = True  # Cooldown complete, double jump available again
        
        # Update shield
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.shield_cooldown_timer > 0:
            self.shield_cooldown_timer -= 1
        elif not self.shield_available:
            self.shield_available = True  # Cooldown complete, shield available again
        
        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # Animation updates
        if self.state == "hurt":
            self.hurt_timer -= 1
            if self.hurt_timer <= 0 and self.lives > 0:
                self.state = "running"
                self.invincible = True
                self.invincible_timer = 90
        elif self.state == "dying":
            self.frame_index += self.animation_speed * 0.3
            if self.frame_index >= len(self.animations["dying"]):
                self.state = "dead"
                self.death_animation_complete = True
        elif self.state == "running" and not self.jumping:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations["running"]):
                self.frame_index = 0
        elif self.state == "jumping":
            self.frame_index += self.animation_speed * 0.6
            if self.frame_index >= len(self.animations["jumping"]):
                self.frame_index = len(self.animations["jumping"]) - 1
        
        # Update speed based on score
        speed_multiplier = 1 + (self.score // 10) * 0.03
        self.speed = self.base_speed * speed_multiplier
        
        # Update rect position
        self.rect.topleft = (self.x, self.y)
    
    def take_damage(self):
        if not self.invincible and self.state not in ["hurt", "dying", "dead"]:
            self.lives -= 1
            if self.lives <= 0:
                self.state = "dying"
                self.frame_index = 0
            else:
                self.state = "hurt"
                self.hurt_timer = 120
                self.frame_index = 0
                self.invincible = True
                self.invincible_timer = 120
            return True
        return False
    
    def add_heart(self):
        if self.lives < 3:
            self.lives += 1
    
    def draw(self, screen):
        # Get current frame
        if self.state == "running":
            frame = int(self.frame_index) % len(self.animations["running"])
            current_image = self.animations["running"][frame]
        elif self.state == "jumping":
            frame = min(int(self.frame_index), len(self.animations["jumping"]) - 1)
            current_image = self.animations["jumping"][frame]
        elif self.state == "hurt":
            current_image = self.animations["hurt"][0]
        elif self.state == "dying":
            frame = min(int(self.frame_index), len(self.animations["dying"]) - 1)
            current_image = self.animations["dying"][frame]
        else:
            current_image = self.animations["running"][0]
        
        # Draw shadow
        shadow = pygame.Surface((self.width, 20), pygame.SRCALPHA)
        shadow_color = (0, 0, 0, 80 - abs(self.velocity_y) * 2)
        pygame.draw.ellipse(shadow, shadow_color, (0, 0, self.width, 20))
        screen.blit(shadow, (self.x, HEIGHT - GROUND_HEIGHT - 10))
        
        # Flash effect when invincible
        if self.invincible and self.state not in ["dying", "dead"]:
            if pygame.time.get_ticks() % 150 < 75:
                screen.blit(current_image, (self.x, self.y))
        else:
            screen.blit(current_image, (self.x, self.y))
        
        # Draw shield if active
        if self.shield_active:
            shield_radius = int(self.width // 2 + 30)
            shield_center = (int(self.x + self.width // 2), int(self.y + self.height // 2))
            # Pulsing shield effect
            pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5
            shield_alpha = int(150 * pulse)
            
            # Draw shield circle
            shield_surf = pygame.Surface((shield_radius * 2 + 10, shield_radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(shield_surf, (100, 200, 255, shield_alpha), 
                             (shield_radius + 5, shield_radius + 5), shield_radius, 3)
            
            screen.blit(shield_surf, (shield_center[0] - shield_radius - 5, 
                                    shield_center[1] - shield_radius - 5))

class Obstacle:
    def __init__(self, x, speed):
        self.x = x
        self.width = random.randint(50, 90)
        self.height = random.randint(40, 70)
        self.y = HEIGHT - GROUND_HEIGHT - self.height
        self.speed = speed
        self.passed = False
        self.glow_pulse = 0
        self.pulse_speed = random.uniform(0.05, 0.1)
        
        # Load obstacle images
        self.load_images()
        
        # Choose random obstacle type
        self.type = random.choice(["obj1", "obj2", "obj3"])
        self.image = self.images[self.type]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.x, self.y)
        
        # Set color based on type
        if self.type == "obj1":
            self.color = (220, 80, 80)  # Red
        elif self.type == "obj2":
            self.color = (180, 140, 80)  # Brown
        else:
            self.color = (120, 120, 140)  # Gray
    
    def load_images(self):
        self.images = {}
        # Try to load actual images
        try:
            if os.path.exists("obj1.png"):
                obj1_img = pygame.image.load("obj1.png").convert_alpha()
                obj1_img = pygame.transform.scale(obj1_img, (60, 70))
                self.images["obj1"] = obj1_img
            
            if os.path.exists("obj2.png"):
                obj2_img = pygame.image.load("obj2.png").convert_alpha()
                obj2_img = pygame.transform.scale(obj2_img, (70, 60))
                self.images["obj2"] = obj2_img
            
            if os.path.exists("obj3.png"):
                obj3_img = pygame.image.load("obj3.png").convert_alpha()
                obj3_img = pygame.transform.scale(obj3_img, (65, 65))
                self.images["obj3"] = obj3_img
        except:
            pass
        
        # Create placeholders for any missing images
        if "obj1" not in self.images:
            surf = pygame.Surface((60, 70), pygame.SRCALPHA)
            pygame.draw.rect(surf, (220, 80, 80), (0, 10, 60, 60), border_radius=5)
            self.images["obj1"] = surf
        
        if "obj2" not in self.images:
            surf = pygame.Surface((70, 60), pygame.SRCALPHA)
            pygame.draw.rect(surf, (180, 140, 80), (0, 0, 70, 60), border_radius=8)
            self.images["obj2"] = surf
        
        if "obj3" not in self.images:
            surf = pygame.Surface((65, 65), pygame.SRCALPHA)
            pygame.draw.rect(surf, (120, 120, 140), (0, 0, 65, 65), border_radius=12)
            self.images["obj3"] = surf
    
    def update(self, player_speed):
        self.x -= player_speed
        self.rect.topleft = (self.x, self.y)
        self.glow_pulse += self.pulse_speed
    
    def draw(self, screen):
        # Draw glow effect
        glow_intensity = (math.sin(self.glow_pulse) + 1) * 0.5 * 0.3
        
        if glow_intensity > 0:
            glow_size = int(15 * glow_intensity)
            glow_surf = pygame.Surface((self.width + glow_size * 2, 
                                      self.height + glow_size * 2), 
                                     pygame.SRCALPHA)
            
            for i in range(glow_size, 0, -1):
                alpha = int(100 * glow_intensity * (i / glow_size))
                color = (*self.color, alpha)
                pygame.draw.rect(glow_surf, color, 
                               (glow_size - i, glow_size - i,
                                self.width + 2 * i, self.height + 2 * i),
                               border_radius=10)
            
            screen.blit(glow_surf, 
                       (self.x - glow_size, self.y - glow_size))
        
        # Draw obstacle
        screen.blit(self.image, (self.x, self.y))

class Asteroid:
    def __init__(self, x=None):
        # Asteroid falls from top of screen at random x position
        self.x = x if x else random.randint(50, WIDTH - 50)
        self.y = -80  # Start above screen
        self.width = 60
        self.height = 60
        self.velocity_y = random.uniform(3, 7)  # Falling speed
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.passed = False
        self.color = (150, 100, 50)  # Brown/rocky color
        self.rect = pygame.Rect(self.x - self.width//2, self.y, self.width, self.height)
        
        # Load GIF animation
        self.gif_frames = []
        self.frame_index = 0
        self.load_gif()
    
    def load_gif(self):
        """Load obj1.gif image"""
        try:
            if os.path.exists("obj1.gif"):
                img = pygame.image.load("obj1.gif").convert_alpha()
                # Scale to desired size
                img_scaled = pygame.transform.scale(img, (self.width, self.height))
                self.gif_frames = [img_scaled]  # Store as single frame for consistency
            else:
                print("obj1.gif not found")
        except Exception as e:
            print(f"Error loading obj1.gif: {e}")
            # If file not found, use fallback
            pass
    
    def update(self):
        # Fall down
        self.y += self.velocity_y
        self.rotation += self.rotation_speed
        self.rect.topleft = (self.x - self.width//2, self.y)
        
        # Update animation frame
        if self.gif_frames:
            self.frame_index = (self.frame_index + 0.15) % len(self.gif_frames)
    
    def draw(self, screen):
        # Draw glowing asteroid
        # Create glow
        glow_size = 15
        glow_surf = pygame.Surface((self.width + glow_size * 2, self.height + glow_size * 2), pygame.SRCALPHA)
        
        for i in range(glow_size, 0, -1):
            alpha = int(50 * (1 - i / glow_size))
            pygame.draw.circle(glow_surf, (255, 150, 0, alpha), 
                             (self.width//2 + glow_size, self.height//2 + glow_size), 
                             self.width//2 + i)
        
        screen.blit(glow_surf, (self.x - self.width//2 - glow_size, self.y - glow_size))
        
        # Draw asteroid image if loaded
        if self.gif_frames:
            current_frame = self.gif_frames[int(self.frame_index) % len(self.gif_frames)]
            screen.blit(current_frame, (self.x - self.width//2, self.y))
        else:
            # Fallback: Draw main asteroid as circle/irregular shape
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y + self.height//2)), 
                             int(self.width//2))
            # Highlight
            pygame.draw.circle(screen, (200, 150, 80), (int(self.x - self.width//4), int(self.y + self.height//4)), 
                             int(self.width//4))


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
        pygame.display.set_caption(GAME_NAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "start_menu"
        self.player = Player()
        self.obstacles = []
        self.obstacle_timer = 0
        self.obstacle_frequency = 70
        self.background_offset = 0
        self.particles = []
        self.fire_text = None
        self.start_animation_time = 0
        
        # Load countdown images
        try:
            self.countdown_images = {
                "3": pygame.image.load("3.png"),
                "2": pygame.image.load("2.png"),
                "1": pygame.image.load("1.png"),
                "GO!": pygame.image.load("go.png")
            }
        except Exception as e:
            print(f"Warning: Could not load countdown images: {e}")
            self.countdown_images = {}
        
        # Asteroids
        self.asteroids = []
        self.asteroid_timer = 0
        self.asteroid_frequency = 300  # Spawn every 5 seconds (5 * 60 FPS)
        
        # UI Elements
        self.play_button = GlowButton("▶ START", WIDTH//2, HEIGHT//2 + 80, image_path="start.png", is_menu_button=True, game=self)
        self.exit_button = GlowButton("✖ EXIT", WIDTH//2, HEIGHT//2 + 180, image_path="exit.png", is_menu_button=True, game=self)
        self.settings_button = GlowButton("⚙ SETTINGS", WIDTH//2, HEIGHT//2 + 240, image_path="settings.png", is_menu_button=True, game=self)
        self.tutorial_button = GlowButton("❓ HOW TO PLAY", WIDTH//2, HEIGHT//2 + 320, image_path="howtoplay.png", is_menu_button=True, game=self)
        self.restart_button = GlowButton("↺ RESTART", WIDTH//2, HEIGHT//2 + 100, image_path="restart.png", is_menu_button=True, game=self)
        self.menu_button = GlowButton("← MENU", WIDTH//2, HEIGHT//2 + 180, 150, 50, image_path="menu.png", is_menu_button=True, game=self)
        self.back_button = GlowButton("← BACK", WIDTH//2, HEIGHT//2 + 220, 150, 50, image_path="back.png", is_menu_button=True, game=self)
        self.sound_button = GlowButton("🔊 SOUND: ON", WIDTH//2, HEIGHT//2 - 20, 260, 50, image_path="sound.png", is_menu_button=True, game=self)
        self.fullscreen_button = GlowButton("🖵 FULLSCREEN: OFF", WIDTH//2, HEIGHT//2 + 40, 260, 50, image_path="screen.png", is_menu_button=True, game=self)
        # On-screen touch/jump button and pause
        self.jump_touch_button = GlowButton("JUMP", WIDTH - 110, HEIGHT - 150, 100, 100, image_path="button.png")
        self.shield_button = GlowButton("SHIELD", WIDTH - 212, HEIGHT - 150, 100, 100, image_path="button1.png")
        self.pause_button = GlowButton("⏸ PAUSE", 90, 70, 140, 44, image_path="pause.png", is_menu_button=True, game=self)
        # Pause menu buttons
        self.resume_button = GlowButton("▶ RESUME", WIDTH//2, HEIGHT//2 - 40, 240, 60, image_path="resume.png", is_menu_button=True, game=self)
        self.pause_menu_button = GlowButton("← MENU", WIDTH//2, HEIGHT//2 + 50, 240, 60, image_path="menu.png", is_menu_button=True, game=self)
        self.paused = False
        self.last_mouse_click = False
        
        # Best score
        self.best_score = 0
        self.load_best_score()
        # Settings (persisted)
        self.settings = {
            "sound": True,
            "fullscreen": True,
            "map": 0
        }
        self.load_settings()
        # Update toggle labels to match loaded settings
        self.sound_button.text = "SOUND: ON" if self.settings.get("sound", True) else "SOUND: OFF"
        self.fullscreen_button.text = "FULLSCREEN: ON" if self.settings.get("fullscreen", False) else "FULLSCREEN: OFF"
        # Map selection button (0 = default, 1 = desert)
        self.map_button = GlowButton("MAP: DEFAULT", WIDTH//2, HEIGHT//2 + 120, image_path="map.png", is_menu_button=True, game=self)
        self.map_button.text = "MAP: DEFAULT" if self.settings.get("map", 0) == 0 else "MAP: DESERT"
        if self.settings.get("fullscreen", False):
            try:
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
            except:
                pass
        
        # Sound effects
        self.load_sounds()
        
        # Generate background elements
        self.generate_background()
        # Apply initial layouts so buttons are placed deterministically
        try:
            self.layout_start_menu()
            self.layout_settings_menu()
            self.layout_tutorial_menu()
            self.layout_game_over_menu()
        except Exception:
            pass
    
    def load_best_score(self):
        try:
            with open("best_score.json", "r") as f:
                data = json.load(f)
                self.best_score = data.get("best_score", 0)
        except:
            self.best_score = 0

    def load_settings(self):
        try:
            with open("settings.json", "r") as f:
                data = json.load(f)
                self.settings.update(data)
        except:
            pass

    def save_settings(self):
        try:
            with open("settings.json", "w") as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def save_best_score(self):
        try:
            with open("best_score.json", "w") as f:
                json.dump({"best_score": self.best_score}, f)
        except:
            pass
    
    def load_sounds(self):
        self.sounds = {}
        try:
            if os.path.exists("start.mp3"):
                self.sounds["start"] = pygame.mixer.Sound("start.mp3")
            if os.path.exists("hurt.mp3"):
                self.sounds["hurt"] = pygame.mixer.Sound("hurt.mp3")
            if os.path.exists("die.mp3"):
                self.sounds["die"] = pygame.mixer.Sound("die.mp3")
            if os.path.exists("jump.mp3"):
                self.sounds["jump"] = pygame.mixer.Sound("jump.mp3")
            if os.path.exists("score.mp3"):
                self.sounds["score"] = pygame.mixer.Sound("score.mp3")
            if os.path.exists("shield.mp3"):
                self.sounds["shield"] = pygame.mixer.Sound("shield.mp3")
            if os.path.exists("click.mp3"):
                self.sounds["click"] = pygame.mixer.Sound("click.mp3")
            if os.path.exists("pick.mp3"):
                self.sounds["pick"] = pygame.mixer.Sound("pick.mp3")
        except:
            print("Note: Some sound files are missing. Using silent placeholders.")
        
        # Create silent placeholders for missing sounds
        for sound_name in ["start", "hurt", "die", "jump", "score", "shield", "click", "pick"]:
            if sound_name not in self.sounds:
                self.sounds[sound_name] = pygame.mixer.Sound(buffer=bytes(1000))

        # Apply master volume according to settings
        vol = 1.0 if self.settings.get("sound", True) else 0.0
        try:
            for s in self.sounds.values():
                s.set_volume(vol)
        except:
            pass

    def play_sound(self, name):
        if not self.settings.get("sound", True):
            return
        snd = self.sounds.get(name)
        if snd:
            try:
                snd.play()
            except:
                pass
    
    def generate_background(self):
        # Generate different background elements depending on selected map
        self.background_elements = []
        map_sel = self.settings.get("map", 0)

        if map_sel == 0:
            # Default (forest/green) map
            # Create distant mountains
            for i in range(8):
                x = random.randint(0, WIDTH * 2)
                width = random.randint(200, 400)
                height = random.randint(150, 250)
                color = (random.randint(60, 100), random.randint(100, 140), random.randint(60, 100))
                speed = random.uniform(0.1, 0.3)
                self.background_elements.append({
                    "type": "mountain",
                    "x": x,
                    "y": HEIGHT - GROUND_HEIGHT - height,
                    "width": width,
                    "height": height,
                    "color": color,
                    "speed": speed
                })

            # Create trees
            for i in range(20):
                x = random.randint(0, WIDTH * 2)
                height = random.randint(80, 200)
                trunk_width = random.randint(20, 40)
                foliage_size = random.randint(60, 120)
                color = (random.randint(34, 60), random.randint(90, 130), random.randint(34, 60))
                trunk_color = (101, 67, 33)
                speed = random.uniform(0.3, 0.6)
                self.background_elements.append({
                    "type": "tree",
                    "x": x,
                    "y": HEIGHT - GROUND_HEIGHT - height,
                    "height": height,
                    "trunk_width": trunk_width,
                    "foliage_size": foliage_size,
                    "color": color,
                    "trunk_color": trunk_color,
                    "speed": speed
                })

            # Create clouds
            for i in range(12):
                x = random.randint(0, WIDTH * 2)
                y = random.randint(50, HEIGHT - GROUND_HEIGHT - 150)
                size = random.randint(40, 80)
                color = (220 + random.randint(-20, 20), 220 + random.randint(-20, 20), 220 + random.randint(-20, 20))
                speed = random.uniform(0.05, 0.2)
                self.background_elements.append({
                    "type": "cloud",
                    "x": x,
                    "y": y,
                    "size": size,
                    "color": color,
                    "speed": speed
                })

        else:
            # Desert map
            # Warm mountains / dunes
            for i in range(6):
                x = random.randint(0, WIDTH * 2)
                width = random.randint(250, 500)
                height = random.randint(120, 220)
                color = (random.randint(180, 230), random.randint(140, 190), random.randint(80, 120))
                speed = random.uniform(0.05, 0.2)
                self.background_elements.append({
                    "type": "mountain",
                    "x": x,
                    "y": HEIGHT - GROUND_HEIGHT - height,
                    "width": width,
                    "height": height,
                    "color": color,
                    "speed": speed
                })

            # (Cacti removed) Add small sandy rocks for variety instead
            for i in range(14):
                x = random.randint(0, WIDTH * 2)
                size = random.randint(8, 20)
                color = (170 + random.randint(-10, 10), 140 + random.randint(-10, 10), 110 + random.randint(-10, 10))
                speed = random.uniform(0.12, 0.35)
                self.background_elements.append({
                    "type": "rock",
                    "x": x,
                    "y": HEIGHT - GROUND_HEIGHT - size//2,
                    "size": size,
                    "color": color,
                    "speed": speed
                })

            # Fewer, paler clouds
            for i in range(6):
                x = random.randint(0, WIDTH * 2)
                y = random.randint(40, HEIGHT - GROUND_HEIGHT - 150)
                size = random.randint(30, 60)
                color = (240 + random.randint(-10, 10), 235 + random.randint(-10, 10), 220 + random.randint(-10, 10))
                speed = random.uniform(0.02, 0.1)
                self.background_elements.append({
                    "type": "cloud",
                    "x": x,
                    "y": y,
                    "size": size,
                    "color": color,
                    "speed": speed
                })

    # Layout helpers to keep UI buttons consistently positioned
    def layout_start_menu(self):
        # Use fixed title position and stack all buttons vertically in one centered column
        title_y = 120

        # Uniform button size for tidy, consistent UI (compact)
        btn_w, btn_h = 240, 48
        spacing = 18

        cx = WIDTH // 2
        center_y = title_y + 140

        # START (main) - same size as others for uniformity
        self.play_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.play_button.set_center(cx, center_y)

        # SETTINGS
        center_y += btn_h + spacing
        self.settings_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.settings_button.set_center(cx, int(center_y))

        # HOW TO PLAY
        center_y += btn_h + spacing
        self.tutorial_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.tutorial_button.set_center(cx, int(center_y))

        # EXIT
        center_y += btn_h + spacing
        self.exit_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.exit_button.set_center(cx, int(center_y))

    def layout_settings_menu(self):
        # Use uniform button size (compact)
        btn_w, btn_h = 240, 48
        self.sound_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.fullscreen_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.back_button.rect = pygame.Rect(0, 0, btn_w, btn_h)

        self.sound_button.set_center(WIDTH//2, HEIGHT//2 - 20)
        # Map selector placed between sound and fullscreen
        try:
            self.map_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
            self.map_button.set_center(WIDTH//2, HEIGHT//2 + 20)
        except Exception:
            pass

        self.fullscreen_button.set_center(WIDTH//2, HEIGHT//2 + 60)
        self.back_button.set_center(WIDTH//2, HEIGHT - 100)

    def layout_tutorial_menu(self):
        # Keep tutorial text centered and back/menu buttons at bottom with uniform size
        btn_w, btn_h = 240, 48
        self.back_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.menu_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.back_button.set_center(WIDTH//2 + btn_w//2 + 12, HEIGHT - 100)
        self.menu_button.set_center(WIDTH//2 - btn_w//2 - 12, HEIGHT - 100)

    def layout_game_over_menu(self):
        # Position restart and menu buttons below score with uniform size
        btn_w, btn_h = 240, 48
        self.restart_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.menu_button.rect = pygame.Rect(0, 0, btn_w, btn_h)
        self.restart_button.set_center(WIDTH//2, 420)
        self.menu_button.set_center(WIDTH//2, 500)
    
    def handle_events(self):
        # Ensure layouts are applied before handling input so rects are deterministic
        try:
            if self.game_state == "start_menu":
                self.layout_start_menu()
            elif self.game_state == "settings":
                self.layout_settings_menu()
            elif self.game_state == "tutorial":
                self.layout_tutorial_menu()
            elif self.game_state == "game_over":
                self.layout_game_over_menu()
        except Exception:
            pass

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "start_menu":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.start_game()
                elif self.game_state == "playing":
                    if event.key in [pygame.K_UP, pygame.K_SPACE, pygame.K_w]:
                        # Try double jump first if in air
                        if self.player.jumping and self.player.double_jump():
                            self.play_sound("jump")
                            # Create double jump particle effect
                            for _ in range(25):
                                self.particles.append(Particle(
                                    self.player.rect.centerx,
                                    self.player.rect.centery,
                                    "spark"
                                ))
                        elif not self.player.jumping:
                            self.player.jump()
                            self.play_sound("jump")
                    elif event.key in [pygame.K_p, pygame.K_ESCAPE]:
                        self.paused = not self.paused
                    elif event.key == pygame.K_s:
                        if self.player.activate_shield():
                            self.play_sound("shield")
                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.game_state = "start_menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True

        # store last mouse click for UI elements drawn during draw calls
        self.last_mouse_click = mouse_click

        # Handle button clicks
        if self.game_state == "start_menu":
            self.play_button.update(mouse_pos)
            self.exit_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.tutorial_button.update(mouse_pos)

            if self.play_button.is_clicked(mouse_pos, mouse_click):
                self.start_game()
            elif self.exit_button.is_clicked(mouse_pos, mouse_click):
                self.running = False
            elif self.settings_button.is_clicked(mouse_pos, mouse_click):
                self.game_state = "settings"
            elif self.tutorial_button.is_clicked(mouse_pos, mouse_click):
                self.game_state = "tutorial"

        elif self.game_state == "tutorial":
            # Update tutorial buttons and handle navigation back to menu
            self.back_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                # Go back to previous menu (start menu)
                self.game_state = "start_menu"
            elif self.menu_button.is_clicked(mouse_pos, mouse_click):
                self.game_state = "start_menu"

        elif self.game_state == "settings":
            self.back_button.update(mouse_pos)
            self.sound_button.update(mouse_pos)
            self.fullscreen_button.update(mouse_pos)
            try:
                self.map_button.update(mouse_pos)
            except Exception:
                pass

            if self.sound_button.is_clicked(mouse_pos, mouse_click):
                # Toggle sound
                self.settings["sound"] = not self.settings.get("sound", True)
                vol = 1.0 if self.settings.get("sound") else 0.0
                try:
                    for s in self.sounds.values():
                        s.set_volume(vol)
                except:
                    pass
                self.sound_button.text = "SOUND: ON" if self.settings["sound"] else "SOUND: OFF"

            if self.fullscreen_button.is_clicked(mouse_pos, mouse_click):
                # Toggle fullscreen
                self.settings["fullscreen"] = not self.settings.get("fullscreen", False)
                try:
                    if self.settings["fullscreen"]:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        self.fullscreen_button.text = "FULLSCREEN: ON"
                    else:
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
                        self.fullscreen_button.text = "FULLSCREEN: OFF"
                except:
                    pass

            # Map selection toggle
            try:
                if self.map_button.is_clicked(mouse_pos, mouse_click):
                    current = self.settings.get("map", 0)
                    new = 1 if current == 0 else 0
                    self.settings["map"] = new
                    self.map_button.text = "MAP: DEFAULT" if new == 0 else "MAP: DESERT"
                    # Regenerate background for the new map
                    self.generate_background()
            except Exception:
                pass

            if self.back_button.is_clicked(mouse_pos, mouse_click):
                self.save_settings()
                self.game_state = "start_menu"

        elif self.game_state == "playing":
            # Update pause and jump touch button interactions
            self.pause_button.update(mouse_pos)
            self.jump_touch_button.update(mouse_pos)
            self.shield_button.update(mouse_pos)

            if self.pause_button.is_clicked(mouse_pos, mouse_click):
                self.paused = not self.paused

            if self.jump_touch_button.is_clicked(mouse_pos, mouse_click):
                if not self.paused:
                    self.player.jump()
                    self.play_sound("jump")
            
            if self.shield_button.is_clicked(mouse_pos, mouse_click):
                if not self.paused and self.player.activate_shield():
                    self.play_sound("shield")
            
            # Handle pause menu buttons when paused
            if self.paused:
                self.resume_button.update(mouse_pos)
                self.pause_menu_button.update(mouse_pos)
                
                if self.resume_button.is_clicked(mouse_pos, mouse_click):
                    self.paused = False
                elif self.pause_menu_button.is_clicked(mouse_pos, mouse_click):
                    self.game_state = "start_menu"
                    self.paused = False

        elif self.game_state == "game_over":
            self.restart_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)

            if self.restart_button.is_clicked(mouse_pos, mouse_click):
                self.reset_game()
            elif self.menu_button.is_clicked(mouse_pos, mouse_click):
                self.game_state = "start_menu"
                self.save_settings()
                self.game_state = "start_menu"
        
        elif self.game_state == "game_over":
            self.restart_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
            
            if self.restart_button.is_clicked(mouse_pos, mouse_click):
                self.reset_game()
            elif self.menu_button.is_clicked(mouse_pos, mouse_click):
                self.game_state = "start_menu"
    
    def start_game(self):
        self.game_state = "playing"
        self.player = Player()  # Create fresh player for new game
        self.obstacles = []  # Clear obstacles
        self.asteroids = []  # Clear asteroids
        self.obstacle_timer = 0  # Reset timer
        self.asteroid_timer = 0  # Reset asteroid timer
        self.particles = []  # Clear particles
        self.start_animation_time = pygame.time.get_ticks()
        self.fire_text = None
        self.paused = False
        self.play_sound("start")
    
    def update(self):
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)
        
        # Update fire text
        if self.fire_text:
            self.fire_text.update()
            if not self.fire_text.active:
                self.fire_text = None
        
        # Update background
        for element in self.background_elements:
            element["x"] -= element["speed"] * (self.player.speed / 8)
            if element["x"] < -element.get("width", 50):
                element["x"] = WIDTH + random.randint(100, 500)
                if element["type"] == "light":
                    element["y"] = random.randint(100, HEIGHT - GROUND_HEIGHT - 50)
        
        if self.game_state == "playing" and self.player.state != "dead":
            if self.paused:
                return
            # Update player
            self.player.update()
            
            # Update obstacles
            for obstacle in self.obstacles[:]:
                obstacle.update(self.player.speed)
                if obstacle.x < -obstacle.width:
                    self.obstacles.remove(obstacle)
            
            # Generate new obstacles with variable timing
            self.obstacle_timer += 1
            # Higher base frequency ensures more space between obstacles
            base_freq = max(70, 120 - (self.player.score // 50) * 2)
            # Add random variation (0.7 to 1.6x the base frequency for better spacing)
            random_variation = random.uniform(0.7, 1.6)
            target_freq = int(base_freq * random_variation)
            
            if self.obstacle_timer >= target_freq:
                self.obstacles.append(Obstacle(WIDTH, self.player.speed))
                self.obstacle_timer = 0
            
            # Update asteroids
            for asteroid in self.asteroids[:]:
                asteroid.update()
                # Remove asteroid if it goes below screen
                if asteroid.y > HEIGHT:
                    self.asteroids.remove(asteroid)
            
            # Generate asteroids every 5-6 seconds
            self.asteroid_timer += 1
            asteroid_variation = random.uniform(300, 360)  # 5-6 seconds
            if self.asteroid_timer >= asteroid_variation:
                self.asteroids.append(Asteroid())
                self.asteroid_timer = 0
            
            # Check collisions with obstacles
            for obstacle in self.obstacles:
                if self.player.rect.colliderect(obstacle.rect) and self.player.state not in ["hurt", "dying"]:
                    # If shield is active, destroy obstacle instead
                    if self.player.shield_active:
                        # Create shield effect particles
                        for _ in range(15):
                            self.particles.append(Particle(
                                obstacle.rect.centerx,
                                obstacle.rect.centery,
                                "spark"
                            ))
                    else:
                        # No shield, take damage
                        if self.player.take_damage():
                            # If this was the fatal hit, don't play the hurt sound (die will play later)
                            if self.player.lives > 0:
                                self.play_sound("hurt")
                                # Create hit particles
                                for _ in range(15):
                                    self.particles.append(Particle(
                                        obstacle.rect.centerx,
                                        obstacle.rect.centery,
                                        "spark"
                                    ))
                                for _ in range(8):
                                    self.particles.append(Particle(
                                        obstacle.rect.centerx,
                                        obstacle.rect.centery,
                                        "smoke"
                                    ))
                    break
            
            # Check collisions with asteroids
            for asteroid in self.asteroids[:]:
                if self.player.rect.colliderect(asteroid.rect) and self.player.state not in ["hurt", "dying"]:
                    # If shield is active, destroy asteroid instead
                    if self.player.shield_active:
                        self.asteroids.remove(asteroid)
                        # Create shield effect particles
                        for _ in range(20):
                            self.particles.append(Particle(
                                asteroid.x,
                                asteroid.y,
                                "spark"
                            ))
                    else:
                        # No shield, take damage
                        if self.player.take_damage():
                            if self.player.lives > 0:
                                self.play_sound("hurt")
                                # Create explosion particles
                                for _ in range(20):
                                    self.particles.append(Particle(
                                        asteroid.x,
                                        asteroid.y,
                                        "fire"
                                    ))
                                for _ in range(15):
                                    self.particles.append(Particle(
                                        asteroid.x,
                                        asteroid.y,
                                        "spark"
                                    ))
                        break
            
            # Update score
            for obstacle in self.obstacles:
                if not obstacle.passed and obstacle.x < self.player.x:
                    obstacle.passed = True
                    self.player.score += 1
                    
                    # Play score sound every 10 points
                    if self.player.score % 10 == 0:
                        self.play_sound("score")
                    
                    # Create score particles
                    for _ in range(3):
                        self.particles.append(Particle(
                            self.player.rect.centerx,
                            self.player.rect.top,
                            "spark"
                        ))
            
            # Add heart every 20 points
            if self.player.score > 0 and self.player.score % 20 == 0:
                self.player.add_heart()
                # Create heart particles
                for _ in range(20):
                    self.particles.append(Particle(
                        self.player.rect.centerx,
                        self.player.rect.centery,
                        "fire"
                    ))
            
            # Update best score
            if self.player.score > self.best_score:
                self.best_score = self.player.score
                self.save_best_score()
            
            # Check game over
            if self.player.state == "dead" and self.player.death_animation_complete:
                self.play_sound("die")
                pygame.time.delay(2000)
                self.game_state = "game_over"
    
    def draw_background(self):
        # Nature gradient background (sky)
        map_sel = self.settings.get("map", 0)
        for y in range(HEIGHT):
            # Sky gradient - light blue at top to lighter blue at bottom
            progress = y / HEIGHT
            # Slightly warmer sky for desert map
            if map_sel == 0:
                r = int(135 + progress * 50)  # 135 to 185
                g = int(206 - progress * 30)  # 206 to 176
                b = int(235 - progress * 20)  # 235 to 215
            else:
                r = int(200 + progress * 20)
                g = int(170 + progress * 10)
                b = int(150 + progress * 10)
            pygame.draw.line(self.screen, (r, g, b), 
                           (0, y), (WIDTH, y))
        
        # Draw clouds first (behind mountains and trees)
        for element in self.background_elements:
            if element["type"] == "cloud":
                # Draw fluffy cloud
                cloud_x = element["x"]
                cloud_y = element["y"]
                cloud_size = element["size"]
                
                # Multiple circles for cloud shape
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(cloud_x), int(cloud_y)), cloud_size)
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(cloud_x + cloud_size * 0.6), int(cloud_y - cloud_size * 0.3)), 
                                 int(cloud_size * 0.8))
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(cloud_x - cloud_size * 0.6), int(cloud_y - cloud_size * 0.3)), 
                                 int(cloud_size * 0.8))
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(cloud_x + cloud_size * 1.2), int(cloud_y)), 
                                 int(cloud_size * 0.7))
        
        # Draw mountains
        for element in self.background_elements:
            if element["type"] == "mountain":
                # Draw triangle mountain
                mountain_x = element["x"]
                mountain_y = element["y"]
                mountain_width = element["width"]
                mountain_height = element["height"]
                
                points = [
                    (mountain_x + mountain_width // 2, mountain_y),  # Peak
                    (mountain_x, mountain_y + mountain_height),       # Bottom left
                    (mountain_x + mountain_width, mountain_y + mountain_height)  # Bottom right
                ]
                pygame.draw.polygon(self.screen, element["color"], points)
                
                # Mountain shadow for depth
                shadow_points = [
                    (mountain_x + mountain_width // 2, mountain_y),
                    (mountain_x + mountain_width // 2, mountain_y + mountain_height),
                    (mountain_x + mountain_width, mountain_y + mountain_height)
                ]
                shadow_color = tuple(max(0, c - 30) for c in element["color"])
                pygame.draw.polygon(self.screen, shadow_color, shadow_points)
        
        # Draw trees
        for element in self.background_elements:
            if element["type"] == "tree":
                tree_x = element["x"]
                tree_y = element["y"] + element["height"]
                trunk_width = element["trunk_width"]
                foliage_size = element["foliage_size"]
                
                # Draw trunk
                trunk_rect = pygame.Rect(tree_x - trunk_width // 2, 
                                        tree_y - element["height"] * 0.4,
                                        trunk_width, 
                                        element["height"] * 0.4)
                pygame.draw.rect(self.screen, element["trunk_color"], trunk_rect)
                
                # Draw foliage (tree crown)
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(tree_x), int(tree_y - element["height"] * 0.5)), 
                                 int(foliage_size))
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(tree_x - foliage_size * 0.5), int(tree_y - element["height"] * 0.3)), 
                                 int(foliage_size * 0.7))
                pygame.draw.circle(self.screen, element["color"], 
                                 (int(tree_x + foliage_size * 0.5), int(tree_y - element["height"] * 0.3)), 
                                 int(foliage_size * 0.7))
                
                # Add darker green for shadow effect
                shadow_color = tuple(max(0, c - 20) for c in element["color"])
                pygame.draw.circle(self.screen, shadow_color, 
                                 (int(tree_x + foliage_size * 0.3), int(tree_y - element["height"] * 0.4)), 
                                 int(foliage_size * 0.5))

        # (Cacti removed) draw small rocks for desert map
        for element in self.background_elements:
            if element.get("type") == "rock":
                rx = int(element["x"])
                ry = int(element["y"])
                s = int(element.get("size", 12))
                col = element.get("color", (180, 150, 110))
                # draw a few overlapping ellipses for a rough rock
                pygame.draw.ellipse(self.screen, col, (rx - s, ry - s//2, s * 1.6, s))
                pygame.draw.ellipse(self.screen, tuple(max(0, c - 20) for c in col), (rx - s//2, ry - s//3, s, int(s * 0.7)))
                # small highlight
                pygame.draw.ellipse(self.screen, tuple(min(255, c + 20) for c in col), (rx - s//4, ry - s//4, s//3, s//4))
        
        # Draw ground as grass
        ground_y = HEIGHT - GROUND_HEIGHT
        
        # Grass gradient
        for y in range(GROUND_HEIGHT):
            progress = y / GROUND_HEIGHT
            if map_sel == 0:
                r = int(34 - progress * 10)
                g = int(139 + progress * 20)
                b = int(34 - progress * 5)
            else:
                # Sand gradient for desert map
                r = int(210 - progress * 20)
                g = int(180 - progress * 20)
                b = int(140 - progress * 10)
            pygame.draw.line(self.screen, (r, g, b), 
                           (0, ground_y + y), (WIDTH, ground_y + y))
        
        # Draw grass texture (small blades)
        for i in range(40):
            x = (self.background_offset + i * 30) % WIDTH
            if map_sel == 0:
                # Grass blade
                pygame.draw.line(self.screen, (50, 160, 50), 
                               (x, ground_y + 5), (x + 3, ground_y - 10), 2)
                pygame.draw.line(self.screen, (60, 180, 60), 
                               (x + 5, ground_y), (x + 8, ground_y - 8), 1)
                pygame.draw.line(self.screen, (40, 120, 40), 
                               (x + 10, ground_y + 5), (x + 12, ground_y - 5), 1)
            else:
                # Small sand tufts
                pygame.draw.line(self.screen, (200, 170, 120), 
                               (x, ground_y + 8), (x + 2, ground_y - 4), 2)
                pygame.draw.line(self.screen, (195, 165, 110), 
                               (x + 6, ground_y + 4), (x + 9, ground_y - 2), 1)
    
    def draw_ui(self):
        ticks = pygame.time.get_ticks()

        # ── Score / Best panel (glassmorphism card) ──────────────────────────
        score_card = pygame.Rect(WIDTH - 230, 14, 215, 112)
        draw_glass_panel(self.screen, score_card, bg_color=(10, 10, 28),
                         bg_alpha=210, border_color=(80, 120, 255),
                         border_alpha=200, border_radius=18, border_width=2)

        # Animated neon-cyan score value
        pulse = (math.sin(ticks * 0.004) + 1) * 0.5
        sc_r = int(60 + 80 * pulse)
        sc_g = int(200 + 55 * pulse)
        sc_b = 255
        draw_outlined_text(self.screen, f"{self.player.score:06d}",
                           FONT_MEDIUM, WIDTH - 220, 42,
                           (sc_r, sc_g, sc_b), outline_color=(0, 30, 80), outline=2)

        score_lbl = FONT_TINY.render("SCORE", True, (140, 160, 220))
        self.screen.blit(score_lbl, (WIDTH - 220, 24))

        # Best score in gold
        draw_outlined_text(self.screen, f"BEST: {self.best_score:06d}",
                           FONT_TINY, WIDTH - 220, 88,
                           GOLD, outline_color=(80, 50, 0), outline=1)

        # ── Speed panel ───────────────────────────────────────────────────────
        speed_card = pygame.Rect(WIDTH - 190, 136, 175, 52)
        draw_glass_panel(self.screen, speed_card, bg_color=(8, 18, 30),
                         bg_alpha=200, border_color=(60, 200, 130),
                         border_alpha=160, border_radius=12, border_width=2)

        draw_outlined_text(self.screen,
                           f"SPEED  {self.player.speed:.1f}x",
                           FONT_TINY, WIDTH - 182, 142,
                           GREEN, outline_color=(0, 40, 20), outline=1)

        # Gradient speed bar (green → yellow → orange)
        bar_x = WIDTH - 182
        bar_y = 168
        bar_w = 150
        bar_h = 10
        pygame.draw.rect(self.screen, (30, 40, 50),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        speed_ratio = min(1.0, max(0.0,
            (self.player.speed - self.player.base_speed) / self.player.base_speed))
        fill_w = int(bar_w * speed_ratio)
        if fill_w > 0:
            # Draw gradient bar segment by segment
            for px in range(fill_w):
                seg_t = px / max(1, bar_w)
                bar_r = int(60 + 190 * seg_t)
                bar_g = int(220 - 80 * seg_t)
                bar_b = int(130 - 120 * seg_t)
                pygame.draw.line(self.screen, (bar_r, bar_g, bar_b),
                                 (bar_x + px, bar_y),
                                 (bar_x + px, bar_y + bar_h - 1))
            # Rounded end cap
            pygame.draw.rect(self.screen, (255, 140, 30),
                             (bar_x + fill_w - 4, bar_y, 4, bar_h),
                             border_radius=3)

        # ── Hearts ────────────────────────────────────────────────────────────
        # Background panel for hearts
        hearts_card = pygame.Rect(14, 10, 138, 48)
        draw_glass_panel(self.screen, hearts_card, bg_color=(30, 6, 12),
                         bg_alpha=180, border_color=(200, 60, 80),
                         border_alpha=180, border_radius=12, border_width=2)
        for i in range(3):
            hx = 24 + i * 44
            hy = 14
            heart_size = 30
            if i < self.player.lives:
                # Pulsing alive heart with glow
                pulse_h = (math.sin(ticks * 0.005 + i) + 1) * 0.5
                h_r = int(230 + 25 * pulse_h)
                draw_heart(self.screen, hx, hy, heart_size,
                           (h_r, 55, 75), outline=False)
                inner = int(heart_size * 0.55)
                draw_heart(self.screen, hx + 3, hy + 3, inner,
                           (255, 160, 170), outline=False)
            else:
                draw_heart(self.screen, hx, hy, heart_size,
                           (55, 55, 65), outline=True)

        # ── Double-jump indicator ─────────────────────────────────────────────
        dj_x = WIDTH - 190
        dj_y = 200
        dj_size = 44

        dj_card = pygame.Rect(dj_x - 6, dj_y - 6, dj_size + 30, dj_size + 44)
        if self.player.double_jump_available:
            draw_glass_panel(self.screen, dj_card, bg_color=(5, 20, 50),
                             bg_alpha=190, border_color=(0, 180, 255),
                             border_alpha=210, border_radius=14, border_width=2)
            glow_pulse = (math.sin(ticks * 0.006) + 1) * 0.5
            arrow_color = (int(80 + 80 * glow_pulse), int(200 + 55 * glow_pulse), 255)
            # Two stacked arrow glyphs
            for base_y, tip_y in [(dj_y + 8, dj_y + 2), (dj_y + 20, dj_y + 14)]:
                cx = dj_x + dj_size // 2
                pygame.draw.line(self.screen, arrow_color, (cx, base_y), (cx, tip_y), 2)
                pygame.draw.line(self.screen, arrow_color, (cx - 4, tip_y + 5), (cx, tip_y), 2)
                pygame.draw.line(self.screen, arrow_color, (cx + 4, tip_y + 5), (cx, tip_y), 2)
            dj_label = FONT_TINY.render("2×JUMP", True, arrow_color)
        else:
            draw_glass_panel(self.screen, dj_card, bg_color=(30, 10, 10),
                             bg_alpha=190, border_color=(180, 60, 60),
                             border_alpha=160, border_radius=14, border_width=2)
            cooldown_seconds = self.player.double_jump_cooldown_timer / 60.0
            timer_text = FONT_TINY.render(f"{cooldown_seconds:.1f}s", True, (220, 100, 100))
            self.screen.blit(timer_text, (dj_x + 4, dj_y + 4))
            # Cooldown progress bar
            dj_progress = 1.0 - (self.player.double_jump_cooldown_timer
                                  / self.player.double_jump_cooldown)
            bw, bh = 38, 8
            pygame.draw.rect(self.screen, (60, 30, 30),
                             (dj_x + 3, dj_y + 24, bw, bh), border_radius=3)
            fill_w2 = int(bw * dj_progress)
            if fill_w2 > 0:
                pygame.draw.rect(self.screen, (220, 80, 80),
                                 (dj_x + 3, dj_y + 24, fill_w2, bh), border_radius=3)
            dj_label = FONT_TINY.render("COOLDOWN", True, (200, 80, 80))

        self.screen.blit(dj_label,
                         (dj_x + dj_size // 2 - dj_label.get_width() // 2,
                          dj_y + dj_size + 2))

        # ── FPS (subtle, bottom left) ─────────────────────────────────────────
        fps_text = FONT_TINY.render(f"FPS: {int(self.clock.get_fps()):02d}",
                                    True, (100, 100, 130))
        self.screen.blit(fps_text, (10, HEIGHT - 28))

    def draw_start_menu(self):
        # Draw background
        self.draw_background()

        # Vignette for cinematic depth
        draw_vignette(self.screen, WIDTH, HEIGHT, strength=100)

        # Ambient particles
        for particle in self.particles:
            particle.draw(self.screen)
        if random.random() < 0.35:
            self.particles.append(Particle(
                random.randint(0, WIDTH),
                random.randint(HEIGHT - GROUND_HEIGHT - 120, HEIGHT - GROUND_HEIGHT),
                "fire" if random.random() < 0.3 else "spark"
            ))

        # Title image (floating animation)
        ticks = pygame.time.get_ticks()
        title_y = int(-35 + math.sin(ticks * 0.0012) * 12)
        try:
            title_img = pygame.image.load("title.png")
            title_img = pygame.transform.scale(
                title_img,
                (int(title_img.get_width() * 1.1), int(title_img.get_height() * 1.1))
            )
            self.screen.blit(title_img, (WIDTH // 2 - title_img.get_width() // 2, title_y))
        except:
            # Fallback: outlined + glowing text title
            draw_outlined_text(self.screen, GAME_NAME, FONT_TITLE,
                               WIDTH // 2, title_y + 20,
                               CYAN, outline_color=(0, 40, 80), outline=3, center=True)

        # Player preview (left side, floating bob)
        preview_x = 120
        preview_y = int(HEIGHT // 2 - 55 + math.sin(ticks * 0.002) * 18)
        preview_shadow = pygame.Surface((100, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(preview_shadow, (0, 0, 0, 90), (0, 0, 100, 20))
        self.screen.blit(preview_shadow, (preview_x, HEIGHT - GROUND_HEIGHT - 14))
        frame = int(ticks * 0.008) % len(self.player.animations["running"])
        self.screen.blit(self.player.animations["running"][frame], (preview_x, preview_y))

        # Glass panel behind button column
        self.layout_start_menu()
        btn_rects = [
            self.play_button.rect,
            self.settings_button.rect,
            self.tutorial_button.rect,
            self.exit_button.rect,
        ]
        panel_x = btn_rects[0].x - 16
        panel_y = btn_rects[0].y - 14
        panel_w = btn_rects[0].width + 32
        panel_h = btn_rects[-1].bottom - btn_rects[0].top + 28
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_glass_panel(self.screen, panel_rect, bg_color=(8, 12, 28),
                         bg_alpha=200, border_color=(60, 120, 255),
                         border_alpha=180, border_radius=22, border_width=2)

        self.play_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        self.tutorial_button.draw(self.screen)
        self.exit_button.draw(self.screen)

        # Animated gold best-score badge at bottom
        pulse = (math.sin(ticks * 0.003) + 1) * 0.5
        badge_col = (int(220 + 35 * pulse), int(180 + 35 * pulse), 0)
        badge_rect = pygame.Rect(WIDTH // 2 - 220, HEIGHT - 68, 440, 44)
        draw_glass_panel(self.screen, badge_rect, bg_color=(30, 20, 5),
                         bg_alpha=190, border_color=(200, 160, 20),
                         border_alpha=200, border_radius=14, border_width=2)
        draw_outlined_text(self.screen,
                           f"\u2605  BEST SCORE:  {self.best_score:06d}  \u2605",
                           FONT_SMALL, WIDTH // 2, HEIGHT - 50,
                           badge_col, outline_color=(60, 40, 0), outline=2, center=True)
    
    def draw_game_over(self):
        ticks = pygame.time.get_ticks()

        # Draw game world in background
        self.draw_background()
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.player.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)

        # Dark cinematic overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))
        draw_vignette(self.screen, WIDTH, HEIGHT, strength=160)

        # ── "MISSION FAILED" gradient title ─────────────────────────────────
        g_y = int(120 + math.sin(ticks * 0.002) * 4)
        # Layer multiple red→orange tints for shimmer
        shimmer = (math.sin(ticks * 0.005) + 1) * 0.5
        title_col = (int(220 + 35 * shimmer), int(30 + 60 * shimmer), 40)
        draw_outlined_text(self.screen, "MISSION FAILED", FONT_LARGE,
                           WIDTH // 2, g_y,
                           title_col, outline_color=(60, 0, 0), outline=3, center=True)

        # ── Score card ────────────────────────────────────────────────────────
        card = pygame.Rect(WIDTH // 2 - 220, 195, 440, 100)
        draw_glass_panel(self.screen, card, bg_color=(14, 10, 28),
                         bg_alpha=215, border_color=(160, 80, 220),
                         border_alpha=200, border_radius=20, border_width=2)
        draw_outlined_text(self.screen, f"SCORE   {self.player.score:06d}",
                           FONT_MEDIUM, WIDTH // 2, 215,
                           WHITE, outline_color=(30, 0, 60), outline=2, center=True)

        if self.player.score == self.best_score and self.best_score > 0:
            pulse = (math.sin(ticks * 0.008) + 1) * 0.5
            best_col = (int(220 + 35 * pulse), int(190 + 25 * pulse), 0)
            draw_outlined_text(self.screen, "★  NEW BEST SCORE!  ★",
                               FONT_SMALL, WIDTH // 2, 260,
                               best_col, outline_color=(60, 40, 0), outline=2, center=True)

        # Dead player preview
        dead_y = int(315 + math.sin(ticks * 0.001) * 3)
        if len(self.player.animations["dying"]) > 0:
            dead_frame = min(2, int(ticks * 0.003) % 3)
            self.screen.blit(self.player.animations["dying"][dead_frame],
                             (WIDTH // 2 - 45, dead_y))

        # Buttons
        self.layout_game_over_menu()
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)

    def draw_tutorial(self):
        self.draw_background()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))
        draw_vignette(self.screen, WIDTH, HEIGHT, strength=80)

        # Title
        draw_outlined_text(self.screen, "HOW TO PLAY", FONT_LARGE,
                           WIDTH // 2, 72, CYAN,
                           outline_color=(0, 50, 80), outline=3, center=True)

        # Frosted instruction card
        card = pygame.Rect(WIDTH // 2 - 420, 128, 840, 430)
        draw_glass_panel(self.screen, card, bg_color=(6, 10, 24),
                         bg_alpha=205, border_color=(60, 150, 220),
                         border_alpha=170, border_radius=20, border_width=2)

        # Section 1 – Controls
        controls = [
            (CYAN,   "SPACE / UP / W",   "→  Jump"),
            (CYAN,   "SPACE (in air)",   "→  Double Jump"),
            (GREEN,  "S",                "→  Activate Shield"),
            (ORANGE, "P / ESC",          "→  Pause"),
            (ORANGE, "R",                "→  Restart (game over)"),
            (ORANGE, "M",                "→  Main Menu (game over)"),
        ]
        row_y = 148
        key_x = WIDTH // 2 - 380
        sep_x = WIDTH // 2 - 80
        desc_x = WIDTH // 2 - 70
        for col, key, desc in controls:
            draw_outlined_text(self.screen, key, FONT_SMALL, key_x, row_y,
                               col, outline_color=(0, 20, 40), outline=1)
            draw_outlined_text(self.screen, desc, FONT_SMALL, desc_x, row_y,
                               (220, 220, 235), outline_color=(10, 10, 20), outline=1)
            row_y += 38

        # Divider
        pygame.draw.line(self.screen, (60, 80, 160),
                         (WIDTH // 2 - 380, row_y + 2), (WIDTH // 2 + 380, row_y + 2), 1)
        row_y += 14

        # Section 2 – Tips
        tips = [
            "Gain +1 Heart every 20 points  |  Max 3 hearts",
            "Speed increases 3% every 100 points",
            "Shield (S) blocks one obstacle hit — 10 s cooldown",
        ]
        for tip in tips:
            draw_outlined_text(self.screen, tip, FONT_TINY,
                               WIDTH // 2, row_y, (180, 190, 210),
                               outline_color=(5, 5, 15), outline=1, center=True)
            row_y += 30

        self.layout_tutorial_menu()
        self.back_button.draw(self.screen)

    def draw_pause_overlay(self):
        # Frosted overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 20, 165))
        self.screen.blit(overlay, (0, 0))
        draw_vignette(self.screen, WIDTH, HEIGHT, strength=100)

        # Central glass card
        card = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 280)
        draw_glass_panel(self.screen, card, bg_color=(8, 10, 28),
                         bg_alpha=215, border_color=(100, 140, 255),
                         border_alpha=200, border_radius=22, border_width=2)

        draw_outlined_text(self.screen, "PAUSED", FONT_LARGE,
                           WIDTH // 2, HEIGHT // 2 - 130,
                           WHITE, outline_color=(20, 20, 60), outline=3, center=True)

        self.resume_button.draw(self.screen)
        self.pause_menu_button.draw(self.screen)

        hint = FONT_TINY.render("Press  ESC  or  P  to resume", True, (160, 170, 210))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 120))

    def draw_settings_menu(self):
        self.draw_background()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        self.screen.blit(overlay, (0, 0))
        draw_vignette(self.screen, WIDTH, HEIGHT, strength=80)

        draw_outlined_text(self.screen, "SETTINGS", FONT_LARGE,
                           WIDTH // 2, 90, CYAN,
                           outline_color=(0, 40, 70), outline=3, center=True)

        # Glass card around settings buttons
        self.layout_settings_menu()
        card = pygame.Rect(WIDTH // 2 - 160, HEIGHT // 2 - 60, 320, 240)
        draw_glass_panel(self.screen, card, bg_color=(8, 10, 28),
                         bg_alpha=205, border_color=(70, 130, 220),
                         border_alpha=170, border_radius=20, border_width=2)

        self.sound_button.draw(self.screen)
        try:
            self.map_button.draw(self.screen)
        except Exception:
            pass
        self.fullscreen_button.draw(self.screen)
        self.back_button.draw(self.screen)

        hint = FONT_TINY.render("Toggle options  ·  Press BACK to save",
                                True, (140, 150, 200))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 100))
    
    def draw_playing(self):
        # Draw background
        self.draw_background()
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw UI
        self.draw_ui()
        
       
        
        # Draw fire text animation
        if self.fire_text:
            self.fire_text.draw(self.screen)
        
        # Draw countdown
        current_time = pygame.time.get_ticks()
        if current_time - self.start_animation_time < 4000:
            elapsed = current_time - self.start_animation_time
            
            if elapsed < 1000:  # "3"
                self.draw_countdown("3", elapsed/1000, RED)
            elif elapsed < 2000:  # "2"
                self.draw_countdown("2", (elapsed-1000)/1000, ORANGE)
            elif elapsed < 3000:  # "1"
                self.draw_countdown("1", (elapsed-2000)/1000, GREEN)
            else:  # "GO!"
                self.draw_countdown("GO!", (elapsed-3000)/1000, BLUE)

        # Draw on-screen controls (jump and pause)
        self.jump_touch_button.draw(self.screen)
        self.shield_button.draw(self.screen)
        self.pause_button.draw(self.screen)
        
        # Draw shield indicator
        if self.player.shield_available:
            shield_ready_text = FONT_TINY.render("SHIELD READY", True, (100, 200, 255))
            self.screen.blit(shield_ready_text, (110 - shield_ready_text.get_width()//2, HEIGHT - 260))
        else:
            shield_cooldown = self.player.shield_cooldown_timer / 60.0
            shield_cooldown_text = FONT_TINY.render(f"SHIELD: {shield_cooldown:.1f}s", True, (180, 100, 100))
            self.screen.blit(shield_cooldown_text, (110 - shield_cooldown_text.get_width()//2, HEIGHT - 260))

        # If paused, show overlay
        if self.paused:
            self.draw_pause_overlay()
    
    def draw_countdown(self, text, progress, color):
        # Calculate size with pulse effect
        if progress < 0.8:
            size = 120 - progress * 40
        else:
            size = 80 + math.sin(progress * 20) * 10
        
        # Try to use image if available, otherwise fall back to text
        if text in self.countdown_images:
            # Load and scale the image
            img = self.countdown_images[text]
            scaled_width = int(size * 0.8)
            scaled_height = int(size * 0.8)
            scaled_img = pygame.transform.scale(img, (scaled_width, scaled_height))
            
            # Add glow effect by blitting the image multiple times with reduced alpha
            glow_surf = pygame.Surface((scaled_width + 40, scaled_height + 40), pygame.SRCALPHA)
            
            for i in range(20, 0, -1):
                alpha = int(100 * (1 - i/20))
                glow_img = scaled_img.copy()
                glow_img.set_alpha(alpha)
                glow_surf.blit(glow_img, (20 - i, 20 - i))
            
            self.screen.blit(glow_surf,
                           (WIDTH//2 - scaled_width//2 - 20,
                            HEIGHT//2 - scaled_height//2 - 90))
            
            # Draw main image
            self.screen.blit(scaled_img,
                       (WIDTH//2 - scaled_width//2,
                        HEIGHT//2 - scaled_height//2 - 80))
        else:
            # Fallback to text rendering if image not available
            countdown_font = pygame.font.Font(None, int(size))
            text_surface = countdown_font.render(text, True, color)
            
            # Add glow
            glow_surf = pygame.Surface((text_surface.get_width() + 40, 
                                      text_surface.get_height() + 40), 
                                     pygame.SRCALPHA)
            
            for i in range(20, 0, -1):
                alpha = int(100 * (1 - i/20))
                glow_color = (*color, alpha)
                glow_text = countdown_font.render(text, True, glow_color)
                glow_surf.blit(glow_text, (20 - i, 20 - i))
            
            self.screen.blit(glow_surf, 
                           (WIDTH//2 - text_surface.get_width()//2 - 20,
                            HEIGHT//2 - text_surface.get_height()//2 - 20))
            
            # Draw main text
            self.screen.blit(text_surface, 
                           (WIDTH//2 - text_surface.get_width()//2,
                            HEIGHT//2 - text_surface.get_height()//2))
    
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.asteroids = []
        self.obstacle_timer = 0
        self.asteroid_timer = 0
        self.particles = []
        self.game_state = "playing"
        self.start_animation_time = pygame.time.get_ticks()
        self.fire_text = FireText("JUMPING ENGINEER", WIDTH//2, HEIGHT//2 - 100)
        self.play_sound("start")
    
    def draw(self):
        # Clear screen
        self.screen.fill(BLACK)
        
        if self.game_state == "start_menu":
            self.draw_start_menu()
        elif self.game_state == "settings":
            self.draw_settings_menu()
        elif self.game_state == "tutorial":
            self.draw_tutorial()
        elif self.game_state == "playing":
            self.draw_playing()
        elif self.game_state == "game_over":
            self.draw_game_over()
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()