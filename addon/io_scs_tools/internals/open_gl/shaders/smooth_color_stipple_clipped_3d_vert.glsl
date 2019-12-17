uniform mat4 ModelViewProjectionMatrix;

in vec3 pos;
in vec4 color;

out vec4 vertexColor;
flat out vec4 startVertexPos;  // use uninterpolated provoking vertex, to be able to calculate position on line
out vec4 vertexPos;

void main()
{
    startVertexPos = vec4(pos, 1.0);
    vertexPos = startVertexPos;
    vertexColor = color;

    gl_Position = ModelViewProjectionMatrix * vertexPos;
}
