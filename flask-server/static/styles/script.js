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

    // Get selected allergies and preferences
    const selectedAllergies = Array.from(document.querySelectorAll('.allergy-checkbox:checked'))
        .map(checkbox => checkbox.value);
    const isVegetarian = document.getElementById('vegetarian-filter').checked;
    const isVegan = document.getElementById('vegan-filter').checked;

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

        // Vegetarian and vegan filtering
        const isMeat = ['chicken', 'beef', 'turkey', 'shrimp', 'salmon', 'pork', 'crab', 'lamb', 'bacon', 'ham'].includes(ingredientText);
        const isAnimalProduct = isMeat || ['eggs', 'milk', 'cheese', 'yogurt', 'butter', 'cream'].includes(ingredientText);
        
        let matchesSearch = ingredientText.includes(searchValue);

        // Apply vegetarian/vegan filters
        if (isVegan && isAnimalProduct) {
            matchesSearch = false;
        } else if (isVegetarian && isMeat) {
            matchesSearch = false;
        }

        const isAllergen = selectedAllergies.some(allergy => allergens.includes(allergy));

        // Handle allergens and visibility
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