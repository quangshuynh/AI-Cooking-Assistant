// Define categories at the top level
const categories = {
    "protein-list": false,
    "dairy-list": false,
    "fruits-list": false,
    "veggies-list": false,
    "grains-list": false,
    "misc-list": false
};

function toggleCategory(categoryId, show = null) {
    const categoryList = document.getElementById(categoryId);
    if (!categoryList) return;

    if (show === true) {
        categoryList.style.display = 'flex';
    } else if (show === false) {
        categoryList.style.display = 'none';
    } else {
        categoryList.style.display = categoryList.style.display === 'flex' ? 'none' : 'flex';
    }
}

function filterIngredients() {
    const searchValue = document.getElementById('ingredient-search').value.toLowerCase();
    const ingredients = document.querySelectorAll('.ingredient-item');

    const selectedAllergies = Array.from(document.querySelectorAll('.allergy-checkbox:checked')).map(checkbox => checkbox.value);
    const isVegetarian = document.getElementById('vegetarian-filter')?.checked;
    const isVegan = document.getElementById('vegan-filter')?.checked;

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

    updateCategoryVisibility();
}

// Set up search suggestions
let searchTimeout;
const searchSuggestionsContainer = document.createElement('div');
searchSuggestionsContainer.className = 'search-suggestions';
const searchBox = document.getElementById('ingredient-search');
searchBox.parentNode.style.position = 'relative';
searchBox.parentNode.appendChild(searchSuggestionsContainer);

function updateCategoryVisibility() {
    Object.keys(categories).forEach(categoryId => {
        const categoryList = document.getElementById(categoryId);
        if (categoryList) {
            const hasSelectedOrVisible = Array.from(categoryList.querySelectorAll('.ingredient-item'))
                .some(item => !item.classList.contains('disabled') || item.classList.contains('selected'));
            toggleCategory(categoryId, hasSelectedOrVisible);
        }
    });
}

async function handleIngredientSearch(event) {
    const searchValue = event.target.value;

    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    if (!searchValue.trim()) {
        searchSuggestionsContainer.style.display = 'none';
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/suggest_ingredients?query=${encodeURIComponent(searchValue)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) throw new Error('Network response was not ok');
            const suggestions = await response.json();

            searchSuggestionsContainer.innerHTML = '';

            if (suggestions.length > 0) {
                suggestions.forEach(suggestion => {
                    const suggestionElement = document.createElement('div');
                    suggestionElement.className = 'suggestion-item';
                    suggestionElement.textContent = suggestion;

                    suggestionElement.addEventListener('click', () => {
                        let foundIngredient = false;

                        // Show all categories temporarily
                        Object.keys(categories).forEach(categoryId => {
                            toggleCategory(categoryId, true);
                        });

                        document.querySelectorAll('.ingredient-item').forEach(item => {
                            if (item.textContent.toLowerCase() === suggestion.toLowerCase()) {
                                foundIngredient = true;
                                if (!item.classList.contains('disabled')) {
                                    item.classList.add('selected');
                                    const categoryList = item.parentElement;
                                    if (categoryList) {
                                        toggleCategory(categoryList.id, true);
                                    }
                                    updateSelectedIngredientsDisplay();
                                    item.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                }
                            }
                        });

                        searchSuggestionsContainer.style.display = 'none';
                        if (!foundIngredient) {
                            console.log('Ingredient not found:', suggestion);
                        }

                        updateCategoryVisibility();
                    });

                    searchSuggestionsContainer.appendChild(suggestionElement);
                });
                searchSuggestionsContainer.style.display = 'block';
            } else {
                searchSuggestionsContainer.style.display = 'none';
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            searchSuggestionsContainer.style.display = 'none';
        }
    }, 300);
}

// Event Listeners
searchBox.addEventListener('input', (event) => {
    filterIngredients();
    handleIngredientSearch(event);
});

searchBox.addEventListener('focus', () => {
    if (searchBox.value.trim()) {
        handleIngredientSearch({ target: searchBox });
    }
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('#ingredient-search') && !event.target.closest('.search-suggestions')) {
        searchSuggestionsContainer.style.display = 'none';
    }
});

