from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random, math, time

########### Feature 7 ###############
fovY = 130
camera_radius = 900
camera_angle  = 0     
camera_height = 650   

GRID_LENGTH = 800

##### Feature 1 #####
#Corals
coral_offsets = [(-3,  2,  0),(10,  5, 0),(23,  0.8, 0)]

coral_color_y = [0, 0, 0.3]
coral_color_z = [0.2, 0.18, 0.19]
NUM_CORALS = 30
coral_positions = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10),random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10))
    for _ in range(NUM_CORALS)]
CORAL_HEIGHTS = [50, 67, 35]

#Rocks
NUM_ROCKS = 20
rock_positions = [(random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10),random.randint(-GRID_LENGTH + 10, GRID_LENGTH - 10))
    for _ in range(NUM_ROCKS)]

#Water
WATER_HEIGHT   = 300
WAVE_AMPLITUDE = 6
WAVE_FREQ      = 0.8
WAVE_SUBDIV    = 28

def draw_coral(x, y, heights):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glScalef(2.0, 2.0, 2.0)
    for i in range(3):
        ox, oy, oz = coral_offsets[i]
        glPushMatrix()
        glTranslatef(ox, oy, oz)
        glColor3f(1, coral_color_y[i], coral_color_z[i])
        gluCylinder(gluNewQuadric(), 8, 4, heights[i], 5, 4)
        glPopMatrix()
    glPopMatrix()

def draw_rock(x, y):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor3f(0.5, 0.5, 0.5)
    glutSolidCube(45)
    glTranslatef(0, 0, 30)
    glColor3f(0.55, 0.5, 0.5)
    glutSolidCube(30)
    glPopMatrix()

def draw_ocean_objects():
    for (cx, cy) in coral_positions:
        draw_coral(cx, cy, CORAL_HEIGHTS)
    for (rx, ry) in rock_positions:
        draw_rock(rx, ry)

def draw_water_volume():
    half = GRID_LENGTH
    base_z = 0.0
    top_z = base_z + WATER_HEIGHT

    wall_color = (0.68, 0.85, 0.90)

    glColor3f(*wall_color)
    glBegin(GL_QUADS)
    # +X
    glVertex3f( half, -half, base_z)
    glVertex3f( half,  half, base_z)
    glVertex3f( half,  half, top_z)
    glVertex3f( half, -half, top_z)

    # -X
    glVertex3f(-half, -half, base_z)
    glVertex3f(-half,  half, base_z)
    glVertex3f(-half,  half, top_z)
    glVertex3f(-half, -half, top_z)

    # +Y
    glVertex3f(-half,  half, base_z)
    glVertex3f( half,  half, base_z)
    glVertex3f( half,  half, top_z)
    glVertex3f(-half,  half, top_z)

    # -Y
    glVertex3f(-half, -half, base_z)
    glVertex3f( half, -half, base_z)
    glVertex3f( half, -half, top_z)
    glVertex3f(-half, -half, top_z)
    glEnd()

    #Wavy surface
    t = time.perf_counter()
    step = (half * 2.0) / float(WAVE_SUBDIV)
    start = -half

    glBegin(GL_QUADS)
    for i in range(WAVE_SUBDIV):
        for j in range(WAVE_SUBDIV):
            x0 = start + i * step
            y0 = start + j * step
            x1 = x0 + step
            y1 = y0 + step

            z00 = top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z01 = top_z + math.sin((x0*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z10 = top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y0*0.015 - t*1.5)) * WAVE_AMPLITUDE
            z11 = top_z + math.sin((x1*0.02 + t*2.0)) * WAVE_AMPLITUDE*2 + math.cos((y1*0.015 - t*1.5)) * WAVE_AMPLITUDE

            glColor3f(0.4, 0.7, 0.9) 
            glVertex3f(x0, y0, z00)
            glVertex3f(x1, y0, z10)
            glVertex3f(x1, y1, z11)
            glVertex3f(x0, y1, z01)
    glEnd()


def draw_shapes():
    draw_water_volume()
    draw_ocean_objects()


########### Feature 7 ###############

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)  
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    global camera_radius, camera_angle, camera_height

    cam_x = camera_radius * math.cos(math.radians(camera_angle))
    cam_y = camera_radius * math.sin(math.radians(camera_angle))
    cam_z = camera_height

    gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)



def specialKeyListener(key, x, y):
    global camera_height, camera_angle
    if key == GLUT_KEY_UP:
        camera_height += 20
    elif key == GLUT_KEY_DOWN:
        camera_height -= 20
    elif key == GLUT_KEY_LEFT:
        camera_angle -= 5
    elif key == GLUT_KEY_RIGHT:
        camera_angle += 5




def idle():
  glutPostRedisplay()



def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1200, 1000)
    setupCamera()
    # Ocean floor
    glBegin(GL_QUADS)
    glColor3f(1.0, 0.88, 0.65)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH,  GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glEnd()

    draw_shapes()

    glutSwapBuffers()



def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1200, 1000)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Ocean Visualizer - Floor, Corals, Rocks & Water")
    glutDisplayFunc(showScreen)
    glutSpecialFunc(specialKeyListener)

    glutIdleFunc(idle)

    glutMainLoop()

if __name__ == "__main__":
    main()
