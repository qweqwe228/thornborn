import pygame
import random
import math
import os

pygame.init()
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Roguelike")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load("rubick.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface((40, 40))
            self.image.fill((0, 128, 255))
        original_width, original_height = self.image.get_size()
        desired_width = 128
        desired_height = int(original_height * desired_width / original_width)
        self.image = pygame.transform.scale(self.image, (desired_width, desired_height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 10
        self.cooldown = 1000
        self.last_ability_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_UP]:
            self.rect.y -= 5
        if keys[pygame.K_DOWN]:
            self.rect.y += 5

    def use_ability(self, enemies, projectile_group, all_sprites):
        closest_enemy = None
        closest_distance = float('inf')
        for enemy in enemies:
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < closest_distance:
                closest_distance = distance
                closest_enemy = enemy
        if closest_enemy:
            proj = Projectile(self.rect.center, closest_enemy, speed=10)
            projectile_group.add(proj)
            all_sprites.add(proj)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, speed=2):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.player = player

    def update(self):
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        distance = math.sqrt(dx * dx + dy * dy)
        if distance != 0:
            self.rect.x += int((dx / distance) * self.speed)
            self.rect.y += int((dy / distance) * self.speed)
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

class Projectile(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, speed=10):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(center=start_pos)
        dx = target.rect.centerx - start_pos[0]
        dy = target.rect.centery - start_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance == 0:
            distance = 1
        self.velocity_x = (dx / distance) * speed
        self.velocity_y = (dy / distance) * speed

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()

def generate_wave(wave_number, player):
    enemy_count = 5 + 2 * (wave_number - 1)
    enemies = pygame.sprite.Group()
    for _ in range(enemy_count):
        x = random.randrange(0, SCREEN_WIDTH - 30)
        y = random.randrange(0, SCREEN_HEIGHT - 30)
        enemy = Enemy(x, y, player, speed=2 + wave_number * 0.2)
        enemies.add(enemy)
    return enemies

def draw_health_bar(surface, x, y, width, height, current_health, max_health):
    ratio = current_health / max_health
    current_width = int(width * ratio)
    pygame.draw.rect(surface, (255, 0, 0), (x, y, width, height), 2)
    pygame.draw.rect(surface, (0, 255, 0), (x, y, current_width, height))

def main():
    wave = 1
    player = Player(100, 100)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    enemy_group = generate_wave(wave, player)
    all_sprites.add(enemy_group)
    projectile_group = pygame.sprite.Group()
    running = True
    while running:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if now - player.last_ability_time >= player.cooldown:
            player.use_ability(enemy_group, projectile_group, all_sprites)
            player.last_ability_time = now
        all_sprites.update()
        collided_enemies = pygame.sprite.spritecollide(player, enemy_group, True)
        if collided_enemies:
            player.health -= len(collided_enemies)
            if player.health <= 0:
                running = False
        for projectile in projectile_group:
            hit_enemies = pygame.sprite.spritecollide(projectile, enemy_group, True)
            if hit_enemies:
                projectile.kill()
        if len(enemy_group) == 0:
            wave += 1
            enemy_group = generate_wave(wave, player)
            all_sprites.add(enemy_group)
        screen.fill((30, 30, 30))
        all_sprites.draw(screen)
        draw_health_bar(screen, 10, 10, 200, 20, player.health, 10)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == '__main__':
    main()

