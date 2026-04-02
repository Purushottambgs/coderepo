let h1=document.querySelector("h1");

h1.addEventListener("click", function(){
h1.style.color="green";
});

let p=document.querySelector("p");

function pp(){
    p.style.color="red";
};

p.addEventListener("dblclick", pp);
p.removeEventListener("dblclick", pp);

let inn =document.querySelector("input");

inn.addEventListener("input", function(dets){
    if(dets.data != null){
        console.log(dets.data);
    }
});