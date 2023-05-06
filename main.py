import pygame
import os
import random
import csv
pygame.init()

sc_w, sc_h = 1000, 800
fps = 60
game = True
gravity = 0.75
moving_left, moving_right = False, False
ai_moving_left, ai_moving_right = False, False
shoot = False
tileSize = 50
update = True
amount_kills = 0
background_count = 0

sc = pygame.display.set_mode((sc_w, sc_h))
pygame.display.set_caption("Knock'em out! alpha v1.9")
clock = pygame.time.Clock()

bullet_img = pygame.image.load('img/icons/bullet.png')
ammo_box_img = pygame.image.load('img/icons/ammo_box.png')
health_box_img = pygame.image.load('img/icons/health_box.png')
plane_img = pygame.image.load('img/plane/plane.png')
boxes_img = [ammo_box_img, health_box_img]
background_img = pygame.image.load('background.png')
background2_img = pygame.image.load('background2.jpg')
backgrounds = [background_img, pygame.transform.scale(background2_img, (sc_w, sc_h))]
grass_img = pygame.image.load('grass3.png')
grass2_img = pygame.image.load('grass4.png')
sand1_img = pygame.image.load('sand1.png')
sandstone1_img = pygame.image.load('sandstone1.png')

 #to be continued...

font = pygame.font.Font('Baron Neue.otf', 20)
health_text = font.render('Health:', False, (255,255,255))

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.sc = sc
    def draw(self):
        sc.blit(self.image, (self.rect.x, self.rect.y))


class World:
    def __init__(self,filename):
        self.filename = filename
        self.tileSize = 50
        self.listT = []
        self.level = 1
    def read_csv(self):
        map_tile = []
        with open(self.filename) as data:
            data = csv.reader(data, delimiter=',')
            for row in data:
                map_tile.append(list(row))
        return map_tile
    def create_level(self, GameSprite, image1, image2):
        map_tile = self.read_csv()
        y = 0
        for row in map_tile:
            x = -3
            for tile in row:
                if tile == "0":
                    tile_sprite = GameSprite(x*self.tileSize, y*self.tileSize,50,50,image1)
                    self.listT.append(tile_sprite)
                if tile == "1":
                    tile_sprite = GameSprite(x*self.tileSize, y*self.tileSize,50,50,image2)
                    self.listT.append(tile_sprite)
                x += 1
            y += 1


class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed, ammo):
        pygame.sprite.Sprite.__init__(self)
        self.char_type = char_type
        self.scale = scale
        self.speed = speed
        self.ammo = ammo
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.frame_index = 0
        self.action = 0
        self.vel_y = 10
        self.shoot_cooldown = 0
        self.alive = True
        self.flip = False
        self.jump = False
        self.in_air = False
        self.moving = False
        self.shoot = False
        self.animation_list = []
        self.amount_kills = 0
        self.count_kills = 0
        #for ai
        self.move_counter = 0
        self.idle_counter = 0
        self.idling = False
        self.vision = pygame.Rect(0,0,200,20)

        animation_types = ['Idle', "Run", "Jump", "Death"]
        self.update_time = pygame.time.get_ticks()
        for animation in animation_types:
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))
            temp_list = []
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png")
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x,y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def health_bar(self):
        rect_empty = pygame.Rect(100,10,100,20)
        rect_full = pygame.Rect(100,10,self.health,20)
        pygame.draw.rect(sc, (255,0,0), rect_empty)
        if self.health > 0:
            pygame.draw.rect(sc, (0,255,0), rect_full)


    def update(self):
        self.update_animation()
        self.check_health()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def movement(self, moving_left, moving_right, world):
        dx = 0
        dy = 0
        #moving left or right
        keys_input = pygame.key.get_pressed()
        if moving_right and self.rect.right < sc_w:
            self.direction = 1
            self.flip = False
            dx = self.speed
            self.moving = True
        elif moving_left and self.rect.left > 0:
            self.direction = -1
            self.flip = True
            dx = -self.speed
            self.moving = True
        else:
            self.moving = False
        #update action
        if self.moving:
            self.update_action(1)
        elif self.in_air:
            self.update_action(2)
        else:
            self.update_action(0)
        #jumping
        if self.jump == True and not self.in_air:
            self.update_action(2)
            self.vel_y = -12.3
            self.jump = False
            self.in_air = True  
        #action of gravity 
        self.vel_y += gravity
        if self.vel_y >= 10:
            self.vel_y
        dy += self.vel_y

        for tile in world.listT:
            if tile.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0
            if tile.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile.rect.bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile.rect.top - self.rect.bottom
        #landing on a ground
        self.rect.x += dx
        self.rect.y += dy

    def shooting(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 10
            bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullets_group.add(bullet)
            self.ammo -= 1

    def update_animation(self):
        ANIMATION_COOLDOWN = 125
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action])-1
            else:
                self.frame_index = 0

    def ai(self):
        if self.alive and player.alive:
            if random.randint(1,200) == 2 and not self.in_air:
                self.update_action(0)
                self.idling = True
                self.idle_counter = 60
            if self.vision.colliderect(player.rect) and not self.in_air:
                self.update_action(0)
                self.shoot = True
                self.shooting()
            else:
                if self.idling == False:
                    if self.rect.left <= -120 or self.rect.right >= sc_w+120:
                        self.direction *= -1
                        self.move_counter *= -1
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.movement(ai_moving_left, ai_moving_right, world)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > 15:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idle_counter = 0
                        self.idling = False
        else:
            if not player.alive and self.alive:
                self.update_action(0)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_health(self):
        if self.health <= 0 and not self.in_air:
            self.shoot = False
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)
            if self.char_type == 'enemy' and self.frame_index == len(self.animation_list[self.action]) - 1:
                player.amount_kills += 1
                player.count_kills += 1
                self.kill()

    def draw(self):
        sc.blit(pygame.transform.flip(self.image, self.flip, False),(self.rect.x, self.rect.y))


