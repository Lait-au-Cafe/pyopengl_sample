#version 330 core

layout(location = 0) in vec4 position;
layout(location = 1) in vec2 vertex_uv;
//layout(location = 1) in vec4 color;

//out vec4 v_color;
out vec2 uvpos;

void main(){
//	v_color = color;
	gl_Position = vec4(position.xyz, 1.0);
	uvpos = vertex_uv;
}
