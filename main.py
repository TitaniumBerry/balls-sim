import pygame
import math
import random


colors = {"Red":(255, 0, 0), "Green":(0, 255, 0), "Blue":(0, 0, 255), 
          "Black":(0, 0, 0), "White":(255, 255, 255), "LightBlue":(0, 128, 255),
          "Pink":(255, 0, 255)}

keytype = {"wasd":(pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d), 
           "uldr":(pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN, pygame.K_RIGHT)}
window_dimensions = (1320, 680)
fps = 120
particles = []




def distance(c1, c2):
    return(math.sqrt(((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)))


def pygame_initilisation():        
    (pypass, pyfail) = pygame.init()
    print(f"arguments passed = {pypass}")
    print(f"argument failed = {pyfail}")
    print("-----------------")
    print(f"Pygame initialised: {pygame.get_init()}")
    if pygame.get_init() != True:
        pygame.init()
    pygame.font.init()
    print(f"Pygame font initialised: {pygame.font.get_init()}")
    print("-----------------")
    pygame.mixer.init()
    print(f"Pygame mixer initialised: {pygame.mixer.get_init()}")
    print("-----------------")

    # just for icon
    global mushroom
    mushroom = pygame.image.load("mushroom.jpg")



def window_set():

    window = pygame.display.set_mode((window_dimensions[0], window_dimensions[1]))
    pygame.display.set_caption("i can't think of a title")
    pygame.display.set_icon(mushroom)
    clock = pygame.time.Clock()
    running = True
    [x, y] = [400, 400]

    # sounds
    pop = pygame.mixer.Sound("pop.wav")
    thud = pygame.mixer.Sound("thud.wav")
    fullscreen = False
    

    class Speed:
        def __init__(self):
            self.x = 0
            self.y = 0
    
    class Offset:
        def __init__(self):
            self.x = 0
            self.y = 0

    class Particles:
        def __init__(self, x, y, color):
            self.x = x
            self.y = y
            self.radius = random.randint(1, 3)
            self.color = color
            self.life = 10

            angle = random.uniform(0, 2*(math.pi))
            speed = random.uniform(2, 5)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed

        def update(self):
            self.x += self.vx
            self.y += self.vy
            self.life -= 1
            self.radius = max((1, self.radius - 0.1))

        def draw(self, window):
            if self.life > 0:

                # fade
                alpha = max(0, int((self.life / 10) * 255))             
                glow_radius = int(self.radius * 3.5)
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(
                    glow_surf,
                    (*self.color, alpha),
                    (self.radius * 2, self.radius * 2),
                    int(self.radius * 2)
                )
                window.blit(glow_surf,
                            (self.x - self.radius * 2,self.y - self.radius * 2))
                
                # circle on top
                pygame.draw.circle(window, self.color, 
                                (int(self.x), int(self.y)), int(self.radius))
                
    def collision(ball1, ball2):
        
        bounce = 0.5

        dis_x = ball2.x - ball1.x
        dis_y = ball2.y - ball1.y
        dis_xy = math.sqrt((dis_x)**2 + (dis_y)**2)
        min_dis = ball1.radius + ball2.radius
        
        if dis_xy == 0:
            dis_xy = 0.000001

        if dis_xy < min_dis:
            # normal vectors
            n_x = dis_x / dis_xy
            n_y = dis_y / dis_xy


            # push apart to avoid bug
            overlap = min_dis - dis_xy
            push_x = (overlap / 2) * n_x
            push_y = (overlap / 2) * n_y

            ball1.x -= push_x
            ball1.y -= push_y
            ball2.x += push_x
            ball2.y += push_y

            # hard hit
            dv_x = ball2.velocity.x - ball1.velocity.x
            dv_y = ball2.velocity.y - ball1.velocity.y

            impact_vel = (dv_x * n_x) + (dv_y * n_y)

            if impact_vel > 0:
                return
            
            # playnig pop
            pop.play()

            for _ in range(random.randint(1, 3)):

                # midpoint particles

                splash_x = (ball1.x + ball2.x)/2
                splash_y = (ball1.y + ball2.y)/2
                if ball1 == balls[0] or ball2 == balls[0]:
                    avg_color = colors["Pink"]
                else:
                     avg_color = ((ball1.color[0] + ball2.color[0])/2,
                             (ball1.color[1] + ball2.color[1])/2,
                             (ball1.color[2] + ball2.color[2])/2)
                    
                angle_var = random.uniform(-0.5, 0.5)

                # angle flip
                base_angle = math.atan2(n_y, n_x) + math.pi

                final_angle = base_angle + angle_var
                speed = random.uniform(2, 5)
                vx = math.cos(final_angle) * speed
                vy = math.sin(final_angle) * speed  
                pp = Particles(splash_x, splash_y, avg_color)
                pp.vx = vx
                pp.vy = vy
        
                particles.append(pp)

            # apply impulse
            impulse = (1 + bounce) * impact_vel
            ball1.velocity.x += impulse * n_x
            ball2.velocity.x -= impulse * n_x
            ball1.velocity.y += impulse * n_y
            ball2.velocity.y -= impulse * n_y

            ball1.collisions += 1
            ball2.collisions += 1



    class Ball:

        def __init__(self, x, y, radius = 40, color = colors["LightBlue"]):
            self.x = x
            self.y = y
            self.radius = radius
            self.velocity = Speed()
            self.is_dragging = False
            self.drag_offset = Offset()
            self.base_color = color
            self.color = color
            self.on_ground = False
            self.moving_left = False
            self.moving_right = False
            self.prev_pos = None
            self.collisions = 0
            self.base_color = color

        def glow(self, window):
            glow_color = self.color
            glow_layers = 6
            
            # glow fade
            for i in range(glow_layers, 0, -1):
                radius = int(self.radius + 1 * 4)
                alpha = max (5, (25 - i * 3))
                glow_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*glow_color, alpha), (radius, radius),
                                   radius)
                window.blit(glow_surf, (self.x - radius, self.y - radius))



        # main update
        def update(self, window):

            # drag conditions
            if self.is_dragging:
                mouse_pos = pygame.mouse.get_pos()
                if self.prev_pos:
                    self.velocity.x = mouse_pos[0] - self.prev_pos[0]
                    self.velocity.y = mouse_pos[1] - self.prev_pos[1]

                self.prev_pos = mouse_pos
                self.x = mouse_pos[0] + self.drag_offset.x
                self.y = mouse_pos[1] + self.drag_offset.y
                
            else:

                # jump conditions 
                if self.y >= (window.get_height() - 50 - self.radius):
                    
                    # invert y vel 
                    self.velocity.y = -(self.velocity.y * restitution_coeff)
                    
                    # particles on ground collision 
                    if abs(self.velocity.y) > 1:
                        for _ in range(random.randint(1, 3)):
                            splash_x = self.x
                            splash_y = self.y + self.radius
                            particles.append(Particles(splash_x, splash_y, colors["White"]))

                    self.on_ground = True

                else:
                    self.on_ground = False

                keys = pygame.key.get_pressed()

                if self.on_ground and (keys[keytype["wasd"][0]] or keys[keytype["uldr"][0]] 
                                       or keys[pygame.K_SPACE]):
                    self.velocity.y -= jump_strength

                        

                # gravity 
                self.velocity.y += g

                # left right movement 
                if self.moving_left:
                    self.velocity.x -= accn
                if self.moving_right:
                    self.velocity.x += accn

                # friction 
                if not self.moving_left and not self.moving_right:
                    if abs(self.velocity.x) < friction:
                        self.velocity.x = 0
                    elif self.velocity.x > 0:
                        self.velocity.x -= friction
                    elif self.velocity.x < 0:
                        self.velocity.x += friction

                # velocity bounds 
                self.velocity.x = max(-(max_speed_x), min(self.velocity.x, max_speed_x))
                self.velocity.y = max(-(max_speed_y), min(self.velocity.y, max_speed_y))

                # position update 
                self.x += self.velocity.x
                self.y += self.velocity.y
        
            # position bounds 
            self.x = max(self.radius, min(self.x, (window.get_width() - self.radius)))
            self.y = max(0, min(self.y, (window.get_height() - 50 - self.radius)))
            
            # collision bounds 
            if (self.x <= self.radius) or (self.x >= (window.get_width() - self.radius)):
                self.velocity.x = -((self.velocity.x * restitution_coeff))
            if self.y <= 0:
                self.velocity.y = -((self.velocity.y * restitution_coeff))
            
            
            self.glow(window)

            pygame.draw.circle(window, self.color, (self.x, self.y), self.radius)

            
        
        

            

    # first ball                             
    balls = [Ball(x, y, color = colors["Pink"])]
                
    # movement variables 
    accn = 0.5
    max_speed_x = 15
    max_speed_y = 50
    friction = 0.165
    g = 0.3
    jump_strength = 10
    restitution_coeff = 0.5
    slowmo = False

    fade_surface = pygame.Surface(window.get_size(), pygame.SRCALPHA)
    def update_fade_surface():
        nonlocal fade_surface
        fade_surface = pygame.Surface(window.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 45))

    update_fade_surface()

    
    while running:
        
        window.blit(fade_surface, (0, 0))
        
        ground = pygame.draw.rect(window, colors["White"],
                                   (0, (window.get_height() - 50), window.get_width(), 10))

        for ball in balls:
            ball.update(window)
            # print(ball.on_ground)
            for particle in particles[:]:
                particle.update()
                particle.draw(window)
                if particle.life <= 0:
                    particles.remove(particle)


        # collision check
        for i in range(len(balls)):
            for j in range(i + 1, len(balls)):
                collision(balls[i], balls[j])

        
        # events
        events = pygame.event.get()
        
        for event in events:
            # print(event)

            # quit
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:

                    running = False


            
            # mouse controls 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cursor_pos = pygame.mouse.get_pos()

                    ball_clicked = False
                    for ball in balls:
                        if distance(cursor_pos, [ball.x, ball.y]) <= ball.radius:
                            ball.is_dragging = True
                            ball.drag_offset.x = ball.x - cursor_pos[0]
                            ball.drag_offset.y = ball.y - cursor_pos[1]
                            ball_clicked = True
                            break
                            
                    if not ball_clicked:
                        # not create ball if clicking on ground 
                        if cursor_pos[1] < window.get_height() - 50:
                            balls.append(Ball(cursor_pos[0], cursor_pos[1]))
            
            # stop dragging 
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for ball in balls:
                        ball.is_dragging = False
                        ball.prev_pos = None
            
            

            # Key controls 
            if event.type == pygame.KEYDOWN:
                if event.key == keytype["wasd"][1] or event.key == keytype["uldr"][1]:
                    for ball in balls:
                        ball.moving_left = True
                if event.key == keytype["wasd"][3] or event.key == keytype["uldr"][3]:
                    for ball in balls:
                        ball.moving_right = True
                
                # reset screen
                if event.key == pygame.K_r:
                    balls.clear()
                    particles.clear()
                    balls.append(Ball(400, 400, color=colors["Pink"]))

                # delete last ball
                if event.key == pygame.K_BACKSPACE:
                    if len(balls) > 1:
                        balls.pop()
                    
                # slowmo
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    slowmo = True

                # fullscreen 
                elif event.key == pygame.K_f:
                    fullscreen = not fullscreen
                    if fullscreen:
                        window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        window = pygame.display.set_mode(window_dimensions, pygame.RESIZABLE)
                    update_fade_surface()
                            
                    
                
            if event.type == pygame.KEYUP:
                if event.key == keytype["wasd"][1] or event.key == keytype["uldr"][1]:
                    for ball in balls:
                        ball.moving_left = False
                if event.key == keytype["wasd"][3] or event.key == keytype["uldr"][3]:
                    for ball in balls:
                        ball.moving_right = False

                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    slowmo = False

        if slowmo:
            clock.tick(fps//4)
        else:
            clock.tick(fps)
        pygame.display.update()


pygame_initilisation()
window_set()