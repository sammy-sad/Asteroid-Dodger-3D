from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import random
import sys
import math

import time


win_w, win_h = 800, 600
stars = []
NUM_STARS = 1500
star_sp = 35.0
planetNumbers = 10


planets = []
_last_time = None
quadric = None
mode_camera = 0




ship_x = 0.0
ship_y = 0.0
SHIP_BOUND_X = 50.0
SHIP_BOUND_Y = 30.0





asteroids = []
NUM_ASTEROIDS = 10
ini_speed_ast = 25.0
ast_speed = ini_speed_ast
lives = 3
score = 0
cheat = False





bullets = []
BULLET_SPEED = 60.0
MAX_BULLETS = 5





spboost_active = False
spboost_endt = 0
boost_duration = 10
boost_mult = 2.0
boost_flame_visible = True
boost_flame_timer = 0




gameState = "MENU"
selected_option = 0
menu_options = ["Start Game", "Select Theme", "Exit"]

theme_names = ["Black", "Blue", "Pink"]
current_theme = 0


paused_options = ["Resume", "Start New Game", "Select Theme", "Exit"]
game_over_options = ["1. Start Over", "2. Exit"]

select_gameOver = 0
pause_button_visible = True








def init_stars():
    global stars
    stars = []


    for _ in range(NUM_STARS):
        x = random.uniform(-200, 200)
        y = random.uniform(-100, 100)
        z = random.uniform(-500, -5)
        stars.append([x, y, z])

def stars_spawning(dt):
    for s in stars:

        current_speed =star_sp * (boost_mult if spboost_active else 1.0)
        s[2] += current_speed * dt

        if s[2] > 0:
            s[0] = random.uniform(-200, 200)
            s[1] = random.uniform(-100, 100)
            s[2] = random.uniform(-500, -50)

class Planet:
    def __init__(self, x, y, z, radius, color):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius
        self.color = color





def init_planets():
    global planets, quadric
    planets = []
    if quadric is None:
        quadric = gluNewQuadric()
    for _ in range(planetNumbers):
        x = random.uniform(-200, 200)
        y = random.uniform(-100, 100)
        z = random.uniform(-500, -50)
        radius = random.uniform(4, 10)
        color = (random.random(), random.random(), random.random())
        planets.append(Planet(x, y, z, radius, color))



def planets_spawning(dt):

    for p in planets:
        current_speed = star_sp * (boost_mult if spboost_active else 1.0)
        p.z += current_speed * dt

        if p.z > 0:
            p.x = random.uniform(-200, 200)
            p.y = random.uniform(-100, 100)
            p.z = random.uniform(-800, -100)
            p.radius = random.uniform(4, 10)
            p.color = (random.random(), random.random(), random.random())




class Asteroid:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

        self.color = (random.uniform(0.3, 0.6),
                      random.uniform(0.3, 0.4),
                      random.uniform(0.2, 0.3))

        self.rot = random.uniform(0, 180)
        self.rot_speed = random.uniform(-50, 50)
        self.vx, self.vy, self.vz = 0, 0, 0



    def aimingship(self):
        dx = ship_x - self.x
        dy = ship_y - self.y
        dz = 0.0 - self.z
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist == 0: dist = 0.01
        self.vx = dx / dist * ast_speed
        self.vy = dy / dist * ast_speed
        self.vz = dz / dist * ast_speed

    def reset(self):
        self.x = random.uniform(-40, 40)
        self.y = random.uniform(-20, 20)
        self.z = random.uniform(-400, -200)
        self.radius = random.uniform(5, 12)
        self.aimingship()

def init_asteroids():
    global asteroids
    asteroids = []

    for _ in range(NUM_ASTEROIDS):
        x = random.uniform(-50, 50)
        y = random.uniform(-30, 30)
        z = random.uniform(-400, -200)
        radius = random.uniform(5, 12)
        a = Asteroid(x, y, z, radius)
        a.aimingship()
        asteroids.append(a)



