
void main() {
    vec3 result = vec3(0, 0, 0);
    float face = texture(Face, uvInterp).r;
    float distA = texture(SDFA, uvInterp).r;
    float distB = texture(SDFB, uvInterp).r;
    result = mix(vec3(1,1,1), vec3(0,0,0), distB- distA) * face;

    if(flag==1){
        vec3 pre = texture(Pre, uvInterp).rgb;
        result = result * weight + pre;
    }
    else{
        result = result * weight;
    }
    FragColor = vec4(result, 1.0);
}