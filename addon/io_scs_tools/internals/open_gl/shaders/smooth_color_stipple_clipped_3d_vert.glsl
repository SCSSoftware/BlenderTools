void main()
{
    // startVertexPos is flat (uninterpolated provoking vertex), to be able to calculate position on line
    startVertexPos = vec4(pos, 1.0);
    vertexPos = startVertexPos;
    vertexColor = color;

    gl_Position = ModelViewProjectionMatrix * vertexPos;
}
