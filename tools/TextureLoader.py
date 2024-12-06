import numpy as np
from OpenGL.GL import (GL_LINEAR, GL_REPEAT, GL_RGBA, GL_TEXTURE_2D,
                       GL_TEXTURE_MAG_FILTER, GL_TEXTURE_MIN_FILTER,
                       GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T, GL_UNSIGNED_BYTE,
                       glBindTexture, glTexImage2D, glTexParameteri)
from PIL import Image


# for use with GLFW
def load_texture(path, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image
    image = Image.open(path)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = image.convert("RGBA").tobytes()
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return texture

def load_texture_by_color(texture, color):
    glBindTexture(GL_TEXTURE_2D, texture)
    # Set the texture wrapping parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    # Set texture filtering parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    # load image
    img_frame = Image.open('src/textures/cube4m_frame.png').transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
    img_shadow = Image.open('src/textures/cube4m_shadow.png').transpose(Image.FLIP_TOP_BOTTOM).convert("RGBA")
    color = Image.new('RGBA', (img_frame.height, img_frame.width), tuple(color))
    # color cover image
    image = Image.blend(img_frame, color, 0.7)
    image = Image.blend(img_shadow, image, 0.8)
    # image = Image.alpha_composite(image, color)
    # image.paste(color, (0, 0), color)
    # image = color
    img_data = image.tobytes()
    # img_data = image.convert("RGBA").tobytes()
    # pil create array
    # print(color)
   
    # image = Image.fromarray(np.array(color, dtype='uint8')).convert("RGBA").tobytes()
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
    return texture