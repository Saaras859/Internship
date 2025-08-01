import pygame
import random
import math

class PizzaMakerModal:
    def __init__(self, screen_width=1000, screen_height=700):
        pygame.init()
        
        # Constants
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.FPS = 60
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BROWN = (139, 69, 19)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)
        self.LIGHT_BROWN = (210, 180, 140)
        self.DARK_RED = (139, 0, 0)
        self.CHEESE_COLOR = (255, 255, 200)
        self.PEPPERONI_COLOR = (139, 0, 0)
        self.MUSHROOM_COLOR = (160, 82, 45)
        self.PEPPER_COLOR = (34, 139, 34)
        
        # Initialize screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Pizza Making Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game objects
        self.pizza = None
        self.ingredients = []
        self.dragging_ingredient = None
        self.cooking = False
        self.cooking_timer = 0
        self.running = False
        self.finished = False
        
    class Ingredient:
        def __init__(self, x, y, ingredient_type, color, size=20):
            self.x = x
            self.y = y
            self.ingredient_type = ingredient_type
            self.color = color
            self.size = size
            self.dragging = False
            self.on_pizza = False
            self.cooked = False
            self.original_pos = (x, y)
            
        def draw(self, screen):
            color = self.color
            if self.cooked:
                # Darker, more cooked appearance
                color = tuple(max(0, c - 50) for c in color)
                
            if self.ingredient_type == "cheese":
                # Draw cheese as a blob
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, tuple(max(0, c - 30) for c in color), 
                                 (int(self.x), int(self.y)), self.size, 3)
            elif self.ingredient_type == "pepperoni":
                # Draw pepperoni as circle with darker edge
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, tuple(max(0, c - 40) for c in color), 
                                 (int(self.x), int(self.y)), self.size, 2)
            elif self.ingredient_type == "mushroom":
                # Draw mushroom as dome shape
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
                pygame.draw.circle(screen, tuple(max(0, c - 20) for c in color), 
                                 (int(self.x), int(self.y - 5)), self.size - 5)
            elif self.ingredient_type == "pepper":
                # Draw pepper as small rectangles
                pygame.draw.rect(screen, color, 
                               (self.x - self.size//2, self.y - self.size//2, 
                                self.size, self.size//2))
            
        def is_clicked(self, pos):
            distance = math.sqrt((pos[0] - self.x)**2 + (pos[1] - self.y)**2)
            return distance <= self.size
            
        def is_on_pizza(self, pizza_center, pizza_radius):
            distance = math.sqrt((self.x - pizza_center[0])**2 + (self.y - pizza_center[1])**2)
            return distance <= pizza_radius

    class Pizza:
        def __init__(self, center_x, center_y, radius=150):
            self.center_x = center_x
            self.center_y = center_y
            self.radius = radius
            self.cooked = False
            self.cooking_progress = 0
            
        def draw(self, screen, colors):
            # Pizza base (dough)
            base_color = colors['LIGHT_BROWN'] if not self.cooked else (180, 140, 100)
            if self.cooking_progress > 0:
                # Gradually change color while cooking
                cook_factor = min(self.cooking_progress / 100, 1.0)
                base_color = (
                    int(colors['LIGHT_BROWN'][0] - cook_factor * 30),
                    int(colors['LIGHT_BROWN'][1] - cook_factor * 40), 
                    int(colors['LIGHT_BROWN'][2] - cook_factor * 40)
                )
                
            pygame.draw.circle(screen, base_color, (self.center_x, self.center_y), self.radius)
            
            # Pizza crust
            crust_color = colors['BROWN'] if not self.cooked else (100, 50, 20)
            pygame.draw.circle(screen, crust_color, (self.center_x, self.center_y), self.radius, 8)
            
            # Cooking effects
            if self.cooking_progress > 0 and self.cooking_progress < 100:
                # Bubbling effect
                for _ in range(int(self.cooking_progress // 10)):
                    bubble_x = self.center_x + random.randint(-self.radius + 20, self.radius - 20)
                    bubble_y = self.center_y + random.randint(-self.radius + 20, self.radius - 20)
                    bubble_size = random.randint(3, 8)
                    pygame.draw.circle(screen, (255, 255, 255, 100), (bubble_x, bubble_y), bubble_size)

    def setup_ingredients(self):
        # Create ingredient stations
        ingredient_data = [
            ("cheese", self.CHEESE_COLOR, 25),
            ("pepperoni", self.PEPPERONI_COLOR, 20),
            ("mushroom", self.MUSHROOM_COLOR, 18),
            ("pepper", self.PEPPER_COLOR, 15)
        ]
        
        start_x = 50
        start_y = 100
        spacing = 80
        
        for i, (ing_type, color, size) in enumerate(ingredient_data):
            # Create multiple of each ingredient
            for j in range(8):
                x = start_x + (j % 4) * 40
                y = start_y + i * spacing + (j // 4) * 40
                ingredient = self.Ingredient(x, y, ing_type, color, size)
                self.ingredients.append(ingredient)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    
                    # Check if cook button is clicked
                    cook_button_rect = pygame.Rect(self.SCREEN_WIDTH - 150, self.SCREEN_HEIGHT - 80, 120, 50)
                    if cook_button_rect.collidepoint(pos) and not self.cooking:
                        self.start_cooking()
                    
                    # Check if any ingredient is clicked
                    for ingredient in self.ingredients:
                        if ingredient.is_clicked(pos) and not ingredient.on_pizza:
                            ingredient.dragging = True
                            self.dragging_ingredient = ingredient
                            break
                            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_ingredient:
                    # Check if ingredient is dropped on pizza
                    if self.dragging_ingredient.is_on_pizza((self.pizza.center_x, self.pizza.center_y), 
                                                          self.pizza.radius):
                        self.dragging_ingredient.on_pizza = True
                    else:
                        # Return to original position
                        self.dragging_ingredient.x = self.dragging_ingredient.original_pos[0]
                        self.dragging_ingredient.y = self.dragging_ingredient.original_pos[1]
                    
                    self.dragging_ingredient.dragging = False
                    self.dragging_ingredient = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging_ingredient:
                    self.dragging_ingredient.x = event.pos[0]
                    self.dragging_ingredient.y = event.pos[1]
        
        return True
    
    def start_cooking(self):
        self.cooking = True
        self.cooking_timer = 0
        self.pizza.cooking_progress = 0
        
    def update(self):
        if self.cooking:
            self.cooking_timer += 1
            self.pizza.cooking_progress = min((self.cooking_timer / 180) * 100, 100)  # 3 seconds to cook
            
            if self.pizza.cooking_progress >= 100:
                self.cooking = False
                self.pizza.cooked = True
                self.finished = True
                # Mark all ingredients on pizza as cooked
                for ingredient in self.ingredients:
                    if ingredient.on_pizza:
                        ingredient.cooked = True
    
    def draw(self):
        self.screen.fill((50, 150, 50))  # Green kitchen background
        
        # Draw title
        title = self.font.render("Pizza Making Simulator", True, self.WHITE)
        self.screen.blit(title, (self.SCREEN_WIDTH // 2 - title.get_width() // 2, 20))
        
        # Draw ingredient labels
        labels = ["Cheese", "Pepperoni", "Mushrooms", "Peppers"]
        for i, label in enumerate(labels):
            text = self.small_font.render(label, True, self.WHITE)
            self.screen.blit(text, (20, 80 + i * 80))
        
        # Draw pizza
        colors = {
            'LIGHT_BROWN': self.LIGHT_BROWN,
            'BROWN': self.BROWN
        }
        self.pizza.draw(self.screen, colors)
        
        # Draw ingredients
        for ingredient in self.ingredients:
            ingredient.draw(self.screen)
        
        # Draw cook button
        cook_button_rect = pygame.Rect(self.SCREEN_WIDTH - 150, self.SCREEN_HEIGHT - 80, 120, 50)
        button_color = self.RED if not self.cooking else (100, 100, 100)
        pygame.draw.rect(self.screen, button_color, cook_button_rect)
        pygame.draw.rect(self.screen, self.BLACK, cook_button_rect, 2)
        
        button_text = "COOK!" if not self.cooking else f"Cooking {int(self.pizza.cooking_progress)}%"
        text = self.small_font.render(button_text, True, self.WHITE)
        text_rect = text.get_rect(center=cook_button_rect.center)
        self.screen.blit(text, text_rect)
        
        # Draw instructions
        if not any(ing.on_pizza for ing in self.ingredients):
            instruction = self.small_font.render("Drag ingredients onto the pizza!", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        elif not self.pizza.cooked and not self.cooking:
            instruction = self.small_font.render("Click COOK to bake your pizza!", True, self.WHITE)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        elif self.pizza.cooked:
            instruction = self.font.render("🍕 Delicious! Your pizza is ready! 🍕", True, self.YELLOW)
            self.screen.blit(instruction, (self.SCREEN_WIDTH // 2 - instruction.get_width() // 2, self.SCREEN_HEIGHT - 150))
        
        # Draw cooking effects
        if self.cooking:
            # Steam effect
            for _ in range(10):
                steam_x = self.pizza.center_x + random.randint(-50, 50)
                steam_y = self.pizza.center_y - self.pizza.radius - random.randint(10, 40)
                pygame.draw.circle(self.screen, (200, 200, 200, 150), 
                                 (steam_x, steam_y), random.randint(3, 8))
        
        pygame.display.flip()
    
    def run(self):
        # Initialize game objects
        self.pizza = self.Pizza(self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2)
        self.setup_ingredients()
        
        self.running = True
        self.finished = False
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
            
            # Check if we should exit (e.g., when pizza is done)
            if self.finished and pygame.time.get_ticks() > 5000:  # 5 seconds after done
                self.running = False
        
        return self.finished

if __name__ == "__main__":
    game = PizzaMakerModal()
    game.run()