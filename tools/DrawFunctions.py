from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import pyrr
from tools.TextureLoader import load_texture
from tools.ObjLoader import ObjLoader
import math

def get_model_info(model_paths, texture_paths=None, view=None, projection=None):
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

        # projection = pyrr.matrix44.create_perspective_projection_matrix(45, 1280 / 720, 0.1, 100)
        

        model_loc = glGetUniformLocation(shader, "model")
        proj_loc = glGetUniformLocation(shader, "projection")
        view_loc = glGetUniformLocation(shader, "view")


        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        result.append({'model_loc' : model_loc, 'indices': model_indices, 'VAO' : VAO[idx], 'textures' : textures[idx]})

    return result, proj_loc

def deg2rad(deg):
    return deg * math.pi / 180

def draw_model(model_info, deg, model_pos):
    rot_y = pyrr.Matrix44.from_y_rotation(-deg2rad(deg))
    pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(model_pos))
    # load_texture(model_info['texture_path'], model_info['textures'][0])
    glBindVertexArray(model_info['VAO'])
    glBindTexture(GL_TEXTURE_2D, model_info['textures'])
    # glBindVertexArray(model_info['VBO'])
    model_transform = pyrr.matrix44.multiply(rot_y, pos)
    glUniformMatrix4fv(model_info['model_loc'], 1, GL_FALSE, model_transform)
    glDrawArrays(GL_TRIANGLES, 0, len(model_info['indices']))

