const inputField = document.getElementById("popupAjouterVilleFormInput");
const suggestionList = document.getElementById("popupAjouterVilleFormList");
const cityList = [];

document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM Loaded");
  resetMap();

  const menuElements = document.querySelectorAll(".menuElementContainer");

  menuElements.forEach((element) => {
    element.addEventListener("click", () => {
      console.log("Clicked on:", element);
      menuElements.forEach((el) => el.classList.remove("active"));
      element.classList.add("active");
    });
  });

  inputField.addEventListener("input", () => {
    const query = inputField.value.trim();
    const suggestionContainer = document.querySelector(".popupAjouterVilleFormSuggestion");
    if (query.length >= 3) {
      fetch(`https://api-adresse.data.gouv.fr/search/?q=${query}&type=municipality&autocomplete=1`)
        .then(response => response.json())
        .then(data => {
          suggestionContainer.innerHTML = "";
          if (data.features.length === 0) {
            suggestionContainer.style.display = "none";
          } else {
            suggestionContainer.style.display = "block";
            data.features.forEach((feature, index) => {
              const suggestionItem = document.createElement("div");
              suggestionItem.classList.add("suggestion-item");
              suggestionItem.textContent = feature.properties.label;
              suggestionItem.addEventListener("click", () => {
                inputField.value = feature.properties.label;
                suggestionContainer.innerHTML = "";
                suggestionContainer.style.display = "none";
              });
              suggestionContainer.appendChild(suggestionItem);
              if (index === 0) {
                suggestionItem.classList.add("first-suggestion");
              }
            });
          }
        })
        .catch(error => console.error("Erreur de réseau:", error));
    } else {
      suggestionContainer.innerHTML = "";
      suggestionContainer.style.display = "none";
    }
  });

  inputField.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      const firstSuggestion = document.querySelector(".first-suggestion");
      if (firstSuggestion) {
        inputField.value = firstSuggestion.textContent;
        const suggestionContainer = document.querySelector(".popupAjouterVilleFormSuggestion");
        suggestionContainer.innerHTML = "";
        suggestionContainer.style.display = "none";
      }
    }
  });
});

const menuGestion = document.getElementById("menuGestion");
const menuClose = document.getElementById("menuClose");
const menuStatistiques = document.getElementById("menuStatistiques");
const menuAlgorithmes = document.getElementById("menuAlgorithmes");

function closeMenu() {
  if (menuGestion && menuClose && menuStatistiques && menuAlgorithmes) {
    if (menuGestion.style.display !== "none") lastClosedMenu = "menuGestion";
    if (menuStatistiques.style.display !== "none")
      lastClosedMenu = "menuStatistiques";
    if (menuAlgorithmes.style.display !== "none")
      lastClosedMenu = "menuAlgorithmes";

    menuGestion.style.display = "none";
    menuStatistiques.style.display = "none";
    menuAlgorithmes.style.display = "none";
    menuClose.style.display = "flex";
    console.log(lastClosedMenu);
  } else {
    console.log(
      "No menuGestion, menuStatistiques, menuAlgorithmes, or menuClose found"
    );
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

function handleKeyDown(event) {
  if (event.key === "Enter" && inputField.value.trim() !== "") {
    const city = inputField.value.trim();
    const paragraph = document.createElement("p");
    paragraph.textContent = city + ",\u00A0";
    paragraph.style.marginTop = "5px";
    paragraph.style.marginBottom = "5px";
    document.getElementById("popupAjouterVilleFormList").appendChild(paragraph);
    cityList.push(city);
    inputField.value = "";
    console.log(cityList.join(", "));
  }
}

function openPopupAjouterVille() {
  document.getElementById("popupAjouterVille").style.display = "block";
  document.getElementById("overlay").style.display = "block";
}

function closePopupAjouterVille() {
  document.getElementById("popupAjouterVille").style.display = "none";
  document.getElementById("overlay").style.display = "none";
  cityList.length = 0;
  document.getElementById("popupAjouterVilleFormList").innerHTML = "";
}

function deleteListeVille() {
  cityList.length = 0;
  document.getElementById("popupAjouterVilleFormList").innerHTML = "";
  cityListJson = ""
  document.getElementById("menuGestionAjouterListeVilleText").textContent = "";
  resetMap();
  document
    .getElementById("menuGestionAjouter").classList.remove("active");
  document
    .getElementById("menuGestionAjouterListeVille")
    .classList.remove("active");
  document
    .getElementById("menuGestionAjouterListeVilleText")
    .classList.remove("active");
  document
    .getElementById("menuGestionAjouterIconDelete")
    .classList.remove("active");
  document
    .getElementById("menuGestionAjouterIconPlus")
    .classList.remove("active");
}

let cityListJson = "";

function validerPopupAjouterVille() {
  document.getElementById("popupAjouterVille").style.display = "none";
  document.getElementById("overlay").style.display = "none";
  cityListJson = JSON.stringify(
    cityList.map((city) => ({ city_name: city }))
  );
  if (cityList.length > 0) {
    document
      .getElementById("menuGestionAjouter").classList.add("active");
    document
      .getElementById("menuGestionAjouterListeVille")
      .classList.add("active");
    document
      .getElementById("menuGestionAjouterListeVilleText")
      .classList.add("active");
    document
      .getElementById("menuGestionAjouterIconDelete")
      .classList.add("active");
    document
      .getElementById("menuGestionAjouterIconPlus")
      .classList.add("active");
    const cityListText = cityList
      .map((city) => city + ",\u00A0")
      .join("");
    document.getElementById(
      "menuGestionAjouterListeVilleText"
    ).textContent = cityListText;
  }
}


function popupAjouterRandomVille() {
  fetch("http://127.0.0.1:5000/api/random_cities", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },

  })
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        console.log(data);
        data.forEach((city) => {
          const paragraph = document.createElement("p");
          paragraph.style.marginTop = "5px";
          paragraph.style.marginBottom = "5px";
          paragraph.textContent = city.Cityname + ",\u00A0";
          document.getElementById("popupAjouterVilleFormList").appendChild(paragraph);
          cityList.push(city.Cityname);
        });
        console.log(cityList.join(", "));
      } else {
        console.error("Erreur lors de l'envoi des données");
      }
    })

    .catch((error) => {
      console.error("Erreur de réseau:", error);
    });
}

inputField.addEventListener("keydown", handleKeyDown);

function lancerItineraire() {
  document.getElementById("loaderContainer").style.display = 'flex';
  fetch("http://127.0.0.1:5000/api/fourmie", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(cityList),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message) {
        document.querySelector(".map iframe").src = "map.html";
        document.getElementById("loaderContainer").style.display = 'none';
      } else {
        console.error("Erreur lors de l'envoi des données");
        document.getElementById("loaderContainer").style.display = 'none';
      }
    })

    .catch((error) => {
      console.error("Erreur de réseau:", error);
      document.getElementById("loaderContainer").style.display = 'none';
    });
}

function resetMap() {
  const resetJson = JSON.stringify({ city_name: "reset" });
  fetch("http://127.0.0.1:5000/api/reset", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: resetJson,
  })
    .then((response) => {
      if (response.ok) {
        document.querySelector(".map iframe").src = "map.html";
      } else {
        console.error("Erreur lors de l'envoi des données");
      }
    })
    .catch((error) => {
      console.error("Erreur de réseau:", error);
    });
}
