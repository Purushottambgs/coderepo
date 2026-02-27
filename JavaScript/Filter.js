// const numbers=[10,5,1,2,3,5,6,7,11,15];

// const result=numbers.filter((curElem)=>{
//     return curElem<4;
// })

// console.log(result);

// le'ts say user wants to delete value 6

let value=6;
const number=[1,2,3,4,5,6,7,8,6,9,10,20,45];

let updateCart= number.filter((curElem)=>{
    return curElem!==value;
})

console.log(updateCart);
