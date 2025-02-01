import pygame
import random
import math

# Window settings
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (30, 30, 47)

#DEFAULT SETTINGS
# NUM_BOIDS = 80
# BOID_SIZE = 3
# MAX_SPEED = 4
# MAX_FORCE = 0.1

# Boid settings
NUM_BOIDS = 80
BOID_SIZE = 3
MAX_SPEED = 3
MAX_FORCE = 0.1
VIEW_RADIUS = 50
MOUSE_RADIUS = 150  # Distance at which boids will react to the mouse
REPEL_MOUSE = True

# Menu settings
FONT_SIZE = 20
MENU_OFFSET = 10  # Distance from the left edge
SPACING = 30  # Spacing between menu items

class Boid:
    def __init__(self):
        self.position = pygame.Vector2(random.randint(0, WIDTH), random.randint(0, HEIGHT))
        angle = random.uniform(0, 2 * math.pi)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * MAX_SPEED
        self.acceleration = pygame.Vector2(0, 0)
        
    def update(self):
        self.velocity += self.acceleration
        if self.velocity.length() > MAX_SPEED:
            self.velocity.scale_to_length(MAX_SPEED)
        self.position += self.velocity
        self.acceleration *= 0  # Reset acceleration after each frame
        
        # Wrap around screen edges
        if self.position.x > WIDTH: self.position.x = 0
        if self.position.x < 0: self.position.x = WIDTH
        if self.position.y > HEIGHT: self.position.y = 0
        if self.position.y < 0: self.position.y = HEIGHT

    def apply_force(self, force):
        self.acceleration += force

    def flock(self, boids, mouse_pos):
        alignment = pygame.Vector2(0, 0)
        cohesion = pygame.Vector2(0, 0)
        separation = pygame.Vector2(0, 0)
        total = 0
        
        SEPARATION_RADIUS = 20

        for other in boids:
            distance = self.position.distance_to(other.position)
            if other != self:
                if distance < SEPARATION_RADIUS:
                    # Apply a stronger separation force within a closer range
                    separation += (self.position - other.position) / distance
                if distance < VIEW_RADIUS:
                    # Apply alignment and cohesion within the regular view radius
                    alignment += other.velocity
                    cohesion += other.position
                    total += 1

        if total > 0:
            # Alignment
            alignment /= total
            alignment.scale_to_length(MAX_SPEED)
            alignment -= self.velocity
            if alignment.length() > MAX_FORCE:
                alignment.scale_to_length(MAX_FORCE)
            self.apply_force(alignment)
            
            # Cohesion
            cohesion /= total
            cohesion -= self.position
            cohesion.scale_to_length(MAX_SPEED)
            cohesion -= self.velocity
            if cohesion.length() > MAX_FORCE:
                cohesion.scale_to_length(MAX_FORCE)
            self.apply_force(cohesion)
            
            # Separation
            if total > 0:
                separation /= total
                if separation.length() > 0:  # Check after division to avoid zero-length scaling
                    separation.scale_to_length(MAX_SPEED)
                    separation -= self.velocity
                    separation *= 1.5  # Increase separation weight
                    if separation.length() > MAX_FORCE * 2:  # Higher max force for separation
                        separation.scale_to_length(MAX_FORCE * 2)
                    self.apply_force(separation)
        # Repel from the mouse
        self.repel_from_mouse(mouse_pos)

    def repel_from_mouse(self, mouse_pos):
        mouse_vector = pygame.Vector2(mouse_pos)
        distance_to_mouse = self.position.distance_to(mouse_vector)
        if distance_to_mouse < MOUSE_RADIUS:
            # Calculate the repelling force direction and magnitude
            if(REPEL_MOUSE):
                repel_force = self.position - mouse_vector
            else:
                repel_force = mouse_vector - self.position
            repel_force.scale_to_length(MAX_SPEED)
            repel_force -= self.velocity
            if repel_force.length() > MAX_FORCE:
                repel_force.scale_to_length(MAX_FORCE)
            self.apply_force(repel_force)

    def draw(self, screen):
        # Calculate angle based on velocity direction
        angle = math.atan2(self.velocity.y, self.velocity.x)
        wiggle = 2
        # Define triangle points with a bit of "wiggle" for each frame
        point1 = self.position + pygame.Vector2(math.cos(angle), math.sin(angle)) * BOID_SIZE * 2
        point2 = self.position + pygame.Vector2(math.cos(angle + wiggle), math.sin(angle + wiggle)) * BOID_SIZE
        point3 = self.position + pygame.Vector2(math.cos(angle - wiggle), math.sin(angle - wiggle)) * BOID_SIZE

        # Add a slight random offset to make the points "wiggle"
        wiggle_amount = 1.5
        point2 += pygame.Vector2(random.uniform(-wiggle_amount, wiggle_amount), random.uniform(-wiggle_amount, wiggle_amount))
        point3 += pygame.Vector2(random.uniform(-wiggle_amount, wiggle_amount), random.uniform(-wiggle_amount, wiggle_amount))

        # Draw the wiggly triangle
        pygame.draw.polygon(screen, (200, 200, 255), [point1, point2, point3])

def draw_menu(screen, font, selected_index, parameters):
    for i, (param, value) in enumerate(parameters.items()):
        color = (255, 255, 255) if i == selected_index else (150, 150, 150)
        text_surface = font.render(f"{param}: {value}", True, color)
        screen.blit(text_surface, (MENU_OFFSET, MENU_OFFSET + i * SPACING))

def main():
    global VIEW_RADIUS, MOUSE_RADIUS, MAX_SPEED  # Make parameters global for updates
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Boids Simulation")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, FONT_SIZE)
    
    # Create boids
    boids = [Boid() for _ in range(NUM_BOIDS)]

    # Parameters to adjust with menu
    parameters = {"VIEW_RADIUS": VIEW_RADIUS, "MOUSE_RADIUS": MOUSE_RADIUS}#, "MAX_SPEED":MAX_SPEED
    param_keys = list(parameters.keys())
    selected_index = 0  # Index of currently selected parameter in the menu
    
    running = True
    while running:
        screen.fill(BACKGROUND_COLOR)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(param_keys)
                elif event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(param_keys)
                elif event.key == pygame.K_RIGHT:
                    parameters[param_keys[selected_index]] += 10
                elif event.key == pygame.K_LEFT:
                    parameters[param_keys[selected_index]] -= 10

        # Update global parameters with current values from menu
        VIEW_RADIUS = parameters["VIEW_RADIUS"]
        MOUSE_RADIUS = parameters["MOUSE_RADIUS"]
        # MAX_SPEED = parameters["MAX_SPEED"]

        # Get the mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Update and draw each boid
        for boid in boids:
            boid.flock(boids, mouse_pos)
            boid.update()
            #pygame.draw.circle(screen, (100, 255, 255), (int(boid.position.x), int(boid.position.y)), BOID_SIZE)
            boid.draw(screen)  # Draw boid as a wiggly triangle

        # Draw parameter adjustment menu
        draw_menu(screen, font, selected_index, parameters)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
