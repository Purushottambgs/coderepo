// add dec at the end of an array?
// what is the return value of splice method?
// update march to March(update)?
// Delete june from an array?

const months=["january","february","march","april","june","july","august"];
// console.log(months);
// months.push("December");
// console.log(months);

months.splice(1,0);
console.log(months);
months.splice(1,2,"March");
console.log(months);

console.log(months.pop("june"));
console.log(months);
