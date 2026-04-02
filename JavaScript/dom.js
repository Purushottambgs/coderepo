// Selecting Elements

let input= document.getElementById("taskInput");
let addBtn=document.getElementById("addBtn");
let tasklist=document.getElementById("taskList");
let colorBtn=document.getElementById("colorBtn");



let h2=document.querySelector("h2");

h2.addEventListener("click", function(){
    h2.style.color="red";
});
// Add task event
alert("Hello");
addBtn.addEventListener("click", function(){
    // Create new li
let li=document.createElement("li");

// Add text to li
li.textContent= input.value;

// Create Delete button
let delBtn=document.createElement("button");
delBtn.textContent="Delete";

// Delete event
delBtn.addEventListener("click",function() {
    li.remove();
});
// Append delete button to li
li.appendChild(delBtn);

// append li to list
tasklist.appendChild(li);

// clear input
input.value="";
});

// Change Background
colorBtn.addEventListener("click", function(){
    document.body.style.backgroundColor="lightblue";
});