def Asteroid_spawn(dt):
    global lives, score, cheat, ast_speed
    for a in asteroids:
        a.x += a.vx * dt
        a.y += a.vy * dt
        a.z += a.vz * dt

        dx = ship_x - a.x
        dy = ship_y - a.y
        dz = 0.0 - a.z
        distance = math.sqrt(dx * dx + dy * dy + dz * dz)
        if distance < a.radius + 5.0:
            if not cheat:
                lives -= 1
            a.reset()
            continue

        if a.z > 50:
            a.reset()




def draw_asteroids():
    for a in asteroids:
        glPushMatrix()
        glTranslatef(a.x, a.y, a.z)
        glRotatef(a.rot, 1.0, 1.0, 0.0)
        glScalef(a.radius / 5, a.radius / 5, a.radius / 5)
        glColor3f(*a.color)
        glutSolidDodecahedron()
        glPopMatrix()
        a.rot += a.rot_speed * 0.01


class Bullet:

    def __init__(self, x, y, z, angle=0):
        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

def bulletFiring(offset_x=0.0, angle=0):
    global bullets

    if True:
        bullets.append(Bullet(ship_x + offset_x, -5.0, 0.0, angle))

def update_bullets(dt):
    global score, ast_speed
    new_bullets = []

    for b in bullets:

        angle_rad = math.radians(b.angle)
        b.x += math.sin(angle_rad) * BULLET_SPEED * dt
        b.z -= math.cos(angle_rad) * BULLET_SPEED * dt

        hit = False

        for a in asteroids[:]:
            dx = b.x - a.x
            dy = b.y - a.y
            dz = b.z - a.z
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)

            if distance < a.radius + 2.0:
                asteroids.remove(a)
                score += 1
                hit = True
                if score % 10 == 0:
                    ast_speed += 2.0
                new_asteroid = Asteroid(
                    random.uniform(-200, 200),
                    random.uniform(-100, 100),
                    random.uniform(-500, -200),
                    random.uniform(5, 12)
                )
                new_asteroid.aimingship()
                asteroids.append(new_asteroid)
                break
        if not hit and b.z > -500 and abs(b.x) < 200:
            new_bullets.append(b)
    bullets[:] = new_bullets

def bulletdraw():

    glDisable(GL_LIGHTING)
    glColor3f(0.55, 0.27, 0.07)
    for b in bullets:
        glPushMatrix()
        glTranslatef(b.x, b.y, b.z)
        glutSolidSphere(1.0, 10, 10)
        glPopMatrix()
    glEnable(GL_LIGHTING)

def activate_speed_boost():

    global spboost_active, spboost_endt

    if not spboost_active:
        spboost_active = True
        spboost_endt = time.time() + boost_duration

def SpeedBoost_update():

    global spboost_active, boost_flame_visible, boost_flame_timer

    if spboost_active:
        if time.time() > spboost_endt:
            spboost_active = False

        boost_flame_timer += 0.1
        if boost_flame_timer > 0.5:
            boost_flame_visible = not boost_flame_visible
            boost_flame_timer = 0

def starDraw():

    glDisable(GL_LIGHTING)
    glPointSize(1.0)
    glBegin(GL_POINTS)

    for x, y, z in stars:
        brightness = random.uniform(0.7, 1.0)
        glColor3f(brightness, brightness, brightness)
        glVertex3f(x, y, z)


    glEnd()
    glEnable(GL_LIGHTING)

def planets_drawing():

    for p in planets:

        glPushMatrix()
        glTranslatef(p.x, p.y, p.z)
        glRotatef(20, 0, 1, 0)

        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [p.color[0], p.color[1], p.color[2], 1.0])
        gluSphere(quadric, p.radius, 32, 16)
        glPopMatrix()


