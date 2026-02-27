// write a program to multiply each element with 2.

let arr=[1,2,3,4,5,6,7,8,9];

for(let i of arr){
    let mul= i*2;
    console.log(mul);
}

arr.forEach((element)=>{
    console.log(element*2);
}); 