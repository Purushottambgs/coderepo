let form= document.querySelector("form");
let inputs= document.querySelector("input");
let main= document.querySelector("#main");

form.addEventListener("submit", function(dets){
    dets.preventDefault();

    let card= document.createElement("div");
    card.classList.add("card");

    let profile= document.createElement("div");
    profile.classList.add("profile");

    let img= document.createElement("img");
    img.setAttribute("src", "https://www.pexels.com/search/desktop%20wallpaper/");

    let h3= document.createElement("h3");
    h3.textContent="Bgs.com_";
    let h5= document.createElement("h5");
    h5.textContent="good engineer";
    let p= document.createElement("p");
    p.textContent="i am intelligent student in it department";


    profile.appendChild(img);
    card.appendChild(profile);

    card.appendChild(h3);
    card.appendChild(h5);
    card.appendChild(p);

    main.appendChild(card);
});