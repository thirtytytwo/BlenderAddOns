void main(){
    vec2 val = texture(ImageInput, uvInterp).rg;
    float dist = 1 - length(val - uvInterp);
    FragColor = vec4(dist,dist,dist, 1.0);
}