def draw_ship():

    glPushMatrix()

    glTranslatef(ship_x, ship_y, 0.0)
    glDisable(GL_LIGHTING)

    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.0, 3.0, 0.0)
    glVertex3f(-2.0, -3.0, 0.0)
    glVertex3f(2.0, -3.0, 0.0)
    glEnd()

    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-1.5, 0.0, 0.0)
    glVertex3f(1.5, 0.0, 0.0)
    glVertex3f(1.5, -0.5, 0.0)
    glVertex3f(-1.5, -0.5, 0.0)
    glEnd()

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-2.0, -3.0, 0.0)
    glVertex3f(-4.0, -3.0, 0.0)
    glVertex3f(-2.0, 0.0, 0.0)

    glEnd()

    glBegin(GL_TRIANGLES)

    glVertex3f(2.0, -3.0, 0.0)
    glVertex3f(4.0, -3.0, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glEnd()

    glColor3f(0.0, 0.0, 0.9)
    glBegin(GL_TRIANGLES)
    glVertex3f(0.0, 3.0, 1.0)
    glVertex3f(0.0, 3.0, -1.0)

    glVertex3f(0.0, 5.0, 0.0)
    glEnd()

    glColor3f(1.0, 0.3, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex3f(-1.0, -3.0, 0.0)
    glVertex3f(1.0, -3.0, 0.0)

    glVertex3f(0.0, -6.0, 0.0)
    glEnd()

    if spboost_active and boost_flame_visible:
        glColor3f(0.0, 0.5, 1.0)
        glBegin(GL_TRIANGLES)

        glVertex3f(-1.5, -3.0, 0.0)
        glVertex3f(1.5, -3.0, 0.0)
        glVertex3f(0.0, -9.0, 0.0)
        glEnd()

    glEnable(GL_LIGHTING)
    glPopMatrix()

def set_camera():

    if mode_camera == 0:
        gluLookAt(ship_x, ship_y + 5.0, 10.0,
                  ship_x, ship_y, -50.0,
                  0.0, 1.0, 0.0)

    elif mode_camera == 1:

        gluLookAt(0.0, 50.0, 0.0,
                  0.0, 0.0, -50.0,
                  0.0, 0.0, -1.0)

def draw_ui():
    glDisable(GL_LIGHTING)
    glDisable(GL_BLEND)

    glMatrixMode(GL_PROJECTION)

    glPushMatrix()

    glLoadIdentity()
    gluOrtho2D(0, win_w, 0, win_h)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(20, win_h - 30)

    for char in f"Score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glRasterPos2f(20, win_h - 60)
    for char in f"Lives: {lives}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glRasterPos2f(20, win_h - 90)

    for char in f"Speed: {ast_speed:.1f}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glRasterPos2f(20, win_h - 120)
    if spboost_active:
        remaining = max(0, spboost_endt - time.time())
        for char in f"Boost: {remaining:.1f}s":

            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    else:
        for char in "Boost: READY (W)":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    if pause_button_visible and gameState == "PLAYING":

        glColor3f(0.8, 0.2, 0.2)
        glRasterPos2f(win_w - 100, win_h - 30)

        for char in "  PAUSE  ":
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glRasterPos2f(20, 30)
    for char in "Controls: Arrows to move, A/D to shoot from wings, S to shoot from center, W for speed boost":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()

    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_LIGHTING)

    glEnable(GL_BLEND)


def draw_menu():
    glDisable(GL_BLEND)
    glDisable(GL_LIGHTING)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluOrtho2D(0, win_w, 0, win_h)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


    glColor3f(0.8, 0.8, 1.0)
    glRasterPos2f(win_w / 2 - 80, win_h - 100)

    for char in "SPACE DODGER":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    option_colors = [
        (1.0, 0.5, 0.5),
        (0.5, 0.8, 1.0),
        (1.0, 0.7, 0.8)
    ]



    for i, option in enumerate(menu_options):
        if i == selected_option:
            glColor3f(1.0, 1.0, 0.0)
        else:
            glColor3f(*option_colors[i % len(option_colors)])

        glRasterPos2f(win_w / 2 - 100, win_h / 2 - i * 40)
        for char in f"{i + 1}. {option}":
            glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(char))

    glEnable(GL_BLEND)
    glEnable(GL_LIGHTING)

def draw_pause_menu():
    glDisable(GL_BLEND)
    glDisable(GL_LIGHTING)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluOrtho2D(0, win_w, 0, win_h)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)

    glRasterPos2f(win_w / 2 - 30, win_h - 100)

    for char in "PAUSED":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    for i, option in enumerate(paused_options):
        if i == selected_option:
            glColor3f(1.0, 0.5, 0.5)
        else:

            glColor3f(1.0, 1.0, 1.0)

        glRasterPos2f(win_w / 2 - 70, win_h / 2 - i * 30)
        for char in f"{i + 1}. {option}":

            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glDisable(GL_BLEND)
    glDisable(GL_LIGHTING)

