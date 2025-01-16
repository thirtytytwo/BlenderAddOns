
void main(){
    float sampleStep = 1.0 / float(textureCount);
    float val = 0;
    if(flag == 0){
        float sdfVal = texture(SDF, uvInterp).r;
        val = (1.0f - sdfVal) * sampleStep;
    }
    else{
        float sdfVal = texture(SDF, uvInterp).r;
        val = texture(Pre, uvInterp).r;
        val += ((1.0f - sdfVal) * sampleStep);
    }
    FragColor = vec4(val, val, val, 1.0);
}