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

// filter ingredients based on search input and show matching categories
function filterIngredients() {
    const searchValue = document.getElementById('ingredient-search').value.toLowerCase();
    const ingredients = document.querySelectorAll('.ingredient-item');

    const categories = {
        "protein-list": false,
        "dairy-list": false,
        "fruits-list": false,
        "veggies-list": false
    };

    ingredients.forEach(item => {
        const ingredientText = item.textContent.toLowerCase();
        const category = item.parentElement.id;

        if (ingredientText.includes(searchValue)) {
            item.style.display = 'block';
            categories[category] = true; // mark category to be shown if there's a match
        } else {
            item.style.display = 'none';
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
        item.classList.toggle('selected');
    });
});

// generate a placeholder recipe based on selected ingredients
function generateRecipe() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);

    const recipeDisplay = document.getElementById('recipe-display');
    if (selectedIngredients.length > 0) {
        recipeDisplay.innerHTML = `
            <h3>Generated Recipe</h3>
            <p>Ingredients: ${selectedIngredients.join(', ')}</p>
            <p>Instructions: Combine the selected ingredients with your favorite spices and cook until perfect! Enjoy your unique dish!</p>
        `;
    } else {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to generate a recipe.</p>`;
    }
}
