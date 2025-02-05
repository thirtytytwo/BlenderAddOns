
void main() {
    float distA = texture(SDFA, uvInterp).r;
    distA = pow(distA, 1.0 / 2.2);
    float distB = texture(SDFB, uvInterp).r * 2.0 - 1.0;
    distB = pow(distB, 1.0 / 2.2);

    FragColor = vec4(distB - distA, 0, 0, 1.0);
}