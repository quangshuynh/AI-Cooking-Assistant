async function searchIngredients() {
    const query = document.getElementById('ingredient-search').value;
    const resultsList = document.getElementById('search-results');
    const spinner = document.getElementById('loading-spinner');

    // Show loading spinner
    spinner.classList.remove('hidden');
    resultsList.innerHTML = '';  // Clear previous results

    try {
        const response = await fetch(`/api/ingredients?query=${query}`);
        const ingredients = await response.json();

        ingredients.forEach(ingredient => {
            const li = document.createElement('li');
            li.textContent = ingredient.description;
            li.onclick = () => selectIngredient(ingredient.description);
            resultsList.appendChild(li);
        });
    } finally {
        // Hide loading spinner
        spinner.classList.add('hidden');
    }
}

function selectIngredient(ingredient) {
    const selectedList = document.getElementById('selected-ingredients');
    const existingIngredient = Array.from(selectedList.children).find(
        child => child.textContent === ingredient
    );

    if (existingIngredient) {
        existingIngredient.remove();
    } else {
        const li = document.createElement('li');
        li.textContent = ingredient;
        li.classList.add('selected');
        li.onclick = () => li.remove();
        selectedList.appendChild(li);
    }
}

async function generateRecipe() {
    const ingredients = Array.from(document.getElementById('selected-ingredients').children).map(li => li.textContent);
    const allergies = document.getElementById('allergies').value;
    const maxCost = document.getElementById('max-cost').value;
    const cuisine = document.getElementById('cuisine').value;
    const servingSize = document.getElementById('serving-size').value;
    const mealType = document.getElementById('meal-type').value;

    const response = await fetch(`/api/recipes?` +
        `ingredients=${ingredients.join(',')}&allergies=${allergies}` +
        `&max_cost=${maxCost}&cuisine=${cuisine}&serving_size=${servingSize}&meal_type=${mealType}`);
    
    const recipes = await response.json();
    const recipeDisplay = document.getElementById('recipe-display');

    if (recipes.length) {
        recipeDisplay.innerHTML = recipes.map(recipe => `
            <h3>${recipe.description}</h3>
            <p>Category: ${recipe.food_category_id}</p>
            <p>Published: ${recipe.publication_date}</p>
        `).join('');
    } else {
        recipeDisplay.innerHTML = `<p>No recipes found. Try adjusting your preferences.</p>`;
    }
}
