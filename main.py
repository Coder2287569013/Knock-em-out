import pygame
import os
import random
pygame.init()

sc_w, sc_h = 1000,800
fps = 60
game = True
gravity = 0.75
moving_left, moving_right = False, False
ai_moving_left, ai_moving_right = False, False
shoot = False
tileSize = 50

sc = pygame.display.set_mode((sc_w, sc_h))
pygame.display.set_caption("Knock'em out! alpha v1.3")
clock = pygame.time.Clock()

bullet_img = pygame.image.load('img/icons/bullet.png')

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
        #for ai
        self.move_counter = 0
        self.idle_counter = 0
        self.idling = False
        self.vision = pygame.Rect(0,0,150,20)

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

    def update(self):
        self.update_animation()
        self.check_health()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def movement(self, moving_left, moving_right):
        dx = 0
        dy = 0
        #moving left or right
        keys_input = pygame.key.get_pressed()
        if moving_right:
            self.direction = 1
            self.flip = False
            dx = self.speed
            self.moving = True
        elif moving_left:
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
            self.vel_y = -11
            self.jump = False 
            self.in_air = True  
        #action of gravity 
        self.vel_y += gravity
        if self.vel_y >= 10:
            self.vel_y
        dy += self.vel_y
        #landing on a ground
        if self.rect.bottom + dy >= 400:
            dy = 400 - self.rect.bottom
            self.in_air = False
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
            if random.randint(1,200) == 2:
                self.update_action(0)
                self.idling = True
                self.idle_counter = 60
            if self.vision.colliderect(player.rect):
                self.update_action(0)
                self.shoot = True
                self.shooting()
            else:
                if not self.idling:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.movement(ai_moving_left, ai_moving_right)
                    self.move_counter += 1
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    if self.move_counter > tileSize:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idle_counter -= 1
                    if self.idle_counter <= 0:
                        self.idle_counter = 0
                        self.idling = False

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_health(self):
        if self.health <= 0:
            self.shoot = False
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

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
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullets_group, False):
                if enemy.alive: 
                    enemy.health -= 25
                    self.kill()
        if pygame.sprite.spritecollide(player, bullets_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

bullets_group = pygame.sprite.Group()
bullets_group_enemy = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
player = Soldier("player",200,200,2,5,40)
enemy = Soldier("enemy",570,200,2,5,20)
enemy2 = Soldier("enemy",300,200,2,5,20)
enemy_group.add(enemy)
enemy_group.add(enemy2)

while game:
    sc.fill((50,50,50))
    for enemy in enemy_group:
        enemy.ai()
        enemy.update()
        enemy.draw()
    player.draw()
    bullets_group.draw(sc)
    bullets_group_enemy.draw(sc)
    bullets_group.update()
    if player.alive:
        player.movement(moving_left, moving_right)
        if shoot:
            player.shooting()
    player.update()

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
        
    pygame.display.update()
    clock.tick(fps)