void main(){
    float result = texture(ImageInput, gl_GlobalInvocationID.xy).r;
    for(int i = -1; i <= 1; i++){
        for(int j = -1; j <= 1; j++){
            vec2 samplePoint = gl_GlobalInvocationID.xy + vec2(i, j) * sampleStep;
            float tarPDist = texture(ImageInput, samplePoint/size).r * size - distance(samplePoint, gl_GlobalInvocationID.xy);
            if(tarPDist > result){
                result = tarPDist;
            }
        }
    }
    result = result / size;
    imageStore(ImageOutput, ivec2(gl_GlobalInvocationID.xy), vec4(result, result, result, 1.0));
}