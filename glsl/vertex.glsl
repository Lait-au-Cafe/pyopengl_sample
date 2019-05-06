#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec2 vertex_uv;
//layout(location = 1) in vec4 color;

uniform mat4 mvp_matrix;

//out vec4 v_color;
out vec2 uvpos;

void main(){
	//gl_Position = mvp_matrix * vec4(position, 1);
	vec4 pos = mvp_matrix * vec4(position, 1);
	gl_Position = vec4(pos.x / pos.z, pos.y / pos.z, 0, 1);
	uvpos = vertex_uv;
}
