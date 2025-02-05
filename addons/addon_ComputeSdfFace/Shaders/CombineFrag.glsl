
void main() {
    float distA = texture(SDFA, uvInterp).r * 2.0 - 1.0;
    float distB = texture(SDFB, uvInterp).r * 2.0 - 1.0;
    vec3 result = vec3(0,0,0);
    if(distA < -0.5){
        result = vec3(1,1,1);
    }
    FragColor = vec4(result, 1.0);
}