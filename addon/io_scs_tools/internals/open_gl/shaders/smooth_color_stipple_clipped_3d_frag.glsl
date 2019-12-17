in vec4 vertexColor;
flat in vec4 startVertexPos;
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

    if (step(sin(length(vertexPos - startVertexPos) * 100), 0.4) == 1) discard;

    fragColor = vertexColor;
}
