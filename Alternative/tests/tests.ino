unsigned int a = 0;
void setup() {
  Serial.begin(9600);
}

void loop() {
  a = millis();
  Serial.println(a);



}
