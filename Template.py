from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

colors = { 'WHITE':(1.0, 1.0, 1.0),
        'LILAC':(0.85, 0.75, 0.95),
        'BLUE':(0.0, 0.0, 1.0),
        'CYAN':(0.0, 1.0, 1.0),
        'GREEN':(0.0, 1.0, 0.0),
        'BLACK':(0.0, 0.0, 0.0),
        'YELLOW':(1.0, 1.0, 0.0),
        'BROWN':(0.59, 0.29, 0.0) }



# Camera-related variables
camera_pos = (0,-1000,1000)

fovY = 120  # Field of view
GRID = 1000  # Length of grid lines
rand_var = 423

# Maze variables
p = 170
w = 10
b = 15
height = 300

co = []

i = 0
dist = -1000

while True:

    co += [dist]

    if i == 0:
        dist += b
    elif i==22:
        dist += b
        co += [dist]
        break
    elif i%2==1:
        dist += p
    elif i%2==0:
        dist += w
    i += 1

print(co)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top

    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def cuboids(p1, p2, p3, p4, h, color):

    glColor3f(*color)

    
    glBegin(GL_QUADS)
    
    #bottom
    # glVertex3f(p1[0], p1[1], 0)
    # glVertex3f(p2[0], p2[1], 0)
    # glVertex3f(p3[0], p3[1], 0)
    # glVertex3f(p4[0], p4[1], 0)

    #right
    glVertex3f(p4[0], p4[1], 0)
    glVertex3f(p4[0], p4[1], h)
    glVertex3f(p3[0], p3[1], h)
    glVertex3f(p3[0], p3[1], 0)

    #left
    glVertex3f(p2[0], p2[1], 0)
    glVertex3f(p2[0], p2[1], h)
    glVertex3f(p1[0], p1[1], h)
    glVertex3f(p1[0], p1[1], 0)

    #back
    glVertex3f(p2[0], p2[1], 0)
    glVertex3f(p2[0], p2[1], h)
    glVertex3f(p3[0], p3[1], h)
    glVertex3f(p3[0], p3[1], 0)

    #front
    glVertex3f(p1[0], p1[1], 0)
    glVertex3f(p1[0], p1[1], h)
    glVertex3f(p4[0], p4[1], h)
    glVertex3f(p4[0], p4[1], 0)

    #top
    glVertex3f(p1[0], p1[1], h)
    glVertex3f(p2[0], p2[1], h)
    glVertex3f(p3[0], p3[1], h)
    glVertex3f(p4[0], p4[1], h)

    glEnd()



def draw_walls():

    # #boundaries

    # #back
    # cuboids((-GRID, GRID-b), (-GRID, GRID), 
    #         (GRID, GRID),(GRID, GRID-b),
    #         height,colors['BROWN'])

    # #front
    # cuboids((-GRID, -GRID), (-GRID, -GRID+b), 
    #         (GRID, -GRID+b), (GRID, -GRID),
    #         height, colors['BROWN'])
    
    # #left
    # cuboids((-GRID, -GRID), (-GRID, GRID-2*p-b-w),
    #         (-GRID+b, GRID-2*p-b-w), (-GRID+b, -GRID),
    #         height, colors['BROWN'])
    
    # cuboids((-GRID, GRID-p-b-w), (-GRID, GRID),
    #         (-GRID+b, GRID), (-GRID+b, GRID-p-b-w),
    #         height, colors['BROWN'])
    
    # #right
    # cuboids((GRID-b, -GRID), (GRID-b, -GRID+b+p+w),
    #         (GRID, -GRID+b+p+w), (GRID, -GRID),
    #         height, colors['BROWN'])
    
    # cuboids((GRID-b, -GRID+b+2*p+w), (GRID-b, GRID),
    #         (GRID, GRID), (GRID, -GRID+b+2*p+w),
    #         height, colors['BROWN'])
    

    #boundaries

    #front

    cuboids((co[0], co[0]), (co[0], co[1]), 
            (co[23], co[1]), (co[23], co[0]), 
             height, colors["BROWN"])

    #back

    cuboids((co[0],co[22]), (co[0],co[23]), 
            (co[23],co[23]), (co[23],co[22]),
             height, colors["BROWN"])

    #left

    cuboids((co[0],co[0]), (co[0],co[19]), 
            (co[1],co[19]), (co[1],co[0]), 
             height, colors["BROWN"])
    
    cuboids((co[0],co[20]), (co[0],co[23]), 
            (co[1],co[23]), (co[1],co[20]), 
             height, colors["BROWN"])
    
    #right

    cuboids((co[22],co[0]), (co[22],co[3]), 
            (co[23],co[3]), (co[23],co[0]), 
             height, colors["BROWN"])
    
    cuboids((co[22],co[4]), (co[22],co[23]), 
            (co[23],co[23]), (co[23],co[4]), 
             height, colors["BROWN"])
    
    