def on_display():
    global _last_time, lives, gameState, select_gameOver

    if gameState == "MENU":
        draw_menu()
        glutSwapBuffers()
        return

    if gameState == "PAUSED":
        draw_pause_menu()
        glutSwapBuffers()
        return

    if lives <= 0 and gameState != "GAME_OVER":

        gameState = "GAME_OVER"
        select_gameOver = 0

    if gameState == "GAME_OVER":
        draw_game_over_menu()
        glutSwapBuffers()
        return

    now = glutGet(GLUT_ELAPSED_TIME) / 1000.0
    dt = 0 if _last_time is None else now - _last_time
    _last_time = now

    stars_spawning(dt)
    planets_spawning(dt)

    Asteroid_spawn(dt)
    update_bullets(dt)

    SpeedBoost_update()

    for p in planets:
        dx = ship_x - p.x
        dy = ship_y - p.y
        dz = 0.0 - p.z

        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < p.radius + 3.0:
            lives = 0

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70.0, win_w / float(win_h), 0.1, 500.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    set_camera()

    starDraw()
    planets_drawing()
    draw_asteroids()
    bulletdraw()
    draw_ship()

    draw_ui()

    glutSwapBuffers()
    glutPostRedisplay()

def draw_game_over_menu():
    glDisable(GL_LIGHTING)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()
    gluOrtho2D(0, win_w, 0, win_h)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(win_w / 2 - 50, win_h - 100)
    for char in "GAME OVER":
        glutBitmapCharacter(GLUT_BITMAP_TIMES_ROMAN_24, ord(char))

    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(win_w / 2 - 70, win_h - 150)
    for char in f"Your score: {score}":
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

    for i, option in enumerate(game_over_options):
        if i == select_gameOver:
            glColor3f(1.0, 1.0, 1.0)
        else:
            glColor3f(0.8, 0.8, 0.8)

        glRasterPos2f(win_w / 2 - 50, win_h / 2 - i * 40)
        for char in option:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
    glEnable(GL_LIGHTING)

def on_reshape(w, h):
    global win_w, win_h
    win_w, win_h = max(1, w), max(1, h)
    glViewport(0, 0, win_w, win_h)

def on_keyboard(key, x, y):
    global cheat, mode_camera, gameState, selected_option, lives, score, asteroids, bullets, select_gameOver

    if gameState == "GAME_OVER":
        if key == b'\r':
            handle_game_over_selection()
            return
        elif key == b'w' or key == b'W':
            select_gameOver = (select_gameOver - 1) % len(game_over_options)

            return
        elif key == b's' or key == b'S':
            select_gameOver = (select_gameOver + 1) % len(game_over_options)
            return
        elif key == b'1':
            select_gameOver = 0
            handle_game_over_selection()
            return
        elif key == b'2':
            select_gameOver = 1
            handle_game_over_selection()
            return
    if gameState == "MENU" or gameState == "PAUSED":
        if key == b'\r':
            handle_menu_selection()
            return
        elif key == b'\x1b':

            if gameState == "PAUSED":
                gameState = "PLAYING"
            else:
                glutLeaveMainLoop()
            return

        elif key == b'w' or key == b'W':
            max_options = len(menu_options) if gameState == "MENU" else len(paused_options)
            selected_option = (selected_option - 1) % max_options
            return

        elif key == b's' or key == b'S':
            max_options = len(menu_options) if gameState == "MENU" else len(paused_options)
            selected_option = (selected_option + 1) % max_options
            return
        elif key == b'1':
            selected_option = 0
            handle_menu_selection()
            return
        elif key == b'2':
            selected_option = 1
            handle_menu_selection()
            return
        elif key == b'3' and gameState == "MENU":
            selected_option = 2

            handle_menu_selection()
            return
        elif key == b'3' and gameState == "PAUSED":
            selected_option = 2
            handle_menu_selection()
            return
        elif key == b'4' and gameState == "PAUSED":
            selected_option = 3
            handle_menu_selection()
            return


    if key == b'\x1b':
        glutLeaveMainLoop()

    elif key == b' ':
        if gameState == "PLAYING":
            gameState = "PAUSED"

            selected_option = 0
        elif gameState == "PAUSED":
            gameState = "PLAYING"
        return
    elif key == b'c' or key == b'C':
        cheat = not cheat
    elif key in (b'a', b'A'):

        bulletFiring(offset_x=-1.5, angle=-15)
    elif key in (b'd', b'D'):

        bulletFiring (offset_x=1.5, angle=15)

    elif key == b's' or key == b'S':
        bulletFiring(offset_x=0.0, angle=0)
    elif key == b'w' or key == b'W':
        activate_speed_boost()

