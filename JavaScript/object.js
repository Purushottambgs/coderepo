// // object is a collection of key-value pair

// // object literal.

// let person={
//     name:"purushottam",
//     age:23
// }
// console.log(person);

// // using new object
// let person1=new Object("puru",52);
// person1.name="name";
// person1.age=23;

// constructor function

// function student(name, age){
//     this.name=name;
//     this.age=age;
// }

// let std=new student("puru",22);
// console.log(std);

// ES6 class

class student{
    constructor(name, age){
        this.name=name;
        this.age=age;

    }
}
let s1=new student("purushottam",30);
console.log(student.name);