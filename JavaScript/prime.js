var num=13;
var isprime=true;

for(var i=2; i<num; i++){
    if(num%i==0){
        isprime=false;
        break;
    }
}

if(isprime){
    console.log("This number is prime number");
}
else{
    console.log("This is not a prime number");
}