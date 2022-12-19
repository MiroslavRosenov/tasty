function populateRecentPostedDishes(data) {
    let postSection = document.getElementById("home-posts");
    
    while (postSection.firstChild) {
        postSection.removeChild(postSection.firstChild);
    }

    for (let i = 0; i < data.length; i++){
        let dish = data[i];
        
        // Card div
        let postCard = document.createElement("div");
        postCard.id = dish["id"];
        postCard.className = "rounded overflow-hidden shadow-lg cursor-pointer transition duration-500 ease-in-out transform hover:-translate-y-1 hover:scale-105 ...";
        postCard.onclick = () => {
            window.location.href = `/dishes/${dish["id"]}`
        }

        // Image
        let dishImage = document.createElement("img");
        dishImage.className = "w-full h-64 object-cover";
        dishImage.src = dish["imageUrl"];
        dishImage.alt = dish["name"];

        // Text div
        let textDiv = document.createElement("div");
        textDiv.className = "px-6 py-4";
        let titleText = document.createElement("div");
        titleText.className = "font-medium text-xl mb-2 overflow-ellipsis overflow-hidden whitespace-nowrap";
        titleText.textContent = dish["name"];
        textDiv.appendChild(titleText);

        // Tag div
        let tagDiv = document.createElement("div");
        tagDiv.className = "px-6 pb-2";
        let tagSpan = document.createElement("span");
        tagSpan.className = "inline-block bg-gray-200 rounded-full px-3 py-1 text-sm font-semibold text-gray-700 mr-2 mb-2";
        tagSpan.textContent = `${dish["readyInMinutes"]} минути`;
        tagDiv.appendChild(tagSpan);

        postCard.appendChild(dishImage);
        postCard.appendChild(textDiv);
        postCard.appendChild(tagDiv);

        postSection.appendChild(postCard);
    }
}

function fetchDishes(){
    $.ajax({
        type: "GET",
        url: "/api/recentRecipes",
        success: function(res) {
            populateRecentPostedDishes(res["results"]);
        },
        error: function(error){
            console.log(JSON.stringify(error));
        }
    })
}

function onSearchChange(element){    
    if (element.target.value === undefined){
        fetchDishes();
        return;
    }
    $.ajax({
        type: "POST",
        url: "/api/searchRecipe",
        data: JSON.stringify({"ingredients": element.target.value}),
        success: function(data) {
            if (data["results"] === undefined) {
                document.getElementById("home-no-posts").style.display = "block";
                populateRecentPostedDishes([]);
            }
            else {
                document.getElementById("home-no-posts").style.display = "none";
                populateRecentPostedDishes(data["results"]);
            }
        },
        error: function(error){
            console.log(JSON.stringify(error));
        }
    })
}

// let searchBar = document.getElementById("home-dish-search-bar");
// let searchButton = document.getElementById("home-dish-search-button");
// searchButton.addEventListener("click", onSearchChange);

var input = document.querySelector("input[name=tags]");
// initialize Tagify on the above input node reference
tags = new Tagify(input, {originalInputValueFormat: valuesArr => valuesArr.map(item => item.value).join(", ")});
input.addEventListener('change', onSearchChange)

fetchDishes();