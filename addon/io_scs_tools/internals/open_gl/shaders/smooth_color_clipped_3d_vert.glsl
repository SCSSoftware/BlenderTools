uniform mat4 ModelViewProjectionMatrix;

#ifdef USE_WORLD_CLIP_PLANES
uniform mat4 ModelMatrix;
#endif

in vec3 pos;
in vec4 color;

out vec4 finalColor;
out vec4 vertexPos;

void main()
{
    vertexPos = vec4(pos, 1.0);
    gl_Position = ModelViewProjectionMatrix * vertexPos;
    finalColor = color;

#ifdef USE_WORLD_CLIP_PLANES
    world_clip_planes_calc_clip_distance((ModelMatrix * vec4(pos, 1.0)).xyz);
#endif
}