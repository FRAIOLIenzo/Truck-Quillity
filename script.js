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
    const suggestionContainer = document.querySelector(
      ".popupAjouterVilleFormSuggestion"
    );
    if (query.length >= 3) {
      fetch(
        `https://api-adresse.data.gouv.fr/search/?q=${query}&type=municipality&autocomplete=1`
      )
        .then((response) => response.json())
        .then((data) => {
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
        .catch((error) => console.error("Erreur de réseau:", error));
    } else {
      suggestionContainer.innerHTML = "";
      suggestionContainer.style.display = "none";
    }
  });

  inputField.addEventListener("paste", (event) => {
    event.preventDefault();
    const pasteData = event.clipboardData.getData("text");
    const cities = pasteData.split(",").map((city) => city.trim());
    cities.forEach((city) => {
      const paragraph = document.createElement("p");
      paragraph.textContent = city + ",\u00A0";
      paragraph.style.marginTop = "5px";
      paragraph.style.marginBottom = "5px";
      document
        .getElementById("popupAjouterVilleFormList")
        .appendChild(paragraph);
      cityList.push(city);
    });
    inputField.value = "";
  });

  inputField.addEventListener("keydown", (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      const firstSuggestion = document.querySelector(".first-suggestion");
      if (firstSuggestion) {
        inputField.value = firstSuggestion.textContent;
        const suggestionContainer = document.querySelector(
          ".popupAjouterVilleFormSuggestion"
        );
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
  }
}

function openPopupAjouterVille() {
  console.log("Opening popup");
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
  cityListJson = "";
  document.getElementById("menuGestionAjouterListeVilleText").textContent = "";
  resetMap();
  document.getElementById("menuGestionAjouter").classList.remove("active");
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
  document.getElementById("menuGestionTemps").style.display = "none";
  document.getElementById("menuGestionDistance").style.display = "none";
  document.getElementById("menuGestionNbCamion").style.display = "none";
}

let cityListJson = "";

function validerPopupAjouterVille() {
  document.getElementById("popupAjouterVille").style.display = "none";
  document.getElementById("overlay").style.display = "none";
  cityListJson = JSON.stringify(cityList.map((city) => ({ city_name: city })));
  if (cityList.length > 0) {
    document.getElementById("menuGestionAjouter").classList.add("active");
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
    let cityListText = cityList
      .slice(0, 10)
      .map((city) => city + ",\u00A0")
      .join("");
    if (cityList.length > 14) {
      cityListText += "...";
    }
    document.getElementById("menuGestionAjouterListeVilleText").textContent =
      cityListText;
  }
}

function lireDonneesResultJson(type) {
  fetch("http://127.0.0.1:5000/api/stat", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data) {
        console.log(data);
        let tableBody;
        let container;
        let activeClass;

        // Close any open tables
        const containers = document.querySelectorAll(
          ".menuStatistiquesAfficherPulpTableauContainer, .menuStatistiquesAfficherFourmisTableauContainer, .menuStatistiquesAfficherTabouTableauContainer, .menuStatistiquesAfficherGenetiqueTableauContainer"
        );
        containers.forEach((cont) => (cont.style.display = "none"));
        const activeElements = document.querySelectorAll(
          ".menuStatistiquesAfficherPulp.active, .menuStatistiquesAfficherFourmis.active, .menuStatistiquesAfficherTabou.active, .menuStatistiquesAfficherGenetique.active"
        );
        activeElements.forEach((el) => el.classList.remove("active"));

        switch (type) {
          case "Pulp":
            container = document.getElementById(
              "menuStatistiquesAfficherPulpTableauContainer"
            );
            tableBody = document.getElementById(
              "menuStatistiquesAfficherPulpTableauBody"
            );
            activeClass = "menuStatistiquesAfficherPulp";
            break;
          case "ANT":
            container = document.getElementById(
              "menuStatistiquesAfficherFourmisTableauContainer"
            );
            tableBody = document.getElementById(
              "menuStatistiquesAfficherFourmisTableauBody"
            );
            activeClass = "menuStatistiquesAfficherFourmis";
            break;
          case "Tabu":
            container = document.getElementById(
              "menuStatistiquesAfficherTabouTableauContainer"
            );
            tableBody = document.getElementById(
              "menuStatistiquesAfficherTabouTableauBody"
            );
            activeClass = "menuStatistiquesAfficherTabou";
            break;
          case "Genetique":
            container = document.getElementById(
              "menuStatistiquesAfficherGenetiqueTableauContainer"
            );
            tableBody = document.getElementById(
              "menuStatistiquesAfficherGenetiqueTableauBody"
            );
            activeClass = "menuStatistiquesAfficherGenetique";
            break;
          default:
            console.error("Type non reconnu");
            return;
        }

        container.style.display = "block";
        document.getElementById(activeClass).classList.add("active");
        tableBody.innerHTML = ""; // Clear existing rows
        Object.keys(data).forEach((key) => {
          const row = document.createElement("tr");

          const cellJeu = document.createElement("td");
          cellJeu.textContent = key;
          row.appendChild(cellJeu);

          const cellDistance = document.createElement("td");
          cellDistance.textContent =
            data[key][type].Distance.toFixed(2) + " km";
          row.appendChild(cellDistance);

          const cellNombreCamion = document.createElement("td");
          cellNombreCamion.textContent = data[key][type].NombreCamion;
          row.appendChild(cellNombreCamion);

          const cellTemps = document.createElement("td");
          cellTemps.textContent = data[key][type].Temps.toFixed(2) + " s";
          row.appendChild(cellTemps);

          tableBody.appendChild(row);
        });
      } else {
        console.error("Erreur lors de l'envoi des données");
      }
    })
    .catch((error) => {
      console.error("Erreur de réseau:", error);
    });
}