class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 20
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x,y
        self.direction = direction

    def update(self):
        self.rect.x += (self.speed * self.direction)
        if self.rect.x < 0 or self.rect.x > sc_w: self.kill()
        for tile in world.listT:
            if self.rect.colliderect(tile.rect):
                self.kill()
        for group in enemy_groups:
            for enemy in group:
                if pygame.sprite.spritecollide(enemy, bullets_group, False):
                    if enemy.alive: 
                        enemy.health -= 25
                        self.kill()
        if pygame.sprite.spritecollide(player, bullets_group, False):
            if player.alive:
                player.health -= 5
                self.kill()


class ItemBox(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.speed_falling = 10
        self.image = random.choice(boxes_img)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x,y
        self.falling = True
    def update(self):
        self.rect.y += self.speed_falling
        for tile in world.listT:
            if tile.rect.colliderect(self.rect):
                self.rect.bottom = tile.rect.top
        if self.rect.colliderect(player.rect):
            if self.image == boxes_img[0]:
                player.ammo += 20
            if self.image == boxes_img[1]:
                player.health += 20
            self.kill()


class Plane(pygame.sprite.Sprite):
    def __init__(self,box):
        pygame.sprite.Sprite.__init__(self)
        self.image = plane_img
        self.rect = self.image.get_rect()
        self.box = box
        self.rect.y = 10
        self.rect.x = 0
        self.dx = 0
        self.rect.x, self.rect.y = 0,0
        self.is_hp = False
        self.is_ammo = False
    def position(self):
        if self.box.rect.x >= 0 and self.box.rect.x <= 450:
            self.rect.x = sc_w+300
            self.dx = -1
            self.image = pygame.transform.flip(self.image, False, False)
        if self.box.rect.x >= 450 and self.box.rect.x <= 950:
            self.rect.x = -300
            self.dx = 1
            self.image = pygame.transform.flip(self.image, True, False)
    def update(self):
        if (self.rect.left >= sc_w+500) or (self.rect.right <= -500):
            self.kill()
        if ((self.rect.left <= self.box.rect.x-50 and self.dx == -1) or (self.rect.right >= self.box.rect.x+50 and self.dx == 1)) and self.box.falling:
            items_group.add(self.box)
            self.box.falling = False
        self.rect.x += 2*self.dx
def redraw():
    for tile in world.listT:
        tile.draw()
    player.update()
    player.health_bar()
    player.draw()
    for group in enemy_groups:
        for enemy in group:
            enemy.ai()
            enemy.draw()
            enemy.update()
    if player.alive:
        player.movement(moving_left, moving_right, world)
        if shoot:
            player.shooting()
    
    bullets_group.draw(sc)
    bullets_group_enemy.draw(sc)
    bullets_group.update()
    items_group.update()
    items_group.draw(sc)
    plane_group.draw(sc)
    plane_group.update()


bullets_group = pygame.sprite.Group()
bullets_group_enemy = pygame.sprite.Group()
plane_group = pygame.sprite.Group()
items_group = pygame.sprite.Group()
enemy_groups = [pygame.sprite.Group() for i in range(5)]
for i in range(len(enemy_groups)-1):
    for y in range(2):
        if i == 0:
            enemy = Soldier('enemy', random.randint(-120,0),700, 1.7, 5, 20)
        if i == 1:
            enemy = Soldier('enemy', random.randint(-120,0), 500, 1.7, 5, 20)
        if i == 2:
            enemy = Soldier('enemy', random.randint(sc_w,sc_w+100), 700, 1.7, 5, 20)
        if i == 3:
            enemy = Soldier('enemy', random.randint(sc_w, sc_w+100), 500, 1.7, 5, 20)
        enemy_groups[i].add(enemy)


player = Soldier("player",200,200,1.7,5,40)
world = World("map1_2.csv")
world.create_level(GameSprite, grass_img , grass2_img)

while game:
    sc.blit(backgrounds[background_count], (0,0))
    ammo_text = font.render(f'Ammo: {player.ammo}', False, (255,255,255))
    sc.blit(health_text, (10,12))
    sc.blit(ammo_text, (10,37))
    redraw()
    if random.randint(1,1000) == 2:
        item = ItemBox(0, 40)
        if world.level == 1:
            item.rect.x = random.choice([random.randint(50,150), random.randint(800,900)])
        if world.level == 2:
            item.rect.x = random.choice([random.randint(0,100), 250, 700, random.randint(850,950)])
        plane = Plane(item)
        plane.position()
        plane_group.add(plane)

    if player.amount_kills >= 8:
        for i in range(len(enemy_groups)-1):
            for y in range(2):
                if i == 0:
                    enemy = Soldier('enemy', random.randint(-120,0),700, 1.7, 5, 20)
                if i == 1:
                    enemy = Soldier('enemy', random.randint(-120,0), 500, 1.7, 5, 20)
                if i == 2:
                    enemy = Soldier('enemy', random.randint(sc_w,sc_w+100), 700, 1.7, 5, 20)
                if i == 3:
                    enemy = Soldier('enemy', random.randint(sc_w, sc_w+100), 500, 1.7, 5, 20)
                enemy_groups[i].add(enemy)
        player.amount_kills = 0
    
    if player.count_kills > 1 and world.level == 1: 
        world.level += 1
        background_count += 1
        plane_group.empty()
        world.filename = 'map2_1.csv'
        world.listT = []
        world.create_level(GameSprite, sand1_img, sandstone1_img)
        player.rect.x, player.rect.y = 100, 100
        player.health = 100
        player.ammo = 40
        player.count_kills = 0
        for enemy_group in enemy_groups:
            enemy_group.empty()
        items_group.empty()
        for i in range(len(enemy_groups)-1):
            for y in range(2):
                if i == 0:
                    enemy = Soldier('enemy', random.randint(-120,0),700, 1.4, 5, 20)
                if i == 1:
                    enemy = Soldier('enemy', random.randint(-120,0), 500, 1.4, 5, 20)
                if i == 2:
                    enemy = Soldier('enemy', random.randint(sc_w,sc_w+100), 700, 1.4, 5, 20)
                if i == 3:
                    enemy = Soldier('enemy', random.randint(sc_w, sc_w+100), 500, 1.4, 5, 20)
                enemy_groups[i].add(enemy)
            player.amount_kills = 0

    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            game = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_SPACE:
                player.jump = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_a:
                moving_left = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            shoot = True
        if event.type == pygame.MOUSEBUTTONUP:
            shoot = False
        
    clock.tick(fps)