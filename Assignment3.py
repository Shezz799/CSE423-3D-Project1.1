from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

# ------------------------------
# Constants and global state
# ------------------------------
# Camera
camera_pos = (0, 500, 400)
camera_target = (0, 0, 0)
# fovY = 120
ASPECT = 1.25

# World / grid
GRID_LENGTH = 600
GRID_CELL = 60
WALL_HEIGHT = 200
BOUND_MIN = -GRID_LENGTH
BOUND_MAX = GRID_LENGTH

# Game state
rand_seed = 423
random.seed(rand_seed)
player = {
    "x": 0.0, "y": 0.0, "z": 0.0,
    "angle_deg": 0.0,
    "life": 5, "alive": True, "lying": False
}
score = 0
missed = 0
game_over = False

# Dynamics
PLAYER_SPEED = 8.0
TURN_SPEED = 4.0
BULLET_SPEED = 10
BULLET_SIZE = 4.0
BULLET_MAX_DIST = 2000.0
ENEMY_SPEED = 0.1
ENEMY_COUNT = 5
ENEMY_BASE_RADIUS = 35.0
ENEMY_PULSE_AMP = 10.0

enemies = []
bullets = []

# Camera controls
third_person = True
cam_orbit_deg = 270.0
cam_radius = 100.0
cam_height = 300.0

# First-person offsets
FP_EYE_HEIGHT = 120.0
# GUN_BARREL_LEN = 60.0

# Cheat mode
cheat_on = False
cheat_vision_on = False
auto_rotate_speed = 1.5
auto_fire_cooldown = 0
AUTO_FIRE_COOLDOWN_MAX = 10
# AIM_THRESHOLD_DEG = 4.0

def d2r(a):
    return a * math.pi / 180.0

# ------------------------------
# Text rendering
# ------------------------------
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

# ------------------------------
# World drawing
# ------------------------------
def draw_boundaries():
    h = WALL_HEIGHT
    glBegin(GL_QUADS)
    # +Y wall
    glColor3f(0.0, 1.0, 1.0)
    glVertex3f(BOUND_MIN, BOUND_MAX, 0)
    glVertex3f(BOUND_MAX, BOUND_MAX, 0)
    glVertex3f(BOUND_MAX, BOUND_MAX, h)
    glVertex3f(BOUND_MIN, BOUND_MAX, h)
    # -Y wall
    glColor3f(1.0, 1.0, 1.0)
    glVertex3f(BOUND_MIN, BOUND_MIN, 0)
    glVertex3f(BOUND_MIN, BOUND_MIN, h)
    glVertex3f(BOUND_MAX, BOUND_MIN, h)
    glVertex3f(BOUND_MAX, BOUND_MIN, 0)
    # +X wall
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(BOUND_MAX, BOUND_MIN, 0)
    glVertex3f(BOUND_MAX, BOUND_MIN, h)
    glVertex3f(BOUND_MAX, BOUND_MAX, h)
    glVertex3f(BOUND_MAX, BOUND_MAX, 0)
    # -X wall
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(BOUND_MIN, BOUND_MIN, 0)
    glVertex3f(BOUND_MIN, BOUND_MAX, 0)
    glVertex3f(BOUND_MIN, BOUND_MAX, h)
    glVertex3f(BOUND_MIN, BOUND_MIN, h)
    glEnd()

def draw_floor_quads():
    glBegin(GL_QUADS)
    for i in range(int(BOUND_MIN / GRID_CELL), int(BOUND_MAX / GRID_CELL)):
        for j in range(int(BOUND_MIN / GRID_CELL), int(BOUND_MAX / GRID_CELL)):
            if (i + j) % 2 == 0:
                glColor3f(0.8, 0.8, 0.8)
            else:
                glColor3f(0.5, 0.2, 0.8)
            x = i * GRID_CELL
            y = j * GRID_CELL
            glVertex3f(x, y, 0)
            glVertex3f(x + GRID_CELL, y, 0)
            glVertex3f(x + GRID_CELL, y + GRID_CELL, 0)
            glVertex3f(x, y + GRID_CELL, 0)
    glEnd()

