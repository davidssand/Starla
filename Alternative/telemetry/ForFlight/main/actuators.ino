void buzz(byte n, int sleep_time){
  for(byte i = 0; i < n; i++){
    analogWrite(A2, 1023);
    delay(sleep_time);
    analogWrite(A2, 0);
    delay(sleep_time);
  }
}

void open_parachute() {
  servo1.write(175);
  servo2.write(5);
}
