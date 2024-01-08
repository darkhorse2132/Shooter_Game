from typing import Any
from pygame import *
from random import randint

# ! Створюємо вікно гри
win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter 2D")

# ! Створення таймеру гри
clock = time.Clock()

# ! Записали назви файлів спрайтів
ASTEROID_SPRITE = "asteroid.png"
BULLET_SPRITE = "bullet.png"
BACKGROUND_SPRITE = "kitchen2.jpg"
PLAYER_SPRITE = "kisspng-carnivorous-plant-pitcher-plant-carnivore-clip-art-cartoon-bush-5b362d9918bf50.2974618315302772731014.png"
ENEMY_SPRITE = "kisspng-cartoon-fly-clip-art-fly-5abde314863167.9404411215223938765497.png"

# ! Звуки гри
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
mixer.music.set_volume(0.025)

fire_sound = mixer.Sound("fire.ogg")

# ! Ініциалізація модулю для створення тексту
font.init()
main_font = font.SysFont("Arial", 72, True, False)
stats_font = font.SysFont("Arial", 28, True, False)

# ? НЕ в ігровому циклі створюємо текст, який НЕ змінюється
win_text = main_font.render("You win!", True, (0, 200, 0))
lose_text = main_font.render("You lost!", True, (200, 0, 0))

# ! Клас GameSprite як основа для інших
class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()
        
        self.image = transform.scale(
            image.load(img),
            (w, h)
        )
        
        self.speed = speed
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))  
        
# ! Клас Player - наш ігрок
class Player(GameSprite):
    fire_delay = 20 # ! Сколько задержка между выстрелами
    fire_timer = fire_delay # ! Таймер (когда можно опять стрелять)
    fire_timer_active = False # ! Активный ли таймер (ограничение стрельбы)
    # ! Логіка
    def update(self):
        # ! Таймер работает только когда он АКТИВЕН
        # ! Ждем, пока пройдет время таймера...
        if self.fire_timer_active:
            # ! Если число в таймере > 0, то ждем
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                # ! Деактивируем таймер и восстанавливаем на следующий раз
                self.fire_timer_active = False
                self.fire_timer = self.fire_delay
        
        keys = key.get_pressed()
        if keys[K_a] or keys[K_LEFT]:
            if self.rect.x > 0:
                self.rect.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            if self.rect.x < win_width - self.image.get_width():
                self.rect.x += self.speed
        if keys[K_SPACE]:
            # ! Стреляем только если таймер НЕ активен
            if not self.fire_timer_active:
                self.fire() # ! Выстрелили
                self.fire_timer_active = True # ! Активировали таймер
    
    # ! Стрільба
    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx, self.rect.y, 10, 20, 7)
        bullet_group.add(bullet)
        fire_sound.play()
        fire_sound.set_volume(0.1)
    
# ! Клас Enemy - наші вороги
class Enemy(GameSprite):
    def update(self):
        global lost
        if self.rect.y < win_height and not sprite.collide_rect(player, self):
            self.rect.y += self.speed
        else:
            lost += 1
            self.kill()

# ! Клас Bullet - нашы пули
class Bullet(GameSprite):
    def update(self):
        global score
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()
        if sprite.spritecollide(self, enemys_group, True):
            score += 1
            self.kill()
    
# ! Стандартні змінні для нашої гри
FPS = 60 # ? 1 секунда = 60 тиков
GAME_RUN = True
GAME_FINISHED = False

score, lost = 0, 0
spawnrate_delay = FPS * 2 # ? 2 секунди
spawnrate_enemy = spawnrate_delay # ? ТАЙМЕР

# ! Спрайти
background = GameSprite(BACKGROUND_SPRITE, 0, 0, win_width, win_height, 0)
player = Player(PLAYER_SPRITE, win_width / 2, win_height - 100, 100, 70, 5)

enemys_group = sprite.Group()
bullet_group = sprite.Group()

# ! Игровий цикл
while GAME_RUN:
    
    # ? Перевірка на закриття гри
    for ev in event.get():
        if ev.type == QUIT:
            GAME_RUN = False
            
    # ? Гра "грається" поки не...
    if not GAME_FINISHED:
        
        # ? Створюємо В ігровому циклі тексти, які БУДУТЬ змінюватись по ходу гри
        score_text = stats_font.render("Вбито: " + str(score), True, (200, 200, 200))
        lost_text = stats_font.render("Пропущено: " + str(lost), True, (200, 200, 200))
        
        # ! ТАЙМЕР СПАВНА ВОРОГІВ
        if spawnrate_enemy < 0:
            enemy = Enemy("kisspng-cartoon-fly-clip-art-fly-5abde314863167.9404411215223938765497.png", randint(64, win_width - 64), -64, 64, 64, randint(1, 7))
            enemys_group.add(enemy)
            if spawnrate_delay > FPS * 0.5:
                spawnrate_delay -= 10
            spawnrate_enemy = spawnrate_delay
        else:
            spawnrate_enemy -= 1
        
        background.reset()
        player.reset()
        enemys_group.draw(window)
        bullet_group.draw(window)
        
        player.update()
        enemys_group.update()
        bullet_group.update()
        
        window.blit(score_text, (5, 5))
        window.blit(lost_text, (5, score_text.get_height() + 5))
        
        # ! ПЕРЕМОГА ТА ПОРАЗКА
        if score >= 15:
            end_screen = main_font.render("Ти виграв!", True, (200, 200, 200))
            window.blit(end_screen, (win_width / 2 - end_screen.get_width() / 2, win_height / 2))
            GAME_FINISHED = True
            
        if lost >= 5:
            end_screen = main_font.render("Ти програв!", True, (200, 0, 0))
            window.blit(end_screen, (win_width / 2 - end_screen.get_width() / 2, win_height / 2))
            GAME_FINISHED = True
        
        # ? Відновлюємо екран якщо не закінчили гру
        display.update()
    
    # ? Встановили ФПС
    clock.tick(FPS)

