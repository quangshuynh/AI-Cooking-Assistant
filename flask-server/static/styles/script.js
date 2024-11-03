// toggle the display of each ingredient list
function toggleCategory(categoryId, show = null) {
    const categoryList = document.getElementById(categoryId);
    if(show === true) {
        categoryList.style.display = 'flex';
    } else if(show === false) {
        categoryList.style.display = 'none';
    } else {
        categoryList.style.display = categoryList.style.display === 'flex' ? 'none' : 'flex';
    }
}

// filter ingredients based on search input and allergies
function filterIngredients() {
    const searchValue = document.getElementById('ingredient-search').value.toLowerCase();
    const ingredients = document.querySelectorAll('.ingredient-item');

    // get selected allergens
    const selectedAllergies = Array.from(document.querySelectorAll('.allergy-checkbox:checked'))
        .map(checkbox => checkbox.value);

    // track categories with matches
    const categories = {
        "protein-list": false,
        "dairy-list": false,
        "fruits-list": false,
        "veggies-list": false
    };

    ingredients.forEach(item => {
        const ingredientText = item.textContent.toLowerCase();
        const category = item.parentElement.id;
        const allergens = item.getAttribute('data-allergens') || '';

        // check if ingredient should be disabled due to allergies
        const isAllergen = selectedAllergies.some(allergy => allergens.includes(allergy));
        const matchesSearch = ingredientText.includes(searchValue);

        // if it's an allergen, gray it out and disable selection
        if(isAllergen) {
            item.classList.add('disabled');
            item.classList.remove('selected'); // deselect if already selected
        } else {
            item.classList.remove('disabled');
        }

        // Show ingredient if it matches the search and is not hidden by allergy
        item.style.display = matchesSearch ? 'block' : 'none';
        if(matchesSearch && !isAllergen) {
            categories[category] = true; // Show category if there's a matching ingredient
        }
    });

    // show or hide categories based on matches
    Object.keys(categories).forEach(categoryId => {
        toggleCategory(categoryId, categories[categoryId]);
    });
}

// select ingredient elements
const ingredients = document.querySelectorAll('.ingredient-item');

ingredients.forEach(item => {
    item.addEventListener('click', () => {
        // only toggle selection if item is not disabled
        if(!item.classList.contains('disabled')) {
            item.classList.toggle('selected');
        }
    });
});

// unselect all ingredients
function unselectAllIngredients() {
    ingredients.forEach(item => {
        item.classList.remove('selected');
    });
}

// toggle custom cuisine input field when "Other" is selected
function toggleCustomCuisineInput() {
    const cuisineSelect = document.getElementById('cuisine');
    const customCuisineInput = document.getElementById('custom-cuisine');

    // show the custom cuisine input field if 'Other' is selected
    if(cuisineSelect.value === 'other') {
        customCuisineInput.style.display = 'block';  // show input
        customCuisineInput.focus();  // automatically focus on the input field
    } else {
        customCuisineInput.style.display = 'none';  // hide input
        customCuisineInput.value = '';  // clear the value if hidden
    }
}

// generate a placeholder recipe based on selected ingredients and filters
function generateRecipe() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);

    const cost = document.getElementById('cost').value;
    const cuisineSelect = document.getElementById('cuisine').value;
    const customCuisine = document.getElementById('custom-cuisine').value;
    const cuisine = cuisineSelect === 'other' ? customCuisine : cuisineSelect;  // use custom cuisine if 'Other'

    const servingSize = document.getElementById('serving-size').value;
    const mealType = document.getElementById('meal-type').value;

    const recipeDisplay = document.getElementById('recipe-display');
    if (selectedIngredients.length > 0) {
        recipeDisplay.innerHTML = `
            <h3>Generated Recipe</h3>
            <p>Ingredients: ${selectedIngredients.join(', ')}</p>
            <p>Cost: ${cost ? `$${cost}` : 'N/A'}</p>
            <p>Cuisine: ${cuisine || 'N/A'}</p>
            <p>Serving Size: ${servingSize || 'N/A'}</p>
            <p>Meal Type: ${mealType || 'N/A'}</p>
            <p>Instructions: Combine the selected ingredients with your favorite spices and cook until perfect! Enjoy your unique dish!</p>
        `;
    } else {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to generate a recipe.</p>`;
    }
}
