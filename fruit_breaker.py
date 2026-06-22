import pygame
import random
import math


pygame.init()


WIDTH, HEIGHT = 1080, 720
FPS = 60
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)  
RED = (255, 80, 80)
GREEN = (80, 255, 80)
BLUE = (80, 80, 255)
YELLOW = (255, 255, 80)
ORANGE = (255, 165, 0)
PURPLE = (160, 80, 255)

FRUIT_COLORS = [RED, GREEN, YELLOW, ORANGE, PURPLE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fruit Breaker Arcade")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 24, bold=True)
large_font = pygame.font.SysFont("Arial", 48, bold=True)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 6)
        self.life = random.randint(20, 40)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60
        self.y_vel = -1

    def update(self):
        self.y += self.y_vel
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            # Fade out effect
            alpha = max(0, min(255, int(255 * (self.life / 60))))
            txt_surf = font.render(self.text, True, self.color)
            # Create a surface with alpha support
            alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, alpha))
            txt_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(txt_surf, (self.x, self.y))

class Paddle:
    def __init__(self):
        self.width = 120
        self.height = 20
        self.x = (WIDTH - self.width) // 2
        self.y = HEIGHT - 50
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.color = (100, 200, 255)

    def move(self, dx):
        self.x += dx
        # Clamp to screen
        if self.x < 0: self.x = 0
        if self.x + self.width > WIDTH: self.x = WIDTH - self.width
        self.rect.x = int(self.x)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        # Add a shine effect
        pygame.draw.rect(surface, (200, 230, 255), (self.rect.x + 10, self.rect.y + 5, self.width - 20, 5), border_radius=5)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sound("wall", "hit_wall.wav")
        self.load_sound("paddle", "hit_paddle.wav")
        self.load_sound("fruit", "hit_fruit.wav")
        self.load_sound("level_clear", "level_clear.wav")

    def load_sound(self, name, filename):
        try:
            self.sounds[name] = pygame.mixer.Sound(filename)
            self.sounds[name].set_volume(0.4)
        except:
            print(f"Warning: Could not load sound {filename}")
            self.sounds[name] = None

    def play(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()

class Ball:
    def __init__(self, x, y, speed=6, sound_manager=None):
        self.radius = 10
        self.x = x
        self.y = y
        self.speed = speed
        self.sound_manager = sound_manager
        angle = random.uniform(-math.pi/4, math.pi/4) - math.pi/2 # Upwards cone
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.active = True
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        self.trail = []
        self.color = WHITE
        
    def reset(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(-math.pi/4, math.pi/4) - math.pi/2
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.active = False
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)
        self.trail = []

    def move(self):
        if not self.active:
            return
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

        # Wall Collisions
        hit_wall = False
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -1
            self.color = (255, 100, 100) # Red-ish
            hit_wall = True
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -1
            self.color = (100, 100, 255) # Blue-ish
            hit_wall = True
        
        if self.y - self.radius < 0:
            self.y = self.radius
            self.vy *= -1
            self.color = (100, 255, 100) # Green-ish
            hit_wall = True
            
        if hit_wall and self.sound_manager:
            self.sound_manager.play("wall")

    def draw(self, surface):
        # Draw Trail
        for i, (tx, ty) in enumerate(self.trail):
            size = int(self.radius * (i / len(self.trail)))
            # Fade current color
            fade = i / len(self.trail)
            c = (int(self.color[0] * fade), int(self.color[1] * fade), int(self.color[2] * fade))
            pygame.draw.circle(surface, c, (int(tx), int(ty)), size)

        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

class Fruit:
    def __init__(self, x, y, color):
        self.width = 60
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = color
        self.active = True

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
            # "Shine"
            pygame.draw.circle(surface, (255, 255, 255, 100), (self.rect.x + 10, self.rect.y + 10), 3)

def create_level(level):
    fruits = []
    rows = 4 + level  # Increase rows with level
    cols = 10
    padding = 10
    start_x = (WIDTH - (cols * (60 + padding))) // 2
    start_y = 50

    for r in range(rows):
        for c in range(cols):
            x = start_x + c * (60 + padding)
            y = start_y + r * (30 + padding)
            color = FRUIT_COLORS[r % len(FRUIT_COLORS)]
            fruits.append(Fruit(x, y, color))
    return fruits

    return fruits

def apply_difficulty(level, balls, paddle):
    # Increase ball speed
    base_speed = 6 + (level - 1) * 0.8
    for b in balls:
        b.speed = base_speed
    
    # Increase paddle speed
    paddle.speed = 8 + (level - 1) * 1.0
    
    # Decrease paddle width (min 60)
    paddle.width = max(60, 120 - (level - 1) * 10)
    paddle.rect.width = paddle.width
    print(f"Level {level}: Ball Speed {base_speed}, Paddle Speed {paddle.speed}, Paddle Width {paddle.width}")

def main():
    # Real display surface
    display_surface = pygame.display.get_surface()
    # Virtual canvas for shaking
    canvas = pygame.Surface((WIDTH, HEIGHT))
    
    paddle = Paddle()
    balls = [Ball(WIDTH // 2, HEIGHT // 2 + 100)]
    balls[0].active = False # Start inactive
    particles = []
    texts = []
    
    # Shake variables
    shake_duration = 0
    shake_magnitude = 0
    
    # Combo variables
    combo_count = 0
    combo_timer = 0
    
    # Falling Fruits
    fall_timer = 0
    FALL_INTERVAL = 300 # 5 seconds at 60 FPS
    
    # Multiball tracker
    bricks_broken_total = 0

    # Audio
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("background.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except Exception as e:
        print(f"Music not found or error: {e}")

    sound_manager = SoundManager()

    level = 1
    score = 0
    lives = 3
    fruits = create_level(level)
    
    # Initialize balls with sound manager
    balls = [Ball(WIDTH // 2, HEIGHT // 2 + 100, sound_manager=sound_manager)]
    balls[0].active = False
    
    apply_difficulty(level, balls, paddle)
    
    running = True
    game_over = False
    
    while running:
        clock.tick(FPS)
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Launch all inactive balls
                    launched = False
                    for b in balls:
                        if not b.active and not game_over:
                            b.active = True
                            b.vy = -abs(b.speed)
                            launched = True
                    
                    if game_over:
                        # Restart
                        level = 1
                        score = 0
                        lives = 3
                        bricks_broken_total = 0
                        fruits = create_level(level)
                        balls = [Ball(WIDTH // 2, HEIGHT // 2 + 100, sound_manager=sound_manager)]
                        balls[0].active = False
                        apply_difficulty(level, balls, paddle)
                        game_over = False

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle.move(-paddle.speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle.move(paddle.speed)

        if not game_over:
            # Updates
            
            # Falling Fruits Logic
            fall_timer += 1
            if fall_timer >= FALL_INTERVAL:
                fall_timer = 0
                for f in fruits:
                    f.rect.y += 10
                    # Check Game Over
                    if f.rect.bottom >= paddle.rect.top:
                        game_over = True
            
            # Move Balls
            for ball in balls:
                ball.move()
                
                # Paddle Collision
                if ball.rect.colliderect(paddle.rect) and ball.vy > 0:
                    sound_manager.play("paddle")
                    # Calculate hit position relative to center
                    hit_pos = (ball.x - (paddle.x + paddle.width/2)) / (paddle.width/2)
                    # Bounce angle based on hit position
                    bounce_angle = hit_pos * (math.pi/3) # Max 60 degrees
                    speed = math.sqrt(ball.vx**2 + ball.vy**2)
                    ball.vx = speed * math.sin(bounce_angle)
                    ball.vy = -speed * math.cos(bounce_angle)
                    
                    # Ensure it moves up
                    if ball.vy > -2: ball.vy = -2

                # Fruit Collision
                hit_index = ball.rect.collidelist([f.rect for f in fruits if f.active])
                if hit_index != -1:
                    sound_manager.play("fruit")
                    # Find the actual fruit object
                    active_fruits = [f for f in fruits if f.active]
                    hit_fruit = active_fruits[hit_index]
                    hit_fruit.active = False
                    
                    # Combo Logic
                    combo_count += 1
                    combo_timer = 60 # 1 second to keep combo
                    points = 10 * combo_count
                    score += points
                    bricks_broken_total += 1
                    
                    # Multiball Spawn
                    if bricks_broken_total % 10 == 0:
                        new_ball = Ball(ball.x, ball.y, ball.speed, sound_manager=sound_manager)
                        new_ball.vx = -ball.vx
                        new_ball.vy = ball.vy
                        balls.append(new_ball)
                        texts.append(FloatingText(ball.x, ball.y - 40, "MULTIBALL!", GREEN))
                    
                    # Floating Text
                    texts.append(FloatingText(hit_fruit.rect.centerx, hit_fruit.rect.y, f"+{points}", WHITE))
                    if combo_count > 1:
                        texts.append(FloatingText(hit_fruit.rect.centerx, hit_fruit.rect.y - 20, f"{combo_count}x COMBO!", YELLOW))

                    # Screen Shake
                    shake_duration = 5 + min(combo_count, 10)
                    shake_magnitude = 3 + min(combo_count, 5)
                    
                    # Physics bounce
                    # Simple bounce: reverse Y if hitting top/bottom, X if hitting sides
                    # For simplicity in this grid, just reversing Y often works, but let's be slightly smarter
                    # Check overlap
                    overlap_rect = ball.rect.clip(hit_fruit.rect)
                    if overlap_rect.width > overlap_rect.height:
                        ball.vy *= -1
                    else:
                        ball.vx *= -1
                    
                    # Spawn particles
                    for _ in range(10):
                        particles.append(Particle(hit_fruit.rect.centerx, hit_fruit.rect.centery, hit_fruit.color))

            # Level Clear
            if all(not f.active for f in fruits):
                sound_manager.play("level_clear")
                level += 1
                # Reset balls to one
                balls = [Ball(WIDTH // 2, HEIGHT // 2 + 100, sound_manager=sound_manager)]
                balls[0].active = False
                apply_difficulty(level, balls, paddle)
                fruits = create_level(level)
                # Bonus score
                score += 100
                fall_timer = 0

            # Ball Lost
            # Remove dead balls
            balls = [b for b in balls if b.y <= HEIGHT]
            
            if len(balls) == 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    balls = [Ball(WIDTH // 2, HEIGHT // 2 + 100, sound_manager=sound_manager)]
                    balls[0].active = False

            # Particles
            for p in particles[:]:
                p.update()
                if p.life <= 0:
                    particles.remove(p)
                    
            # Floating Text
            for t in texts[:]:
                t.update()
                if t.life <= 0:
                    texts.remove(t)
            
            # Update Combo Timer
            if combo_timer > 0:
                combo_timer -= 1
            else:
                combo_count = 0

        # Draw to Canvas
        canvas.fill(BLACK)
        
        paddle.draw(canvas)
        for ball in balls:
            ball.draw(canvas)
        for f in fruits:
            f.draw(canvas)
        for p in particles:
            p.draw(canvas)
        for t in texts:
            t.draw(canvas)

        # UI
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        canvas.blit(score_text, (10, 10))
        canvas.blit(level_text, (WIDTH//2 - 40, 10))
        canvas.blit(lives_text, (WIDTH - 100, 10))

        if any(not b.active for b in balls) and not game_over:
            start_text = font.render("Press SPACE to Start", True, WHITE)
            canvas.blit(start_text, (WIDTH//2 - 100, HEIGHT//2 + 50))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            canvas.blit(overlay, (0, 0))
            
            go_text = large_font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press SPACE to Restart", True, WHITE)
            
            canvas.blit(go_text, (WIDTH//2 - 120, HEIGHT//2 - 50))
            canvas.blit(final_score_text, (WIDTH//2 - 80, HEIGHT//2 + 10))
            canvas.blit(restart_text, (WIDTH//2 - 110, HEIGHT//2 + 50))

        # Apply Shake and Blit to Screen
        shake_offset = (0, 0)
        if shake_duration > 0:
            shake_offset = (random.randint(-shake_magnitude, shake_magnitude), random.randint(-shake_magnitude, shake_magnitude))
            shake_duration -= 1
            
        display_surface.fill(BLACK) # Clear borders
        display_surface.blit(canvas, shake_offset)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
