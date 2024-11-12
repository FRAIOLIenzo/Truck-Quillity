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

  const geoNamesUsername = "enzouz";

  async function getCitySuggestions(query) {
    const response = await fetch(
      `http://api.geonames.org/searchJSON?name_startsWith=${query}&maxRows=5&cities=cities1000&username=${geoNamesUsername}`
    );
    console.log(response);
    if (response.ok) {
      const data = await response.json();
      return data.geonames.map((city) => city.name);
    } else {
      console.error("Erreur lors de la récupération des données GeoNames");
      return [];
    }
  }

  function displaySuggestions(suggestions) {
    suggestionList.innerHTML = "";
    suggestions.forEach((city) => {
      const listItem = document.createElement("div");
      listItem.classList.add("suggestion-item");
      listItem.textContent = city;

      listItem.addEventListener("click", () => {
        inputField.value = city;
        suggestionList.innerHTML = "";
      });

      suggestionList.appendChild(listItem);
    });
  }

  // inputField.addEventListener("input", async function () {
  //   const query = inputField.value.trim();
  //   if (query.length > 3) {
  //     const suggestions = await getCitySuggestions(query);
  //     displaySuggestions(suggestions);
  //   } else {
  //     suggestionList.innerHTML = "";
  //   }
  // });
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

inputField.addEventListener("keydown", handleKeyDown);

function lancerItineraire() {
  fetch("http://127.0.0.1:5000/api/test", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: cityListJson,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.message) {
        document.querySelector(".map iframe").src = "map.html";
        console.log(data);
        console.log(data.message);
        console.log(data.distance_multi_start);
        console.log(data.path_multi_start);
        
      } else {
        console.error("Erreur lors de l'envoi des données");
      }
    })

    .catch((error) => {
      console.error("Erreur de réseau:", error);
    });
  console.log(cityListJson);
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
