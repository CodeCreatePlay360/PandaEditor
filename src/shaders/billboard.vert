#version 330

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texCoord;

uniform mat4 p3d_ModelViewMatrix;
uniform mat4 p3d_ModelMatrix;
uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ViewMatrix;  // Adding view matrix
uniform float scale;


void main() {
    // Extract the rotation part of the view matrix and invert it
    mat3 viewRotation = mat3(p3d_ViewMatrix);
    mat3 invViewRotation = transpose(viewRotation);

    // Apply the inverse view rotation to the position
    vec3 billboardPos = invViewRotation * p3d_Vertex.xzy * scale;

    // Translate the billboard position to its world position
    vec4 worldPosition = p3d_ModelMatrix * vec4(-billboardPos, 1.0);

    // Project the world position to clip space
    gl_Position = p3d_ProjectionMatrix * p3d_ViewMatrix * worldPosition;

    // Pass the texture coordinates to the fragment shader
    texCoord = p3d_MultiTexCoord0;
}
