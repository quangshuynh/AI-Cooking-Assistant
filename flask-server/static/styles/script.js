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
    };

    ingredients.forEach(item => {
        const ingredientText = item.textContent.toLowerCase();
        const category = item.parentElement.id;
        const allergens = item.getAttribute('data-allergens') || '';

        const isMeat = ['chicken', 'beef', 'turkey', 'shrimp', 'salmon', 'pork', 'crab', 'lamb', 'bacon', 'ham'].includes(ingredientText);
        const isAnimalProduct = isMeat || ['eggs', 'milk', 'cheese', 'yogurt', 'butter', 'cream'].includes(ingredientText);
        
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
        }
    });
});

function unselectAllIngredients() {
    ingredients.forEach(item => {
        item.classList.remove('selected');
    });
}

function generateRecipe() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);
    const recipeDisplay = document.getElementById('recipe-display');

    if (selectedIngredients.length > 0) {
        recipeDisplay.innerHTML = `
            <h3>Generated Recipe</h3>
            <p>Ingredients: ${selectedIngredients.join(', ')}</p>
            <p>Instructions: Combine the selected ingredients with your favorite spices and cook until perfect!</p>
        `;
    } else {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to generate a recipe.</p>`;
    }
}
