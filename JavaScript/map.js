// const number=[1,2,3,4,5,6,8,9,2];

// const result=number.map((curElem)=> curElem *5);
// console.log(result);



// Using map to square each number and create a new array.

const numbers=[1,2,3,4,5];

let squarenum=numbers.map((curEle)=>{
    return (curEle*curEle);
});
let seq=[squarenum];
console.log(seq);