# ------------------------------
# Models
# ------------------------------
def draw_cuboid(dx, dy, dz):
    x0, x1 = -dx / 2.0, dx / 2.0
    y0, y1 = -dy / 2.0, dy / 2.0
    z0, z1 = -dz / 2.0, dz / 2.0
    glBegin(GL_QUADS)
    # Top
    glVertex3f(x0, y0, z1); glVertex3f(x1, y0, z1); glVertex3f(x1, y1, z1); glVertex3f(x0, y1, z1)
    # Bottom
    glVertex3f(x0, y0, z0); glVertex3f(x0, y1, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y0, z0)
    # Front (y1)
    glVertex3f(x0, y1, z0); glVertex3f(x0, y1, z1); glVertex3f(x1, y1, z1); glVertex3f(x1, y1, z0)
    # Back (y0)
    glVertex3f(x0, y0, z0); glVertex3f(x1, y0, z0); glVertex3f(x1, y0, z1); glVertex3f(x0, y0, z1)
    # Left (x0)
    glVertex3f(x0, y0, z0); glVertex3f(x0, y0, z1); glVertex3f(x0, y1, z1); glVertex3f(x0, y1, z0)
    # Right (x1)
    glVertex3f(x1, y0, z0); glVertex3f(x1, y1, z0); glVertex3f(x1, y1, z1); glVertex3f(x1, y0, z1)
    glEnd()

