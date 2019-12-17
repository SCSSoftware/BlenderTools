in vec4 finalColor;
in vec4 vertexPos;
out vec4 fragColor;

uniform vec4 clip_planes[6];
uniform int num_clip_planes;

void main()
{
    for (int i=0; i<num_clip_planes; ++i) {
        float d = dot(clip_planes[i], vertexPos);
        if (d < 0.0) discard;
    }
    fragColor = finalColor;
}