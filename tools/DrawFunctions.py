import math

import pyrr
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from tools.ObjLoader import ObjLoader
from tools.TextureLoader import load_texture, load_texture_by_color
import numpy as np

class DrawFunctions:
    model_path_prefix = "src/models/"
    texture_path_prefix = "src/textures/"
    offset = 0.3
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
            gl_PointSize = 10.0;
        }
        """

    fragment_src = """
        # version 330
        in vec2 v_texture;
        out vec4 out_color;
        out vec4 fragColor;
        uniform sampler2D s_texture;
        void main()
        {
            out_color = texture(s_texture, v_texture);
            fragColor = vec4(0.5, 0.5, 0.5, 0.5);  // 白色
        }
        """
    
    @classmethod
    def get_model_info(cls, model_dict, view=None, projection=None):
        result = {}

        buf_arr_len = len(model_dict)

        shader = compileProgram(
            compileShader(cls.vertex_src, GL_VERTEX_SHADER),
            compileShader(cls.fragment_src, GL_FRAGMENT_SHADER),
        )

        cls.shader = shader

        VAO = glGenVertexArrays(buf_arr_len)
        VBO = glGenBuffers(buf_arr_len)

        for idx, (model_name, model_content) in enumerate(model_dict.items()):
            model_indices, model_buffer = ObjLoader.load_model(
                cls.model_path_prefix + model_content[0]
            )

            glBindVertexArray(VAO[idx])
            glBindBuffer(GL_ARRAY_BUFFER, VBO[idx])
            glBufferData(
                GL_ARRAY_BUFFER, model_buffer.nbytes, model_buffer, GL_STATIC_DRAW
            )

            # Vertices
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(
                0, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(0)
            )
            # Textures
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(
                1, 2, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(12)
            )
            # Normals
            glEnableVertexAttribArray(2)
            glVertexAttribPointer(
                2, 3, GL_FLOAT, GL_FALSE, model_buffer.itemsize * 8, ctypes.c_void_p(20)
            )

            texture_buf = glGenTextures(buf_arr_len)

            load_texture(cls.texture_path_prefix + model_content[1], texture_buf[idx])

            glUseProgram(shader)

            glEnable(GL_DEPTH_TEST)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            model_loc = glGetUniformLocation(shader, "model")
            proj_loc = glGetUniformLocation(shader, "projection")
            view_loc = glGetUniformLocation(shader, "view")

            glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)
            glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
            result[model_name] = {
                "model_loc": model_loc,
                "indices": model_indices,
                "VAO": VAO[idx],
                "textures": texture_buf[idx],
            }

            cls.dot_vao, cls.dot_vbo = cls.init_occdot_vbo_vao()

        return result, proj_loc, view_loc

    @staticmethod
    def deg2rad(deg):
        return deg * math.pi / 180

    @classmethod
    def draw_model(cls, model_info, deg, model_pos):
        # model yaw rotation
        rot_y = pyrr.Matrix44.from_y_rotation(-cls.deg2rad(deg))

        # model position
        pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(model_pos))

        glBindVertexArray(model_info["VAO"])
        glBindTexture(GL_TEXTURE_2D, model_info["textures"])

        model_transform = pyrr.matrix44.multiply(rot_y, pos)
        glUniformMatrix4fv(model_info["model_loc"], 1, GL_FALSE, model_transform)

        glDrawArrays(GL_TRIANGLES, 0, len(model_info["indices"]))

    @classmethod
    def init_occdot_vbo_vao(cls):
        
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        # glBufferData(GL_ARRAY_BUFFER, points_array.nbytes, points_array, GL_DYNAMIC_DRAW)
        
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        
        # 位置屬性
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        # 顏色屬性
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        
        return vao, vbo


    @staticmethod
    def draw_dot(model_info, model_pos):
        glBindVertexArray(model_info["VAO"])

        pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(model_pos))

        glBindTexture(GL_TEXTURE_2D, model_info["textures"])
        glUniformMatrix4fv(model_info["model_loc"], 1, GL_FALSE, pos)

        glDrawArrays(GL_TRIANGLES, 0, len(model_info["indices"]))

    # @staticmethod
    # def draw_dot(model_info, positions):
      
    #     glBindVertexArray(model_info["VAO"])
    #     glBindTexture(GL_TEXTURE_2D, model_info["textures"])
        
    #     for position in positions:
    #         pos = pyrr.matrix44.create_from_translation(pyrr.Vector3(position))
    #         glUniformMatrix4fv(model_info["model_loc"], 1, GL_FALSE, pos)
    #         glDrawArrays(GL_TRIANGLES, 0, len(model_info["indices"]))

    
    @classmethod
    def draw_occ_dot(cls, colors, c, positions):
        """
        批量繪製點的優化版本
        
        Args:
            model_info: 模型信息字典
            positions: numpy數組形狀為 (N, 3) 的點位置數組
        """


        points_array = np.array(positions, dtype=np.float32)
        # glUseProgram(cls.shader)
        # 位置屬性

        points_array[:, :2] = (points_array[:, :2] - 100) / 1.2
        points_array[:, 1] = -points_array[:, 1]
        points_array[:, 2] = points_array[:, 2] - 15
        points_array[:, 2], points_array[:, 1] = points_array[:, 1], points_array[:, 2].copy()

        glBindVertexArray(cls.dot_vao)
        # glBindVertexArray(model_info["VAO"])
        # glBindTexture(GL_TEXTURE_2D, model_info["textures"])
        glBindTexture(GL_TEXTURE_2D, colors[c])

        model_loc = glGetUniformLocation(cls.shader, "model")
        rotation = pyrr.Matrix44.from_y_rotation(-cls.deg2rad(0))
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, rotation)

        glPointSize(8)
            
        # 绑定缓冲区并更新数据
        glBindBuffer(GL_ARRAY_BUFFER, cls.dot_vbo)
        glBufferData(GL_ARRAY_BUFFER, points_array.nbytes, points_array, GL_DYNAMIC_DRAW)

        
        # BUG: 在 z 軸太遠的地方繪製的畫會出現在 (0, 0, 0)位置
        glDrawArrays(GL_POINTS, 0, len(points_array))
        # glDrawArraysInstanced(GL_TRIANGLES, 0, len(model_info["indices"]), len(points_array))
        glBindVertexArray(0)
        
        
    @staticmethod
    def draw_line(model_info, x_list, z_list, y_list):
        glBindTexture(GL_TEXTURE_2D, model_info["textures"])
        # glColor3f(1, 1, 1)
        glBegin(GL_LINES)

        for idx, (x, z, y) in enumerate(zip(x_list, z_list, y_list)):
            if idx == 0:
                last_pts = (x, z, y)
            else:
                glVertex3f(last_pts[0], last_pts[1], last_pts[2])
                glVertex3f(x, z, y)
                last_pts = (x, z, y)
        glEnd()

    @classmethod
    def draw_traj_pred(cls, colors, x_list, z_list, y_list):
        for idx, (x, z, y) in enumerate(zip(x_list, z_list, y_list)):
            x += cls.offset
            y += cls.offset
            z += cls.offset
            if idx == 0:
                last_pts = (x, z, y)
            else:
                glBindTexture(GL_TEXTURE_2D, colors[idx % len(colors)])
                glBegin(GL_LINES)
                glVertex3f(last_pts[0], last_pts[1], last_pts[2])
                glVertex3f(x, z, y)
                glVertex3f(last_pts[0] + 0.3, last_pts[1], last_pts[2])
                glVertex3f(x + 0.3, z, y)
                last_pts = (x, z, y)
                glEnd()

    @staticmethod
    def get_colors(colors):
        texture_buf = glGenTextures(len(colors))
        for idx, color in enumerate(colors):
            load_texture_by_color(texture_buf[idx], color)

        return texture_buf