function popupAjouterRandomVille() {
  document.getElementById("loaderContainerPopup").style.display = "block";
  document.getElementById("popupAjouterVilleFormList").style.display = "none";
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
          document
            .getElementById("popupAjouterVilleFormList")
            .appendChild(paragraph);
          cityList.push(city.Cityname);
        });
        console.log(cityList.join(", "));
      } else {
        console.error("Erreur lors de l'envoi des données");
      }
      document.getElementById("loaderContainerPopup").style.display = "none";
      document.getElementById("popupAjouterVilleFormList").style.display =
        "flex";
    })

    .catch((error) => {
      document.getElementById("loaderContainerPopup").style.display = "none";
      console.error("Erreur de réseau:", error);
    });
}

inputField.addEventListener("keydown", handleKeyDown);

function lancerItineraire() {
  const selectedAlgo = document
    .getElementById("menuGestionChoixAlgo")
    .value.toLowerCase();
    
  const algoSettings = sauvegarderAlgo();
  console.log("selectedAlgo", selectedAlgo);   
  console.log("TESTESTEST",JSON.stringify({ cityList, algoSettings }));
  if (
    document.querySelector(".menuGestionBoutonLancer").textContent !==
      "Refine routes" 
  ) {
    console.log("cityudufushvsbhbfjbjsf");
    document.getElementById("loaderContainer").style.display = "flex";

    console.log("city", cityList);
    fetch(`http://127.0.0.1:5000/api/${selectedAlgo}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ cityList, algoSettings }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          console.log("data", data);
          document.querySelector(".map iframe").src = "map.html";
          document.getElementById("loaderContainer").style.display = "none";
          document.getElementById("menuGestionTempsValue").textContent =
            data.temps_execution.toFixed(2) + "s";
          document.getElementById("menuGestionDistanceValue").textContent =
            data.distance.toFixed(2) + "km";
          document.getElementById("menuGestionNbCamionValue").textContent =
            data.nb_camions;
          document.getElementById("menuGestionTemps").style.display = "flex";
          document.getElementById("menuGestionDistance").style.display = "flex";
          document.getElementById("menuGestionNbCamion").style.display = "flex";
          if (selectedAlgo === "fourmis") {
            document.querySelector(".menuGestionBoutonLancer").textContent =
            "Refine routes";
          }
        } else {
          console.error("Erreur lors de l'envoi des données");
          document.getElementById("loaderContainer").style.display = "none";
        }
      })

      .catch((error) => {
        console.error("Erreur de réseau:", error);
        document.getElementById("loaderContainer").style.display = "none";
      });
  } else {
    console.log("oui oui oui");
    document.getElementById("loaderContainer").style.display = "flex";
    document.querySelector(".map iframe").src = "map_test.html";
    document.getElementById("loaderContainer").style.display = "none";
    document.querySelector(".menuGestionBoutonLancer").textContent =
    "Start route";
  }
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

function afficherInfo() {
  document.getElementById("popupAfficherVille").style.display = "block";
  document.getElementById("overlay").style.display = "block";
  fetch("http://127.0.0.1:5000/api/statville", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      const popupAfficherVilleList = document.getElementById(
        "popupAfficherVilleList"
      );
      popupAfficherVilleList.innerHTML = ""; // Clear existing content

      Object.keys(data).forEach((key) => {
        const paragraph = document.createElement("p");
        paragraph.textContent = `${key}: ${data[key].join(", ")}`;
        popupAfficherVilleList.appendChild(paragraph);
      });
      console.log(data);
    });
}

function closePopupAfficherCity() {
  document.getElementById("popupAfficherVille").style.display = "none";
  document.getElementById("overlay").style.display = "none";
}


function sauvegarderAlgo() {
  const nbFourmis = document.getElementById("menuAlgoNbFourmis").value;
  const nbIterations = document.getElementById("menuAlgoNbIterations").value;
  const capacity = document.getElementById("menuAlgoCapacity").value;
  const nbStarts = document.getElementById("menuAlgoNbStarts").value;
  const capacityTabou = document.getElementById("menuAlgoCapacityTabou").value;
  const capacityGenetic = document.getElementById("menuAlgoCapacityGenetic").value;
  const nbGenerations = document.getElementById("menuAlgoGenerationGenetic").value;
  const populationSize = document.getElementById("menuAlgoPopulationGenetic").value;
  const algoSettings = {
    nbFourmis: parseInt(nbFourmis, 10),
    nbIterations: parseInt(nbIterations, 10),
    capacity: parseInt(capacity, 10),
    nbStarts: parseInt(nbStarts, 10),
    capacityTabou: parseInt(capacityTabou, 10),
    capacityGenetic: parseInt(capacityGenetic, 10),
    nbGenerations: parseInt(nbGenerations, 10),
    populationSize: parseInt(populationSize, 10),
  };
  console.log("Algorithm settings saved:", algoSettings);
  return algoSettings;
}