def draw_shapes():

    glPushMatrix()  # Save the current matrix state
    glColor3f(1, 0, 0)
    glTranslatef(0, 0, 0)  
    glutSolidCube(60) # Take cube size as the parameter
    glTranslatef(0, 0, 100) 
    glColor3f(0, 1, 0)
    glutSolidCube(60) 

    glColor3f(1, 1, 0)
    glScalef(2, 2, 2)
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)  # parameters are: quadric, base radius, top radius, height, slices, stacks
    glTranslatef(100, 0, 100) 
    glRotatef(90, 0, 1, 0)  # parameters are: angle, x, y, z
    gluCylinder(gluNewQuadric(), 40, 5, 150, 10, 10)

    glColor3f(0, 1, 1)
    glTranslatef(300, 0, 100) 
    gluSphere(gluNewQuadric(), 80, 10, 10)  # parameters are: quadric, radius, slices, stacks

    glPopMatrix()  # Restore the previous matrix state


def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    # # Move forward (W key)
    # if key == b'w':  

    # # Move backward (S key)
    # if key == b's':

    # # Rotate gun left (A key)
    # if key == b'a':

    # # Rotate gun right (D key)
    # if key == b'd':

    # # Toggle cheat mode (C key)
    # if key == b'c':

    # # Toggle cheat vision (V key)
    # if key == b'v':

    # # Reset the game if R key is pressed
    # if key == b'r':


def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos
    x, y, z = camera_pos
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        y += 10
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        y-=10
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x -= 10  # Small angle decrement for smooth movement

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x += 10  # Small angle increment for smooth movement

    camera_pos = (x, y, z)


def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
        # # Left mouse button fires a bullet
        # if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:

        # # Right mouse button toggles camera tracking mode
        # if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:



def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 0.88, 0.1, 3000) # Think why aspect ration is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    gluLookAt(x, y, z,  # Camera position
              0, 0, 0,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)


def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()


def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 960, 1080)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Draw a random points
    glPointSize(20)
    glBegin(GL_POINTS)
    glColor3f(1,0,0)
    glVertex3f(-1000, -1000, 0)
    glColor3f(0,1,0)
    glVertex3f(-1000, 1000, 0)
    glColor3f(0,0,1)
    glVertex3f(1000, 1000, 0)
    glColor3f(1,1,1)
    glVertex3f(1000, -1000, 0)
    glEnd()

    # Draw the grid (game floor)
    glBegin(GL_QUADS)
    
    glColor3f(0.8, 0.52, 0.25)
    glVertex3f(-1000, -1000, 0)
    glVertex3f(-1000, 1000, 0)
    glVertex3f(1000, 1000, 0)
    glVertex3f(1000, -1000, 0)

    
   
    glEnd()

    draw_walls()
    # Display game info text at a fixed screen position
    # draw_text(10, 770, f"A Random Fixed Position Text")
    # draw_text(10, 740, f"See how the position and variable change?: {rand_var}")

    # draw_shapes()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()


# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Double buffering, RGB color, depth test
    glutInitWindowSize(960, 1080)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"3D OpenGL Intro")  # Create the window

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function to move the bullet automatically

    glutMainLoop()  # Enter the GLUT main loop


if __name__ == "__main__":
    main()