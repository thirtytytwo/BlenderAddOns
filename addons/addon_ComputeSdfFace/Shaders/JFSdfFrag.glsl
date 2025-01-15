void main(){
    float bestDist = 10000.0;
    vec2 bestUV = vec2(-1,-1);
    for(int i = -1; i <= 1; i++){
        for(int j = -1; j <= 1; j++){
            vec2 uvOff = uvInterp + vec2(i, j) * sampleStep;
            vec2 val = texture(ImageInput, uvOff).rg;
            float dist = length(val - uvInterp);
            if(dist < bestDist && val.r > 0 && val.g > 0){
                bestDist = dist;
                bestUV = val;
            }
        }
    }
    FragColor = vec4(bestUV, 0.0, 1.0);
}