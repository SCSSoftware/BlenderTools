void main()
{
    vertexPos = vec4(pos, 1.0);
    gl_Position = ModelViewProjectionMatrix * vertexPos;
    finalColor = color;
}
