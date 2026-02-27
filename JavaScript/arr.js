// let fruits= new Array("apple", "banana","mango","orange");
// console.log(typeof arr);
// console.log(fruits);

// let name=["ram","syam","puru","rahul"];
// console.log(typeof name);
// console.log(name);
// console.log(name[0]);
// console.log(name[3]);
// name[2]="Purushottam";
// console.log(name);

let fruits=["mango","papaya","banana","orange"];
// for of---
// for(let item of fruits){
//     console.log("all fruits name "+fruits);
// }

//**for in --
// for(let item in fruits){
//     console.log(item);
// }

//arr.forEach()  --

fruits.forEach((curElem, index, arr)=>{
    console.log('${curElem} ${index}');
    console.log(arr);
})


