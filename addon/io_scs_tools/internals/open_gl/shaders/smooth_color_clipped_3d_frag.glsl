void main()
{
    for (int i = 0; i < num_clip_planes; ++i) {
        float d = dot(clip_planes[i], vertexPos);
        if (d < 0.0) discard;
    }
    fragColor = finalColor;
}