// Add keyboard navigation for suggestions
searchBox.addEventListener('keydown', (event) => {
    const suggestions = searchSuggestionsContainer.querySelectorAll('.suggestion-item');
    const currentIndex = Array.from(suggestions).findIndex(el => el.classList.contains('highlighted'));

    switch(event.key) {
        case 'ArrowDown':
            event.preventDefault();
            if (currentIndex < suggestions.length - 1) {
                suggestions[currentIndex]?.classList.remove('highlighted');
                suggestions[currentIndex + 1].classList.add('highlighted');
            } else if (currentIndex === -1 && suggestions.length > 0) {
                suggestions[0].classList.add('highlighted');
            }
            break;

        case 'ArrowUp':
            event.preventDefault();
            if (currentIndex > 0) {
                suggestions[currentIndex].classList.remove('highlighted');
                suggestions[currentIndex - 1].classList.add('highlighted');
            }
            break;

        case 'Enter':
            const highlighted = searchSuggestionsContainer.querySelector('.suggestion-item.highlighted');
            if (highlighted) {
                event.preventDefault();
                highlighted.click();
            }
            break;
    }
});

// Add click handlers to all ingredient items
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
    updateSelectedIngredientsDisplay();
}

async function generateRecipe() {
    const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);

    const selectedCuisine = document.getElementById('cuisine').value;
    const customCuisine = document.getElementById('custom-cuisine').value;
    const cuisine = selectedCuisine === 'other' ? customCuisine : selectedCuisine;
    const mealType = document.getElementById('meal-type').value;
    const recipeMode = document.getElementById('recipe-mode').value;

    const recipeDisplay = document.getElementById('recipe-display');
    const spinner = document.getElementById('loading-spinner');

    if (selectedIngredients.length > 0) {
        recipeDisplay.innerHTML = '';
        spinner.style.display = 'flex';

        try {
            let endpoint, requestData;

            if (recipeMode === 'find') {
                endpoint = "/find_recipes";
                requestData = {
                    query: `${selectedIngredients.join(', ')}, ${cuisine}, ${mealType}`
                };
            } else {
                endpoint = "/generate_recipe";
                requestData = {
                    ingredients: selectedIngredients,
                    cuisine: cuisine,
                    meal_type: mealType
                };
            }

            console.log('Sending request to:', endpoint);
            console.log('Request data:', requestData);

            const response = await fetch(endpoint, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
            }

            const contentType = response.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
                const text = await response.text();
                console.error('Received non-JSON response:', text);
                throw new Error("Received non-JSON response from server");
            }

            const result = await response.json();
            console.log('Received result:', result);

            spinner.style.display = 'none';

            if (recipeMode === 'find') {
                // Display multiple recipes
                let recipesHtml = '<h3>Found Recipes</h3>';
                if (Array.isArray(result.recipes)) {
                    result.recipes.forEach((recipe, index) => {
                        recipesHtml += `
                            <div class="recipe-card">
                                <h4>${recipe.title || 'Untitled Recipe'}</h4>
                                <h5>Ingredients:</h5>
                                <p>${recipe.ingredients || 'No ingredients listed'}</p>
                                <h5>Instructions:</h5>
                                <p>${recipe.instructions || 'No instructions available'}</p>
                            </div>
                        `;
                    });
                } else {
                    recipesHtml += '<p>No recipes found</p>';
                }
                recipeDisplay.innerHTML = recipesHtml;
            } else {
                // Display generated recipe
                recipeDisplay.innerHTML = `<h3>Generated Recipe</h3>${result.recipe_html}`;
            }
        } catch (error) {
            console.error('Full error:', error);
            spinner.style.display = 'none';
            recipeDisplay.innerHTML = `<p>Error ${recipeMode === 'find' ? 'finding' : 'generating'} recipe: ${error.message}</p>`;
        }
    } else {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to ${recipeMode === 'find' ? 'find' : 'generate'} a recipe.</p>`;
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
    if (progressBar) {
        progressBar.style.width = progress + "%";
    }
}

async function fetchProgress() {
    const eventSource = new EventSource("/progress");
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateProgressBar(data.progress);

        if (data.progress >= 100) {
            eventSource.close();
        }
    };
}

function startRecipeGeneration() {
    fetchProgress();
    generateRecipe();
}