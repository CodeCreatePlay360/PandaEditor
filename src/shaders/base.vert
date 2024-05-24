# version 330

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texCoord;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()
{
	gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
	texCoord = p3d_MultiTexCoord0;
}
