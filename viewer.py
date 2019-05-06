import sys
import dataclasses
import numpy as np
import cv2
import OpenGL.GL as gl
import glfw
import glm
import ctypes

@dataclasses.dataclass
class CameraProperty:
            translation: glm.vec3
            rotation: glm.vec3
            focal_length: float
            clipping_distance: glm.vec2
            field_of_view: float


class Viewer:
    @staticmethod
    def on_error(code, message):
        """
        @fn on_error()
        @brief Callback function invoked when glfw encounters errors. 
        """
        print("[GLFW Error] {} ({})".format(message, code))

    @staticmethod
    def load_shader(shader_id, filename):
        """
        @fn load_shader()
        @brief Load shader script from file. 
        """
        with open(filename) as shader_file:
            shader_code = shader_file.read()
            gl.glShaderSource(shader_id, [shader_code])
            gl.glCompileShader(shader_id)

            result = gl.glGetShaderiv(shader_id, gl.GL_COMPILE_STATUS)
            if result != gl.GL_TRUE:
                print("[GLFW Error] {}".format(gl.glGetShaderInfoLog(shader_id)))
                return False

        return True

    def update_camera_posture(self):
        pass

    def mouse_callback(self, window, xpos, ypos):
        #print("[Left: {}] [Right: {}] ({}, {})".format(
        #    glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_LEFT), 
        #    glfw.get_mouse_button(self.window, glfw.MOUSE_BUTTON_RIGHT), 
        #    xpos,  ypos))
        pass

    def __init__(self, model_vertices, model_uvmap, texture_filename, window_title):
        """
        @fn __init__()
        @brief Initialization. 
        """
        print("Initializing Viewer...")

        # set callback function on error
        glfw.set_error_callback(Viewer.on_error)

        # Initialize
        if glfw.init() != gl.GL_TRUE:
            print("[GLFW Error] Failed to initialize GLFW. ")
            sys.exit()

        #========================================
        # Prepare Window
        #========================================
        # Window hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

        # Create window
        self.window_size = (640, 480)
        self.window = glfw.create_window(
                self.window_size[0],  # width
                self.window_size[1],  # height
                window_title,  # window title
                None, 
                None)

        if self.window == None:
            print("[GLFW Error] Failed to Create a window. ")
            sys.exit()

        # Create OpenGL context
        glfw.make_context_current(self.window)

        # Set background color.
        gl.glClearColor(0.0, 1.0, 1.0, 1.0)

        #gl.glViewport(0, 0, 480, 480)

        # Set callback functions
        glfw.set_cursor_pos_callback(self.window, self.mouse_callback)

        #========================================
        # Prepare Buffers
        #========================================
        # --- Vertex buffer ---
        # Generate & bind buffer
        vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)

        # Allocate memory
        c_vertex_buffer = (ctypes.c_float*len(model_vertices))(*model_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, c_vertex_buffer, gl.GL_STATIC_DRAW)
        size_expected = ctypes.sizeof(ctypes.c_float) * len(model_vertices)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != size_expected:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, vertex_buffer);
            sys.exit()

        # --- UV buffer ---
        # Generate & bind buffer
        uv_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, uv_buffer)

        # Allocate memory
        c_uv_buffer = (ctypes.c_float*len(model_uvmap))(*model_uvmap)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, c_uv_buffer, gl.GL_STATIC_DRAW)
        size_expected = ctypes.sizeof(ctypes.c_float) * len(model_uvmap)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != size_expected:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, uv_buffer);
            sys.exit()

        # --- Bind to vertex array object ---
        self.va_object = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.va_object)

        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glEnableVertexAttribArray(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, uv_buffer)
        gl.glVertexAttribPointer(1, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        #========================================
        # Prepare Texture
        #========================================
        # Load image
        image = cv2.imread(texture_filename)
        if image is None:
            print("[CV Error] Cannot open image: {}".format(texture_filename))
            sys.exit()
        image = cv2.flip(image, 0)

        # Create texture
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        # Generate texture
        gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
        gl.glTexImage2D(
                gl.GL_TEXTURE_2D,  # target texture
                0,  # Mipmap Level
                gl.GL_RGBA,  # The number of color components in the texture
                image.shape[1],  # the width of texture
                image.shape[0],  # the height of texture
                0,  # border (this value must be 0)
                gl.GL_BGR,  # the format of the pixel data
                gl.GL_UNSIGNED_BYTE,  # the type of pixel data
                image)  # a pointer to the image

        # Set parameters
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_BORDER)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_BORDER)

        # Unbind
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        #========================================
        # Prepare Camera Parameter Matrix
        #========================================
        self.camera_property = CameraProperty(
            translation = glm.vec3(0., 0., 10.), 
            rotation = glm.vec3(0., 0., 0.), 
            focal_length = 20., 
            clipping_distance = glm.vec2(0.1, 100.), 
            field_of_view = 60.)

        # Transform matrix
        trans = self.camera_property.translation
        rot = self.camera_property.rotation
        transform_matrix = glm.mat4(1.)
        transform_matrix = glm.translate(transform_matrix, trans)
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.x), glm.vec3(1., 0., 0.))
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.y), glm.vec3(0., 1., 0.))
        transform_matrix = glm.rotate(transform_matrix, glm.radians(rot.z), glm.vec3(0., 0., 1.))

        # Perspective matrix
        perspective_matrix = glm.perspectiveFovLH_NO(
                glm.radians(self.camera_property.field_of_view), 
                self.window_size[0], self.window_size[1], 
                self.camera_property.clipping_distance[0], 
                self.camera_property.clipping_distance[1])

        # MVP matrix
        #mvp_matrix = perspective_matrix * glm.lookAt(glm.vec3(0, 0, -5), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0)) * transform_matrix
        mvp_matrix = perspective_matrix * transform_matrix

        #========================================
        # Prepare Shader Programs
        #========================================
        is_loaded: bool = False

        vert_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        is_loaded = Viewer.load_shader(vert_shader, "glsl/vertex.glsl")
        if not is_loaded: sys.exit()

        frag_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        is_loaded = Viewer.load_shader(frag_shader, "glsl/fragment.glsl")
        if not is_loaded: sys.exit()

        # Create shader program
        self.shader_program = gl.glCreateProgram()

        # Bind shader objects
        gl.glAttachShader(self.shader_program, vert_shader)
        gl.glAttachShader(self.shader_program, frag_shader)
        gl.glDeleteShader(vert_shader)
        gl.glDeleteShader(frag_shader)

        # Link shader program
        gl.glLinkProgram(self.shader_program)
        result = gl.glGetProgramiv(self.shader_program, gl.GL_LINK_STATUS)
        if result != gl.GL_TRUE:
            print("[GLFW Error] {}".format(gl.glGetShaderInfoLog(shader_id)))
            sys.exit()

        # Specify uniform variables
        gl.glUseProgram(self.shader_program)
        gl.glUniform1i(gl.glGetUniformLocation(self.shader_program, "sampler"), 0)
        for i in range(0, len(model_vertices), 3):
            pos = mvp_matrix * glm.vec4(
                    model_vertices[i], model_vertices[i+1], model_vertices[i+2],  1.)
            print(np.array([pos.x, pos.y, pos.z, pos.w]))
            print(np.array([pos.x, pos.y, pos.z]) / pos.w)
            print(np.array([pos.x, pos.y]) / pos.z)
        gl.glUniformMatrix4fv(gl.glGetUniformLocation(self.shader_program, "mvp_matrix"), 
                1, gl.GL_FALSE, glm.value_ptr(perspective_matrix))

    def update(self):
        """
        @fn update()
        @brief Update Buffer
        """
        #========================================
        # Mouse and Keyboard response
        #========================================
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            return False


        #========================================
        # Draw new buffer
        #========================================
        # Initialize
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        #gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE);

        # Bind program
        gl.glUseProgram(self.shader_program)

        # Bind buffer
        gl.glBindVertexArray(self.va_object)

        # Bind buffer
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        # Draw
        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, len(model_vertices) // 3)

        # Unbind
        gl.glBindVertexArray(0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, 0)

        # Update
        glfw.swap_buffers(self.window)
        glfw.poll_events()

        return glfw.window_should_close(self.window) != gl.GL_TRUE
        

# Sample Code
if __name__ == "__main__":
    #model_vertices = [
    #     0.5,  0.5, 0.0, 
    #    -0.5,  0.5, 0.0, 
    #     0.5, -0.5, 0.0, 
    #    -0.5, -0.5, 0.0]
    model_vertices = [
         10,  10, 50.0, 
        -10,  10, 50.0, 
         10, -10, 50.0, 
        -10, -10, 50.0]

    model_uvmap = [
        1.0, 1.0, 
        0.0, 1.0, 
        1.0, 0.0, 
        0.0, 0.0]

    viewer = Viewer(model_vertices, model_uvmap, "img/invader.png", "Sample")
    while True:
        if not viewer.update():
            print("Exit. ")
            break
