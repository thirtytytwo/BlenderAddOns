
void main(){
    vec2 val = texture(ImageInput, uvInterp).rg;
    float dist = 1 - distance(val, uvInterp);
    dist = dist * 2 - 1;
    FragColor = vec4(dist,dist,dist, 1.0);
}