def draw_player():
    glPushMatrix()
    glTranslatef(player["x"], player["y"], player["z"])
    glRotatef(player["angle_deg"], 0, 0, 1)

    if player["lying"]:
        glRotatef(90, 1, 0, 0)

    # Legs
    glColor3f(0.0, 0.0, 1.0)
    glPushMatrix()
    glTranslatef(15, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 10, 40, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-15, 0, 0)
    gluCylinder(gluNewQuadric(), 4, 10, 40, 10, 10)
    glPopMatrix()

    # Torso
    glColor3f(0.2, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 27 + 40)
    draw_cuboid(35, 20, 54)
    glPopMatrix()

    # Head
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 54 + 40 + 10)
    gluSphere(gluNewQuadric(), 10, 10, 10)
    glPopMatrix()

    # Arms
    glColor3f(0.9, 0.7, 0.6)
    glPushMatrix()
    glTranslatef(17, 10, 54 + 40 - 8)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 4, 30, 10, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(-17, 10, 54 + 40 - 8)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 4, 30, 10, 10)
    glPopMatrix()

    # Barrel
    glColor3f(0.5, 0.5, 0.5)
    glPushMatrix()
    glTranslatef(0, 10, 54 + 40 - 10)
    glRotatef(-90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 10, 5, 35, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_enemy(e):
    scale = 1.0 + ENEMY_PULSE_AMP / ENEMY_BASE_RADIUS * math.sin(e["pulse"])
    base_r = e["radius"]
    top_r = base_r * 0.5
    glPushMatrix()
    glTranslatef(e["x"], e["y"], e["z"])
    glScalef(scale, scale, scale)
    glColor3f(1.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, base_r)
    gluSphere(gluNewQuadric(), base_r, 14, 12)
    glPopMatrix()
    glColor3f(0.0, 0.0, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, base_r + top_r * 1.6)
    gluSphere(gluNewQuadric(), top_r, 12, 10)
    glPopMatrix()
    glPopMatrix()

def draw_bullet(b):
    if not b["alive"]:
        return
    glPushMatrix()
    glTranslatef(b["x"], b["y"], b["z"])
    glColor3f(1.0, 0.0, 0.0)
    glutSolidCube(BULLET_SIZE)
    glPopMatrix()

# ------------------------------
# Spawning and collision
# ------------------------------
def spawn_enemy():
    ang = random.uniform(0, 360)
    r = GRID_LENGTH * 0.85
    ex = r * math.cos(d2r(ang))
    ey = r * math.sin(d2r(ang))
    return {
        "x": ex, "y": ey, "z": 0.0,
        "radius": ENEMY_BASE_RADIUS,
        "pulse": random.uniform(0, math.pi * 2.0),
        "alive": True
    }

def reset_game():
    global score, missed, game_over, enemies, bullets, fovY
    player.update({"x": 0.0, "y": 0.0, "z": 0.0, "angle_deg": 0.0, "life": 5, "alive": True, "lying": False})
    score = 0
    missed = 0
    game_over = False
    bullets = []
    enemies = [spawn_enemy() for i in range(ENEMY_COUNT)]
    # fovY = 120

def clamp_to_bounds(x, y):
    x = max(BOUND_MIN + 10, min(BOUND_MAX - 10, x))
    y = max(BOUND_MIN + 10, min(BOUND_MAX - 10, y))
    return x, y

def bullet_hit_enemy(b, e):
    dx = b["x"] - e["x"]
    dy = b["y"] - e["y"]
    dist_xy = math.hypot(dx, dy)
    return dist_xy <= ENEMY_BASE_RADIUS

def enemy_touch_player(e):
    dx = e["x"] - player["x"]
    dy = e["y"] - player["y"]
    dist_xy = math.hypot(dx, dy)
    return dist_xy <= ENEMY_BASE_RADIUS

# ------------------------------
# Input handlers
# ------------------------------
def keyboardListener(key, x, y):
    global cheat_on, cheat_vision_on
    if game_over:
        if key == b'r':
            reset_game()
        return

    if key == b'w':
        rad = d2r(player["angle_deg"])
        nx = player["x"] + PLAYER_SPEED * -math.sin(rad)
        ny = player["y"] + PLAYER_SPEED * math.cos(rad)
        player["x"], player["y"] = clamp_to_bounds(nx, ny)
    elif key == b's':
        rad = d2r(player["angle_deg"])
        nx = player["x"] - PLAYER_SPEED * -math.sin(rad)
        ny = player["y"] - PLAYER_SPEED * math.cos(rad)
        player["x"], player["y"] = clamp_to_bounds(nx, ny)
    elif key == b'a':
        player["angle_deg"] += TURN_SPEED
    elif key == b'd':
        player["angle_deg"] -= TURN_SPEED
    elif key == b'c':
        cheat_on = not cheat_on
    elif key == b'v':
        cheat_vision_on = not cheat_vision_on
    elif key == b'r':
        reset_game()

def specialKeyListener(key, x, y):
    global cam_orbit_deg, cam_height
    if key == GLUT_KEY_UP:
        cam_height += 15.0
    elif key == GLUT_KEY_DOWN:
        cam_height -= 15.0
    elif key == GLUT_KEY_LEFT:
        cam_orbit_deg -= 2.0
    elif key == GLUT_KEY_RIGHT:
        cam_orbit_deg += 2.0

def mouseListener(button, state, x, y):
    global third_person
    if state == GLUT_DOWN:
        if button == GLUT_LEFT_BUTTON and not game_over:
            fire_bullet()
        elif button == GLUT_RIGHT_BUTTON:
            third_person = not third_person

# ------------------------------
# Actions
# ------------------------------
def fire_bullet():
    rad = d2r(player["angle_deg"])
    bx = player["x"] + 48 * -math.sin(rad)
    by = player["y"] + 48 * math.cos(rad)
    bz = 54 + 40 - 10
    bullets.append({
        "x": bx, "y": by, "z": bz,
        "dir_deg": player["angle_deg"],
        "dist": 0.0, "alive": True
    })

# ------------------------------
# Camera setup
# ------------------------------
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    fov = 150 if (not third_person and cheat_on and cheat_vision_on) else 120
    gluPerspective(fov, ASPECT, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(camera_pos[0], camera_pos[1], camera_pos[2],
              camera_target[0], camera_target[1], camera_target[2],
              0, 0, 1)

def update_camera():
    global camera_pos, camera_target
    if third_person:
        rad = d2r(cam_orbit_deg)
        cx = cam_radius * math.cos(rad)
        cy = cam_radius * math.sin(rad)
        camera_pos = (cx, cy, cam_height)
        camera_target = (0.0, 0.0, 0.0)
    else:
        eye_x = player["x"]
        eye_y = player["y"]
        eye_z = player["z"] + FP_EYE_HEIGHT

        if cheat_on and not cheat_vision_on:
            camera_pos = (eye_x, eye_y, eye_z)
            camera_target = (400, 400, eye_z)

        else:
            rad = d2r(player["angle_deg"])
            
            look_x = eye_x + 200.0 * -math.sin(rad)
            look_y = eye_y + 200.0 * math.cos(rad)
            camera_pos = (eye_x, eye_y, eye_z)
            camera_target = (look_x, look_y, eye_z)

# ------------------------------
# Game update loop
# ------------------------------
def update_game():
    global auto_fire_cooldown, score, missed, game_over
    if game_over:
        return

    if cheat_on:
        player["angle_deg"] += auto_rotate_speed
        px, py = player["x"], player["y"]
        rad = d2r(player["angle_deg"])
        dx_ray, dy_ray = -math.sin(rad), math.cos(rad)
        for e in enemies:
            ex, ey = e["x"], e["y"]
            vec_px, vec_py = ex - px, ey - py
            dot_product = vec_px * dx_ray + vec_py * dy_ray
            if dot_product > 0:
                closest_x = px + dot_product * dx_ray
                closest_y = py + dot_product * dy_ray
                dist_sq = (ex - closest_x)**2 + (ey - closest_y)**2
                if dist_sq <= (ENEMY_BASE_RADIUS**2) and auto_fire_cooldown <= 0:
                    fire_bullet()
                    auto_fire_cooldown = AUTO_FIRE_COOLDOWN_MAX
                    break
        if auto_fire_cooldown > 0:
            auto_fire_cooldown -= 1

    for e in enemies:
        if e["alive"]:
            dx = player["x"] - e["x"]
            dy = player["y"] - e["y"]
            d = math.hypot(dx, dy)
            if d > 1e-3:
                e["x"] += ENEMY_SPEED * dx / d
                e["y"] += ENEMY_SPEED * dy / d
            e["pulse"] += 0.01

    for b in bullets:
        if b["alive"]:
            rad = d2r(b["dir_deg"])
            b["x"] += BULLET_SPEED * -math.sin(rad)
            b["y"] += BULLET_SPEED * math.cos(rad)
            b["dist"] += BULLET_SPEED
            if not (BOUND_MIN < b["x"] < BOUND_MAX and BOUND_MIN < b["y"] < BOUND_MAX and b["dist"] < BULLET_MAX_DIST):
                b["alive"] = False
                missed_increment()

    # Handle collisions
    for b in bullets:
        if b["alive"]:
            for e in enemies:
                if e["alive"] and bullet_hit_enemy(b, e):
                    b["alive"] = False
                    score += 1
                    new_enemy = spawn_enemy()
                    e.update(new_enemy)
                    break

    for e in enemies:
        if e["alive"] and enemy_touch_player(e):
            player["life"] -= 1
            new_enemy = spawn_enemy()
            e.update(new_enemy)
            if player["life"] <= 0:
                set_game_over()
            break

def missed_increment():
    global missed
    missed += 1
    if missed >= 10:
        set_game_over()

def set_game_over():
    global game_over
    game_over = True
    player["alive"] = False
    player["lying"] = True

# ------------------------------
# Main display function
# ------------------------------
def showScreen():

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    update_camera()
    setupCamera()
    draw_floor_quads()
    draw_boundaries()
    draw_player()
    for e in enemies:
        draw_enemy(e)
    for b in bullets:
        draw_bullet(b)
    draw_text(10, 770, f"Player Life Remaining: {player['life']}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {missed}")
    if game_over:
        draw_text(360, 400, "GAME OVER — Press R to Restart")
    glutSwapBuffers()

def idle():
    update_game()
    glutPostRedisplay()

# ------------------------------
# Initialization and main loop
# ------------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bullet Frenzy")
    reset_game()
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()