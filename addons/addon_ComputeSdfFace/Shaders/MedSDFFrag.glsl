void main(){
    float val = dot(normalInterp, lightDir);
    val = step(0.5, val);
    vec3 result = vec3(val, val, val);
    if(flag == 1){
        float lastTexColor = texture(ImageInput, uvInterp).r;
        result = clamp(result + lastTexColor, 0.0, 1.0);
    }
    FragColor = vec4(result, 1.0);
}