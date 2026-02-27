// Given an array of products where each product has a name and a price, write a function that uses the filter method to return an array containing only the products with a price less than or equal to 500.

const products=[{name:"Laptop", price:1200},
    {name:"Phone", price:300},
    {name:"Tablet", price:300},
    {name:"Smartwatch", price:150},
];

let result= products.filter((curEle)=>{
    return (curEle.price)<=500;
});

console.log(result);