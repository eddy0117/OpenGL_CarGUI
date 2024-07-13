import os
import glfw
from OpenGL.GL import *
import time
import json
from tools.DrawFunctions import *
# glfw callback functions

def main():

    def window_resize(window, width, height):
        glViewport(0, 0, width, height)
        projection = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

    # Initializing glfw library
    if not glfw.init():
        raise Exception("glfw can not be initialized!")

    # Creating the window
    window = glfw.create_window(1280, 720, "My OpenGL window", None, None)

    # Check if window was created
    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

    # Set window's position
    glfw.set_window_pos(window, 400, 200)

    # Set the callback function for window resize
    glfw.set_window_size_callback(window, window_resize)

    # Make the context current
    glfw.make_context_current(window)

    view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 20]), pyrr.Vector3([0, -1, 0]), pyrr.Vector3([0, 1, 0]))
    projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)

    model, proj_loc = get_model_info(["models/SUV.obj", "models/MasCasual3.obj", "models/cube.obj", "models/cube.obj", "models/cube.obj", "models/scooter.obj", "models/sign_60.obj", "models/sign_ped.obj", "models/cone.obj"], 
                                     ["textures/SUV.jpg", "textures/ManCasual3.png", "textures/crossroad.png", "textures/roadline.png", "textures/side.png", "textures/gray_2.jpg", "textures/sign_60.png", "textures/sign_ped.png", "textures/cone.png"],
                                     view, projection)
    
    dot_dict = {
                '0' : 4, # side
                '1' : 2, # crossroad
                '2' : 3  # roadline
                }

    obj_dict = {
                'car' : 0,
                'pedestrian' : 1,
                'motorcycle' : 5,
                'sign_60' : 6,
                'sign_ped' : 7,
                'cone' : 8
                }

    t1 = None
    idx = 0
    glClearColor(0.1, 0.1, 0.1, 1)

    obj_path = 'result2ue5_add.json'
    road_dots_path = 'coord.json'

    
    with open(os.path.join('JSONfiles', obj_path), 'r') as f:
        data = json.load(f)

    with open(os.path.join('JSONfiles', road_dots_path), 'r') as f:
        coord = json.load(f)

    while not glfw.window_should_close(window):

        glfw.poll_events()

        if idx > len(list(data.keys())) - 1:
            break
        cur_frame_data = data[list(data.keys())[idx]]
        cur_coord_data = coord[list(coord.keys())[idx]]

        if not t1:
            t1 = time.time()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if time.time() - t1 > 0.2:
          
            idx += 1
            t1 = time.time()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            draw_model(model[0], 180, [0, -5, 0])

            # draw floor dots
            for dot in cur_coord_data:
                x = dot[1] / 682 * 70 - 35
                y = dot[0] / 682 * 70 - 35
          
                draw_model(model[dot_dict[str(dot[2])]], 90, [x, -5, y])


            # draw scene objects
            for obj_idx in list(cur_frame_data.keys()):
                obj = cur_frame_data[obj_idx]
                if obj['class'] not in obj_dict.keys():
                    continue
                c_x = obj['x']
                c_y = obj['y']
                x = c_x / 682 * 100 - 50
                y = c_y / 682 * 100 - 50

                draw_model(model[obj_dict[obj['class']]], obj['distance_ang'] + 90, [x, -5, y])
             

            glfw.swap_buffers(window)
        

    glfw.terminate()

if __name__ == "__main__":
    
    main()