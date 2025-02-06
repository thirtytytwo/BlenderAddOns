
void main() {
    float distA = texture(SDFA, uvInterp).r;
    distA = pow(distA, 1.0 / 2.2) * 2.0 - 1.0;
    float distB = texture(SDFB, uvInterp).r;
    distB = pow(distB, 1.0 / 2.2) * 2.0 - 1.0;
    vec3 result = vec3(0.0);
    if(distA < 0.0){
        result = vec3(1.0);
    }
    else if(distB > 0.0){
        result = vec3(0.0);
    }
    else{
        float val = clamp(abs(distB) / (abs(distA) + abs(distB)),0.0, 1.0);
        result = vec3(val);
    }

    if(flag == 1){
        float pre = texture(Pre, uvInterp).r;
        result *= weight;
        result += vec3(pre);
    }
    else{
        result *= weight;
    }
    FragColor = vec4(result, 1.0);
}