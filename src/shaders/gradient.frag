#version 330

uniform vec2 resolution;
varying vec2 uv;
out vec4 outColor;


void main()
{
    vec3 topColor = vec3(1, 0, 0);
    vec3 bottomColor = vec3(0, 1, 0);
	
    float dominanceFactor = smoothstep(0.3, 0.8, uv.y);
	
    vec3 gradientColor = mix(topColor, bottomColor, dominanceFactor);
	
    // Output the final color
    outColor = vec4(gradientColor, 1.0);
}
