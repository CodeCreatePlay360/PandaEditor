#version 330

uniform sampler2D p3d_Texture0;
uniform vec3 gizmoColor;
uniform float colorIntensity; // Input parameter to control the intensity of the white color
in vec2 texCoord;
out vec4 fragColor;


void main() 
{
    // Sample the texture
    vec4 texColor = texture(p3d_Texture0, texCoord);
	
    if(texColor.a < 0.1)
		discard;
	
	vec3 finalColor = clamp(texColor.rgb*colorIntensity, 0.0, 1.0);
	fragColor = vec4(finalColor*gizmoColor, 1.0);
}
