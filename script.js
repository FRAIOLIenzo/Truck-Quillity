document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM Loaded");

  const menuElements = document.querySelectorAll(".menuElementContainer");

  menuElements.forEach((element) => {
    element.addEventListener("click", () => {
      console.log("Clicked on:", element);

      // Remove 'active' class from all elements

      menuElements.forEach((el) => el.classList.remove("active"));

      // Add 'active' class to the clicked element

      element.classList.add("active");
    });
  });
});



const menuGestion = document.getElementById("menuGestion");

const menuClose = document.getElementById("menuClose");

function closeMenuGestion() {
  if (menuGestion && menuClose) {
    menuGestion.style.display = "none";
    menuClose.style.display = "flex";
  } else {
    console.log("No menuGestion or menuClose found");
  }
}

function openMenuGestion() {
  if (menuGestion && menuClose) {
    menuGestion.style.display = "block";
    menuClose.style.display = "none";
  } else {
    console.log("No menuGestion or menuClose found");
  }
}
