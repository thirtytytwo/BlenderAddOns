
void main(){
    float val = texture(ImageInput, uvInterp).r;
    if(val > 0.5){
        FragColor = vec4(uvInterp, 0.0, 1.0);
    }
    else{
        FragColor = vec4(0.0, 0.0, 1, 1.0);
    }
}