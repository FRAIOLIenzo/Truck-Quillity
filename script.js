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
const menuStatistiques = document.getElementById("menuStatistiques");
const menuAlgorithmes = document.getElementById("menuAlgorithmes");

function closeMenu() {
    if (menuGestion && menuClose && menuStatistiques && menuAlgorithmes) {
        if (menuGestion.style.display !== "none") lastClosedMenu = "menuGestion";
        if (menuStatistiques.style.display !== "none") lastClosedMenu = "menuStatistiques";
        if (menuAlgorithmes.style.display !== "none") lastClosedMenu = "menuAlgorithmes";

        menuGestion.style.display = "none";
        menuStatistiques.style.display = "none";
        menuAlgorithmes.style.display = "none";
        menuClose.style.display = "flex";
        console.log(lastClosedMenu);
    } else {
        console.log("No menuGestion, menuStatistiques, menuAlgorithmes, or menuClose found");
    }
}
function openLastClosedMenu() {
    if (lastClosedMenu === "menuGestion") {
        openMenuGestion();
    } else if (lastClosedMenu === "menuStatistiques") {
        openMenuStatistiques();
    } else if (lastClosedMenu === "menuAlgorithmes") {
        openMenuAlgorithmes();
    } else {
        console.log("No lastClosedMenu found");
    }
}

function openMenuGestion() {
    if (menuGestion) {
        menuGestion.style.display = "block";
        menuClose.style.display = "none";
        menuStatistiques.style.display = "none";
        menuAlgorithmes.style.display = "none";
    } else {
        console.log("No menuGestion or menuClose found");
    }
}

function openMenuStatistiques() {
    if (menuStatistiques) {
        menuGestion.style.display = "none";
        menuClose.style.display = "none";
        menuStatistiques.style.display = "block";
        menuAlgorithmes.style.display = "none";
    } else {
        console.log("No menuStatistiques found");
    }
}

function openMenuAlgorithmes() {
    if (menuAlgorithmes) {
        menuGestion.style.display = "none";
        menuClose.style.display = "none";
        menuStatistiques.style.display = "none";
        menuAlgorithmes.style.display = "block";
    } else {
        console.log("No menuAlgorithmes found");
    }
}

function openPopupAjouterVille() {
    document.getElementById("popupAjouterVille").style.display = "block";
    document.getElementById("overlay").style.display = "block";
}

function closePopupAjouterVille() {
    document.getElementById("popupAjouterVille").style.display = "none";
    document.getElementById("overlay").style.display = "none";
}
