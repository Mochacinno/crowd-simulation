import pygame
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Procedural Fish Outline")

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
WHITE = (255, 255, 255)

# Clock for controlling the frame rate
clock = pygame.time.Clock()

# Fish properties
SEGMENT_RADIUS = 15
SEGMENT_SPACING = 25
NUM_SEGMENTS = 10
LEAD_SPEED = 5

# Fish segments (x, y positions)
segments = [(WIDTH // 2, HEIGHT // 2) for _ in range(NUM_SEGMENTS)]

# Function to update fish segments
def update_segments(segments, target_x, target_y):
    # Update the lead segment to the target position
    segments[0] = (target_x, target_y)

    # Update each subsequent segment to follow the one in front
    for i in range(1, len(segments)):
        prev_x, prev_y = segments[i - 1]
        curr_x, curr_y = segments[i]

        # Calculate direction to the previous segment
        dx = prev_x - curr_x
        dy = prev_y - curr_y
        distance = math.hypot(dx, dy)

        # Move the current segment towards the previous one
        if distance > SEGMENT_SPACING:
            angle = math.atan2(dy, dx)
            curr_x += math.cos(angle) * (distance - SEGMENT_SPACING)
            curr_y += math.sin(angle) * (distance - SEGMENT_SPACING)
            segments[i] = (curr_x, curr_y)

# Function to calculate tangent points
def calculate_tangent_points(segments, radius):
    left_points = []
    right_points = []

    for i in range(len(segments)):
        cx, cy = segments[i]

        if i == 0:
            # First circle, no previous segment
            next_x, next_y = segments[i + 1]
            angle = math.atan2(next_y - cy, next_x - cx)
        elif i == len(segments) - 1:
            # Last circle, no next segment
            prev_x, prev_y = segments[i - 1]
            angle = math.atan2(cy - prev_y, cx - prev_x)
        else:
            # Middle segments
            prev_x, prev_y = segments[i - 1]
            next_x, next_y = segments[i + 1]
            angle_prev = math.atan2(cy - prev_y, cx - prev_x)
            angle_next = math.atan2(next_y - cy, next_x - cx)
            angle = (angle_prev + angle_next) / 2

        # Tangent points
        left_angle = angle + math.pi / 2
        right_angle = angle - math.pi / 2

        left_points.append((cx + radius * math.cos(left_angle), cy + radius * math.sin(left_angle)))
        right_points.append((cx + radius * math.cos(right_angle), cy + radius * math.sin(right_angle)))

    return left_points, right_points

# Function to draw the fish outline
def draw_fish_outline(surface, left_points, right_points):
    # Draw the outline by connecting the left and right points
    if left_points and right_points:
        pygame.draw.lines(surface, BLUE, False, left_points, width=2)
        pygame.draw.lines(surface, BLUE, False, right_points[::-1], width=2)

# Function to draw a parametric circle
def draw_circle_parametric(surface, color, center, radius):
    cx, cy = center
    points = [
        (int(cx + radius * math.cos(t)), int(cy + radius * math.sin(t)))
        for t in [i * 0.1 for i in range(63)]  # 0 to 2π in 0.1 increments
    ]
    pygame.draw.polygon(surface, color, points, width=1)

# Main loop
running = True
lead_x, lead_y = WIDTH // 2, HEIGHT // 2

while running:
    screen.fill(BLACK)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get key presses for movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        lead_y -= LEAD_SPEED
    if keys[pygame.K_DOWN]:
        lead_y += LEAD_SPEED
    if keys[pygame.K_LEFT]:
        lead_x -= LEAD_SPEED
    if keys[pygame.K_RIGHT]:
        lead_x += LEAD_SPEED

    # Update the positions of the fish segments
    update_segments(segments, lead_x, lead_y)

    # Calculate tangent points for the fish outline
    left_points, right_points = calculate_tangent_points(segments, SEGMENT_RADIUS)

    # Draw the fish circles
    for i, (x, y) in enumerate(segments):
        color = BLUE if i == 0 else WHITE  # Head is blue, body is white
        draw_circle_parametric(screen, color, (x, y), SEGMENT_RADIUS)

    # Draw the fish outline
    draw_fish_outline(screen, left_points, right_points)

    # Update the display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
