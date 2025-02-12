void main() {
    vec2 tex_offset = 1.0 / textureSize(ImageInput, 0); // gets size of single texel
    vec3 result = vec3(0.0);

    // kernel definition (3x3 Gaussian blur)
    float kernel[9] = float[](
        1.0 / 16, 2.0 / 16, 1.0 / 16,
        2.0 / 16, 4.0 / 16, 2.0 / 16,
        1.0 / 16, 2.0 / 16, 1.0 / 16
    );
    
    // sample from texture and apply kernel
    for (int i = -1; i <= 1; i++) {
        for (int j = -1; j <= 1; j++) {
            vec2 offset = vec2(float(i), float(j)) * tex_offset;
            result += texture(ImageInput, uvInterp + offset).rgb * kernel[(i+1) * 3 + (j+1)];
        }
    }

    FragColor = vec4(result, 1.0);
}