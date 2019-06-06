float bme_rm(float data){
    bme_rm_mean = (bme_rm_mean * bme_rm_length + data)/(bme_rm_length + 1);
    return bme_rm_mean;
}

float velocity_rm(float data){
    
    velocity_rm_mean = (velocity_rm_mean * velocity_rm_length + data)/(velocity_rm_length + 1);

    return velocity_rm_mean;
}
