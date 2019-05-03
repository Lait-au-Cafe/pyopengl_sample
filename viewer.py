import sys
import OpenGL.GL as gl
import glfw
import ctypes

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

    def __init__(self, window_title = ""):
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

        # Window hints
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

        # Create window
        self.window = glfw.create_window(
                640,  # width
                480,  # height
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

        #========================================
        # Prepare Buffers
        #========================================
        self.model_vertices = [
                0.0, 0.5, 0.0, 
                0.5, -0.5, 0.0, 
                -0.5, -0.5, 0.0]

        # Generate & bind buffer
        vertex_buffer = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)

        # Allocate memory
        c_vertex_buffer = (ctypes.c_float*len(self.model_vertices))(*self.model_vertices)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, c_vertex_buffer, gl.GL_STATIC_DRAW)
        size_expected = ctypes.sizeof(ctypes.c_float) * len(self.model_vertices)
        size_allocated = gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE)

        if size_allocated != size_expected:
            print("[GL Error] Failed to allocate memory for buffer. ")
            gl.glDeleteBuffers(1, vertex_buffer);
            sys.exit()

        # Bind to vertex array object
        self.va_object = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(self.va_object)
        gl.glEnableVertexAttribArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertex_buffer)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)

        gl.glBindVertexArray(0)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

    def update(self):
        """
        @fn update()
        @brief Update Buffer
        """
        # Initialize
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Bind program
        gl.glUseProgram(self.shader_program)

        # Bind buffer
        gl.glBindVertexArray(self.va_object)

        # Draw
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

        # Unbind
        gl.glBindVertexArray(0)

        # Update
        glfw.swap_buffers(self.window)
        glfw.poll_events()

        return glfw.window_should_close(self.window) != gl.GL_TRUE
        

# Sample Code
if __name__ == "__main__":
    viewer = Viewer("Sample")
    while True:
        if not viewer.update():
            print("Exit. ")
            break