char input= 0;
int x;
void setup() {
 Serial.begin(9600);  
 Serial.println(); 
 //Serial.println("Relay shield sample code");
 //Serial.println("Press 1-4 to control the state of the relay");
 //Serial.println("This sample will cycle each of the relays once, then wait for your input");
 

  pinMode(2, OUTPUT); //address for Relay 1 (Digital pin 2)
  //delay(250);
  pinMode(3, OUTPUT); //address for Relay 2 (Digital pin 3)
  //delay(250);
  pinMode(4, OUTPUT); //address for Relay 3 (Digital pin 4)
  //delay(250);
  pinMode(5, OUTPUT); //address for Relay 4 (Digital pin 5)
  //delay(250);
  PORTD=B00000000; //Set all relays to off position.
  //delay(250); 
  
 //Serial.println("waiting for input:");
}

void loop() {
 
  if (Serial.available() > 0) {
    input= Serial.read();
    //Serial.print("toggle: ");
    
    
    if(input =='1'){
      Serial.println("Relay 1");
      x=(bitRead(PORTD,2));
      x=!x; 
      bitWrite(PORTD,2,x);
      
    }else if (input =='2'){
       Serial.println("Relay 2");
       x=(bitRead(PORTD,3));
       x=!x; 
       bitWrite(PORTD,3,x);
      
    }else if (input =='3'){
       Serial.println("Relay 3");
       x=(bitRead(PORTD,4));
       x=!x; 
       bitWrite(PORTD,4,x);
      
    }else if (input =='4'){
       Serial.println("Relay 4");
       x=(bitRead(PORTD,5));
       x=!x; 
       bitWrite(PORTD,5,x);
      
    } 
}
}
