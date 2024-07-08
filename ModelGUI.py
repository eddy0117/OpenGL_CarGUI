import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from TextureLoader import load_texture
from ObjLoader import ObjLoader
import math
import time
import json

# glfw callback functions
def window_resize(window, width, height, proj_loc):
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

def get_model_info(model_paths, texture_paths=None):
    vertex_src = """
    # version 330
    layout(location = 0) in vec3 a_position;
    layout(location = 1) in vec2 a_texture;
    layout(location = 2) in vec3 a_normal;
    uniform mat4 model;
    uniform mat4 projection;
    uniform mat4 view;
    out vec2 v_texture;
    void main()
    {
        gl_Position = projection * view * model * vec4(a_position, 1.0);
        v_texture = a_texture;
    }
    """

    fragment_src = """
    # version 330
    in vec2 v_texture;
    out vec4 out_color;
    uniform sampler2D s_texture;
    void main()
    {
        out_color = texture(s_texture, v_texture);
    }
    """

    result = []

   

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
    VAO = glGenVertexArrays(len(model_paths))
    VBO = glGenBuffers(len(model_paths))
    # print(len(model_paths), len(texture_paths))
    for idx, (model_path, texture_path) in enumerate(zip(model_paths, texture_paths)):

        model_indices, model_buffer = ObjLoader.load_model(model_path)
        

        
        glBindVertexArray(VAO[idx])
        glBindBuffer(GL_ARRAY_BUFFER, VBO[idx])
        glBufferData(GL_ARRAY_BUFFER, model_buffer.nbytes, model_buffer, GL_STATIC_DRAW)

        # Vertices
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(0))
        # Textures
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(12))
        # Normals
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(20))

        textures = glGenTextures(len(model_paths))
        load_texture(texture_path, textures[idx])
        

        glUseProgram(shader)
     
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
        view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 25]), pyrr.Vector3([0, -1, 0]), pyrr.Vector3([0, 1, 0]))

        model_loc = glGetUniformLocation(shader, "model")
        proj_loc = glGetUniformLocation(shader, "projection")
        view_loc = glGetUniformLocation(shader, "view")


        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        result.append({'model_loc' : model_loc, 'indices': model_indices, 'VAO' : VAO[idx], 'textures' : textures[idx]})

    return result

def draw_model(model_info, rot_y, model_pos):
    
    # load_texture(model_info['texture_path'], model_info['textures'][0])
    glBindVertexArray(model_info['VAO'])
    glBindTexture(GL_TEXTURE_2D, model_info['textures'])
    # glBindVertexArray(model_info['VBO'])
    model_transform = pyrr.matrix44.multiply(rot_y, model_pos)
    glUniformMatrix4fv(model_info['model_loc'], 1, GL_FALSE, model_transform)
    glDrawArrays(GL_TRIANGLES, 0, len(model_info['indices']))

def deg2rad(deg):
    return deg * math.pi / 180

if __name__ == "__main__":

    model = get_model_info(["models/SVR.obj", "models/MasCasual3.obj", "models/cube.obj"], ["textures/car_jeep_ren.jpg", "textures/ManCasual3.png", "textures/cube.png"])
    
    t1 = None
    idx = 0
    glClearColor(0.3, 0.3, 0.3, 1)
    

    
    with open('result2ue5.json', 'r') as f:
        data = json.load(f)

    with open('coord.json', 'r') as f:
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

        if time.time() - t1 > 0.1:
            r = pyrr.Matrix44.from_y_rotation(math.pi)
            idx += 1
            t1 = time.time()
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            draw_model(model[0], pyrr.Matrix44.from_y_rotation(deg2rad(180)), pyrr.matrix44.create_from_translation(pyrr.Vector3([0, -5, 0])))

            for dot in cur_coord_data:
                x = dot[1] / 682 * 70 - 35
                y = dot[0] / 682 * 70 - 35
                if dot[2] == 0:
                    draw_model(model[2], pyrr.Matrix44.from_y_rotation(-deg2rad(90)), pyrr.matrix44.create_from_translation(pyrr.Vector3([x, -5, y])))


            for obj_idx in list(cur_frame_data.keys()):
                obj = cur_frame_data[obj_idx]
                if obj['class'] == 'car':
                    c_x = obj['x']
                    c_y = obj['y']
                    x = c_x / 682 * 100 - 50
                    y = c_y / 682 * 100 - 50
                    draw_model(model[0], pyrr.Matrix44.from_y_rotation(-deg2rad(obj['distance_ang'] + 90)), pyrr.matrix44.create_from_translation(pyrr.Vector3([x, -5, y])))
                elif obj['class'] == 'pedestrian':
                    c_x = obj['x']
                    c_y = obj['y']
                    x = c_x / 682 * 100 - 50
                    y = c_y / 682 * 100 - 50
                    draw_model(model[1], pyrr.Matrix44.from_y_rotation(-deg2rad(obj['distance_ang'] + 90)), pyrr.matrix44.create_from_translation(pyrr.Vector3([x, -5, y])))

            glfw.swap_buffers(window)
        

    glfw.terminate()