def handle_game_over_selection():
    global gameState, select_gameOver, lives, score, asteroids, bullets, ship_x, ship_y

    if select_gameOver == 0:
        init_game()

        gameState = "PLAYING"
    elif select_gameOver == 1:

        glutLeaveMainLoop()

def handle_menu_selection():
    global gameState, selected_option, lives, score, asteroids, bullets

    if gameState == "MENU":
        if selected_option == 0:
            init_game()
            gameState = "PLAYING"
        elif selected_option == 1:

            ToggleTheme()
        elif selected_option == 2:
            glutLeaveMainLoop()
    elif gameState == "PAUSED":
        if selected_option == 0:

            gameState = "PLAYING"
        elif selected_option == 1:
            init_game()
            gameState = "PLAYING"
        elif selected_option == 2:
            ToggleTheme()

        elif selected_option == 3:
            glutLeaveMainLoop()


def init_game():
    global lives, score, asteroids, bullets, ship_x, ship_y, ast_speed

    lives = 3
    score = 0
    ship_x = 0.0
    ship_y = 0.0
    ast_speed = ini_speed_ast
    init_asteroids()
    bullets = []
    init_stars()
    init_planets()

def ToggleTheme():
    global current_theme
    current_theme = (current_theme + 1) % 3
     
    apply_theme(current_theme)

def apply_theme(theme_id):
    if theme_id == 0:
        glClearColor(0.0, 0.0, 0.0, 1.0)
    elif theme_id == 1:
        glClearColor(0.1, 0.15, 0.4, 1.0)
    elif theme_id == 2:
        glClearColor(1.000, 0.078, 0.576, 1.0)

def on_special(key, x, y):
    global mode_camera, ship_x, ship_y
    step = 2.0
    if spboost_active:
        step *= boost_mult

    if key == GLUT_KEY_UP:
        mode_camera = 1
    elif key == GLUT_KEY_DOWN:
        mode_camera = 0
    elif key == GLUT_KEY_LEFT:


        ship_x -= step
        ship_x = max(ship_x, -SHIP_BOUND_X)
    elif key == GLUT_KEY_RIGHT:
        ship_x += step
        
        ship_x = min(ship_x, SHIP_BOUND_X)
    elif key == GLUT_KEY_PAGE_UP:
        ship_y += step
        ship_y = min(ship_y, SHIP_BOUND_Y)
    elif key == GLUT_KEY_PAGE_DOWN:
        ship_y -= step

        ship_y = max(ship_y, -SHIP_BOUND_Y)

def Mouse(button, state, x, y):
    global gameState, selected_option

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        y = win_h - y


        if (x >= win_w - 100 and x <= win_w and
                y >= win_h - 30 and y <= win_h and

                gameState == "PLAYING"):
            gameState = "PAUSED"
            selected_option = 0

def init_gl():
    glClearColor(0.02, 0.02, 0.05, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 50.0, 50.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 1.0, 1.0))

    glLightfv(GL_LIGHT0, GL_SPECULAR, (0.8, 0.8, 0.9, 1.0))

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)

    glutInitWindowSize(win_w, win_h)
    glutCreateWindow(b"Space Dodger")

    init_gl()
    
    init_stars()
    
    init_planets()
    
    init_asteroids()

    glutDisplayFunc(on_display)
    glutReshapeFunc(on_reshape)

    glutKeyboardFunc(on_keyboard)
    
    glutSpecialFunc(on_special)
    glutMouseFunc(Mouse)


    glutMainLoop()

if __name__ == "__main__":
    main()