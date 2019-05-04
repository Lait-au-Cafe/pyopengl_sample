#version 330 core
in vec2 uvpos;
uniform sampler2D sampler;

//in vec4 v_color;
out vec4 frag_color;

void main(){
	//frag_color = vec4(1.0, 1.0, 1.0, 1.0);
	frag_color = vec4(texture(sampler, uvpos).rgb, 1.0);
}
