void main(){
    vec2 val = texture(ImageInput, uvInterp).rg;
    float dist = pow(length(val - uvInterp), 0.4);
    FragColor = vec4(dist,dist,dist, 1.0);
}