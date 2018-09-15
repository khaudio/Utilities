int color[] = {0, 0, 0};
int rgbPins[] = {9, 10, 11};
const bool reversePolarity = true;
const int delayTime = 10;
static int index[2];


int polarityOffset(int value) {
    return (reversePolarity ? (255 - value) : value);
}


void applyColors() {
    for (int i = 0; i < 3; i++) {
        analogWrite(rgbPins[i], polarityOffset(color[i]));
    }
}


void indexRange(int *index) {
    if (*index > 2) {
        *index = 0;
    }
}


void rotate() {
    for (int i = 0; i < 2; i++) {
        index[i]++;
        indexRange(&index[i]);
    }
}


void cycleUp(int *index) {
    for (int i = 0; i <= 255; i++) {
        color[*index] = i;
        applyColors();
        delay(delayTime);
    }
}


void cycleDown(int *index) {
    for (int i = 255; i >= 0; i--) {
        color[*index] = i;
        applyColors();
        delay(delayTime);
    }
}


void cycleSpectrum() {
    cycleUp(&index[1]);
    delay(delayTime);
    cycleDown(&index[0]);
    delay(delayTime);
    rotate();
}


void setup() {
    for (int pin = rgbPins[0]; pin <= rgbPins[-1]; pin++) {
        pinMode(pin, OUTPUT);
    }
    index[0] = 0;
    index[1] = 1;
}


void loop() {
    cycleSpectrum();
}
