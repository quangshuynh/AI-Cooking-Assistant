// toggle the display of each ingredient list
function toggleCategory(categoryId, show = null) {
    const categoryList = document.getElementById(categoryId);
    if (show === true) {
        categoryList.style.display = 'flex';
    } else if (show === false) {
        categoryList.style.display = 'none';
    } else {
        categoryList.style.display = categoryList.style.display === 'flex' ? 'none' : 'flex';
    }
}

// filter ingredients based on search input and allergies
function filterIngredients() {
    const searchValue = document.getElementById('ingredient-search').value.toLowerCase();
    const ingredients = document.querySelectorAll('.ingredient-item');

    // Get selected allergies and preferences
    const selectedAllergies = Array.from(document.querySelectorAll('.allergy-checkbox:checked')).map(checkbox => checkbox.value);
    const isVegetarian = document.getElementById('vegetarian-filter')?.checked;
    const isVegan = document.getElementById('vegan-filter')?.checked;

    const categories = {
        "protein-list": false,
        "dairy-list": false,
        "fruits-list": false,
        "veggies-list": false,
        "grains-list": false,
        "misc-list": false
    };

    ingredients.forEach(item => {
        const ingredientText = item.textContent.toLowerCase();
        const category = item.parentElement.id;
        const allergens = item.getAttribute('data-allergens') || '';

        const isMeat = [
            'chicken', 'beef', 'turkey', 'shrimp', 'salmon', 'pork', 
            'crab', 'lamb', 'bacon', 'ham', 'duck', 'venison', 'bison'
        ].includes(ingredientText);
        
        const isAnimalProduct = isMeat || [
            'eggs', 'milk', 'cheese', 'yogurt', 'butter', 'cream', 
            'sour cream', 'ice cream', 'whipped cream', 'cottage cheese', 
            'ghee', 'ricotta', 'feta cheese', 'goat cheese', 'kefir'
        ].includes(ingredientText);
        
        
        let matchesSearch = ingredientText.includes(searchValue);

        if (isVegan && isAnimalProduct) matchesSearch = false;
        else if (isVegetarian && isMeat) matchesSearch = false;

        const isAllergen = selectedAllergies.some(allergy => allergens.includes(allergy));

        if (isAllergen || !matchesSearch) {
            item.classList.add('disabled');
            item.classList.remove('selected');
        } else {
            item.classList.remove('disabled');
            item.style.display = 'block';
            categories[category] = true;
        }
    });

    Object.keys(categories).forEach(categoryId => {
        toggleCategory(categoryId, categories[categoryId]);
    });
}

const ingredients = document.querySelectorAll('.ingredient-item');
ingredients.forEach(item => {
    item.addEventListener('click', () => {
        if (!item.classList.contains('disabled')) {
            item.classList.toggle('selected');
            updateSelectedIngredientsDisplay();
        }
    });
});

function unselectAllIngredients() {
    ingredients.forEach(item => {
        item.classList.remove('selected');
    });
}

async function generateRecipe() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);

    const selectedCuisine = document.getElementById('cuisine').value;
    const customCuisine = document.getElementById('custom-cuisine').value;

    const cuisine = selectedCuisine === 'other' ? customCuisine : selectedCuisine;

    const recipeDisplay = document.getElementById('recipe-display');
    const spinner = document.getElementById('loading-spinner');

    if (selectedIngredients.length > 0) {
        recipeDisplay.innerHTML = ''; 
        spinner.style.display = 'flex'; 

        try {
            const response = await fetch("/generate_recipe", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ ingredients: selectedIngredients, cuisine: cuisine })  // Added cuisine here
            });

            const result = await response.json();
            spinner.style.display = 'none';
            recipeDisplay.innerHTML = `<h3>Generated Recipe</h3>${result.recipe_html}`;
        } catch (error) {
            spinner.style.display = 'none';
            recipeDisplay.innerHTML = `<p>Error generating recipe: ${error.message}</p>`;
        }
    } else {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to generate a recipe.</p>`;
    }
}




function toggleRecipeDetails(recipeId) {
    const recipeContent = document.getElementById(recipeId);
    if (recipeContent.style.display === "none" || recipeContent.style.display === "") {
        recipeContent.style.display = "block";
    } else {
        recipeContent.style.display = "none";
    }
}


function updateSelectedIngredientsDisplay() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);
    const selectedIngredientsDisplay = document.getElementById('selected-ingredients-display');

    if (selectedIngredients.length > 0) {
        selectedIngredientsDisplay.innerHTML = `<p>${selectedIngredients.join(', ')}</p>`;
    } else {
        selectedIngredientsDisplay.innerHTML = `<p>No ingredients selected.</p>`;
    }
}

function toggleCustomCuisineInput() {
    const cuisineSelect = document.getElementById('cuisine');
    const customCuisineInput = document.getElementById('custom-cuisine');
    if (cuisineSelect.value === 'other') {
        customCuisineInput.style.display = 'block';
        customCuisineInput.style.opacity = '1';
    } else {
        customCuisineInput.style.display = 'none';
        customCuisineInput.style.opacity = '0';
    }
}


function updateProgressBar(progress) {
    const progressBar = document.getElementById("progress-bar");
    progressBar.style.width = progress + "%";
}

async function fetchProgress() {
    const eventSource = new EventSource("/progress");
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateProgressBar(data.progress);

        // Stop listening when progress reaches 100%
        if (data.progress >= 100) {
            eventSource.close();
        }
    };
}

// Call this function when the recipe generation starts
function startRecipeGeneration() {
    // Start fetching progress
    fetchProgress();

    // Other recipe generation logic...
    generateRecipe();
}
