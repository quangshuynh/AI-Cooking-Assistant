// Theme management
function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const btn = document.getElementById('theme-toggle-btn');
    btn.textContent = theme === 'dark' ? '🌜' : '🌞';
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    setTheme(currentTheme === 'light' ? 'dark' : 'light');
}

// Easter egg and theme initialization
let titleClickCount = 0;
let easterEggActive = false;
const foodEmojis = ['🍕', '🌮', '🍜', '🍣', '🍔', '🌭', '🍖', '🍗', '🥩', '🥓', '🍱', '🥘', '🥗', '🥪', '🌯', '🥙', '🥨', '🧀', '🥐', '🥖', '🍎', '🍇', '🍉', '🍌', '🥑', '🥦', '🥕', '🌽', '🍪', '🍩', '🍰', '🍫', '🍬', '🍭', '🍡', '🍧', '🍨', '🍦', '🥮', '🍮', '😋'];

function activateEasterEgg() {
    if (easterEggActive) return;
    easterEggActive = true;
    
    const header = document.querySelector('header');
    const container = document.createElement('div');
    container.className = 'floating-emojis';
    container.id = 'floating-emojis-container';
    header.appendChild(container);

    foodEmojis.forEach((emoji, index) => {
        const floatingEmoji = document.createElement('span');
        floatingEmoji.className = 'floating-emoji';
        floatingEmoji.textContent = emoji;
        floatingEmoji.style.animationDelay = `${index * 0.3}s`;
        floatingEmoji.style.left = `${Math.random() * 100}%`;
        floatingEmoji.style.top = `${Math.random() * 100}%`;
        container.appendChild(floatingEmoji);
    });
}

function deactivateEasterEgg() {
    const container = document.getElementById('floating-emojis-container');
    if (container) {
        container.remove();
    }
    easterEggActive = false;
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.getElementById('theme-toggle-btn').addEventListener('click', toggleTheme);
    
    // Easter egg trigger
    const header = document.querySelector('header');
    let storedEasterEggState = localStorage.getItem('easterEggActive') === 'true';
    if (storedEasterEggState) {
        activateEasterEgg();
    }

    header.addEventListener('click', () => {
        titleClickCount++;
        if (titleClickCount >= 10) {
            if (!easterEggActive) {
                activateEasterEgg();
                localStorage.setItem('easterEggActive', 'true');
            } else if (titleClickCount >= 20) {
                deactivateEasterEgg();
                localStorage.setItem('easterEggActive', 'false');
                titleClickCount = 0;
            }
        }
    });
});

// Global variables
const categories = {
    "protein-list": false,
    "dairy-list": false,
    "fruits-list": false,
    "veggies-list": false,
    "grains-list": false,
    "misc-list": false
};

let searchTimeout;
const searchBox = document.getElementById('ingredient-search');
const searchSuggestionsContainer = document.createElement('div');
searchSuggestionsContainer.className = 'search-suggestions';
searchBox.parentNode.style.position = 'relative';
searchBox.parentNode.appendChild(searchSuggestionsContainer);

// Core ingredient selection functions
function selectIngredient(ingredient) {
    if (!ingredient || ingredient.classList.contains('disabled')) return;

    ingredient.classList.add('selected');
    const categoryList = ingredient.parentElement;
    if (categoryList) {
        categoryList.style.display = 'flex';
    }
    updateSelectedIngredientsDisplay();
}

function deselectIngredient(ingredient) {
    if (!ingredient) return;
    ingredient.classList.remove('selected');
    updateSelectedIngredientsDisplay();
}

function findIngredientElement(ingredientName) {
    return Array.from(document.querySelectorAll('.ingredient-item'))
        .find(item => item.textContent.toLowerCase() === ingredientName.toLowerCase());
}

// Category management
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

function showAllCategories() {
    Object.keys(categories).forEach(categoryId => {
        const category = document.getElementById(categoryId);
        if (category) {
            category.style.display = 'flex';
        }
    });
}

// Filtering system
function filterIngredients() {
    const searchValue = searchBox.value.toLowerCase();
    const selectedAllergies = Array.from(document.querySelectorAll('.allergy-checkbox:checked'))
        .map(checkbox => checkbox.value);
    const isVegetarian = document.getElementById('vegetarian-filter')?.checked;
    const isVegan = document.getElementById('vegan-filter')?.checked;

    const visibleCategories = new Set();

    document.querySelectorAll('.ingredient-item').forEach(item => {
        const ingredientText = item.textContent.toLowerCase();
        const category = item.parentElement;
        const allergens = item.getAttribute('data-allergens') || '';

        const isMeat = ['chicken', 'beef', 'turkey', 'shrimp', 'salmon', 'pork',
            'crab', 'lamb', 'bacon', 'ham', 'duck', 'venison', 'bison'].includes(ingredientText);

        const isAnimalProduct = isMeat || ['eggs', 'milk', 'cheese', 'yogurt', 'butter', 'cream',
            'sour cream', 'ice cream', 'whipped cream', 'cottage cheese', 'ghee', 'ricotta',
            'feta cheese', 'goat cheese', 'kefir'].includes(ingredientText);

        const matchesSearch = ingredientText.includes(searchValue);
        const hasAllergen = selectedAllergies.some(allergy => allergens.includes(allergy));
        const isFiltered = (isVegan && isAnimalProduct) || (isVegetarian && isMeat) || hasAllergen || !matchesSearch;

        if (isFiltered) {
            item.classList.add('disabled');
            if (!item.classList.contains('selected')) {
                item.style.display = 'none';
            }
        } else {
            item.classList.remove('disabled');
            item.style.display = 'block';
            if (category) {
                visibleCategories.add(category.id);
            }
        }
    });

    // Show only categories with visible ingredients
    Object.keys(categories).forEach(categoryId => {
        toggleCategory(categoryId, visibleCategories.has(categoryId));
    });
}

function handleSuggestionClick(suggestion) {
    // Show all categories temporarily to ensure we can find the ingredient
    Object.keys(categories).forEach(categoryId => {
        const category = document.getElementById(categoryId);
        if (category) {
            category.style.display = 'flex';
            category.querySelectorAll('.ingredient-item').forEach(item => {
                item.style.display = 'block';
            });
        }
    });

    // Find the ingredient
    let found = false;
    document.querySelectorAll('.ingredient-item').forEach(item => {
        if (item.textContent.toLowerCase() === suggestion.toLowerCase()) {
            found = true;
            if (!item.classList.contains('disabled')) {
                // Select the ingredient
                item.classList.add('selected');

                // Make sure its category is visible
                const categoryList = item.parentElement;
                if (categoryList) {
                    categoryList.style.display = 'flex';
                }

                // Scroll to the ingredient
                item.scrollIntoView({ behavior: 'smooth', block: 'center' });

                // Update the display
                updateSelectedIngredientsDisplay();
            }
        }
    });

    // Hide suggestions
    searchSuggestionsContainer.style.display = 'none';

    // Reapply filters
    filterIngredients();

    return found;
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
            const response = await fetch(`/suggest_ingredients?query=${encodeURIComponent(searchValue)}`);
            if (!response.ok) throw new Error('Network response was not ok');

            const suggestions = await response.json();
            searchSuggestionsContainer.innerHTML = '';

            if (suggestions.length > 0) {
                suggestions.forEach(suggestion => {
                    const suggestionElement = document.createElement('div');
                    suggestionElement.className = 'suggestion-item';
                    suggestionElement.textContent = suggestion;

                    suggestionElement.addEventListener('click', () => {
                        handleSuggestionClick(suggestion);
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

// Event listeners
searchBox.addEventListener('input', (event) => {
    filterIngredients();
    handleIngredientSearch(event);
});

document.addEventListener('click', (event) => {
    if (!event.target.closest('#ingredient-search') && !event.target.closest('.search-suggestions')) {
        searchSuggestionsContainer.style.display = 'none';
    }
});

// Add click handlers to all ingredient items
document.querySelectorAll('.ingredient-item').forEach(item => {
    item.addEventListener('click', () => {
        if (!item.classList.contains('disabled')) {
            if (item.classList.contains('selected')) {
                deselectIngredient(item);
            } else {
                selectIngredient(item);
            }
        }
    });
});

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

function unselectAllIngredients() {
    document.querySelectorAll('.ingredient-item.selected').forEach(item => {
        deselectIngredient(item);
    });
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

    if (selectedIngredients.length === 0) {
        recipeDisplay.innerHTML = `<p>Please select at least one ingredient to ${recipeMode === 'find' ? 'find' : 'generate'} a recipe.</p>`;
        return;
    }

    recipeDisplay.innerHTML = '';
    spinner.style.display = 'flex';

    try {
        const endpoint = recipeMode === 'find' ? '/find_recipes' : '/generate_recipe';
        const requestData = recipeMode === 'find'
            ? { query: `${selectedIngredients.join(', ')}, ${cuisine}, ${mealType}` }
            : { ingredients: selectedIngredients, cuisine: cuisine, meal_type: mealType };

        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const result = await response.json();

        spinner.style.display = 'none';

        if (recipeMode === 'find') {
            let recipesHtml = '<h3>Found Recipes</h3>';
            if (Array.isArray(result.recipes) && result.recipes.length > 0) {
                result.recipes.forEach((recipe, index) => {
                    // Split instructions into an array and clean up any empty lines
                    const instructionsArray = recipe.instructions
                        .split(/[.!?]\s+/)
                        .filter(instruction => instruction.trim().length > 0)
                        .map(instruction => instruction.trim());

                    // Split ingredients into an array and clean up
                    const ingredientsArray = recipe.ingredients
                        .split(',')
                        .map(ingredient => ingredient.trim())
                        .filter(ingredient => ingredient.length > 0);

                    recipesHtml += `
                        <div class="recipe-container">
                            <div class="recipe-header" onclick="toggleRecipeDetails('recipe-${index}')">
                                ${recipe.title || 'Untitled Recipe'}
                            </div>
                            <div class="recipe-content" id="recipe-${index}" style="display: none;">
                                <h4>Ingredients:</h4>
                                <ul>
                                    ${ingredientsArray.map(ingredient => `<li>${ingredient}</li>`).join('')}
                                </ul>
                                <h4>Instructions:</h4>
                                <ol>
                                    ${instructionsArray.map(instruction => `<li>${instruction}</li>`).join('')}
                                </ol>
                            </div>
                        </div>
                    `;
                });
            } else {
                recipesHtml += '<p>No recipes found</p>';
            }
            recipeDisplay.innerHTML = recipesHtml;
        } else {
            let recipesHtml = '<h3>Generated Recipes</h3>';
            if (Array.isArray(result.recipes) && result.recipes.length > 0) {
                result.recipes.forEach((recipe, index) => {
                    recipesHtml += `
                        <div class="recipe-container">
                            <div class="recipe-header" onclick="toggleRecipeDetails('recipe-${index}')">
                                ${recipe.name}
                            </div>
                            <div class="recipe-content" id="recipe-${index}" style="display: none;">
                                <p><strong>Description:</strong> ${recipe.description}</p>
                                <h4>Ingredients:</h4>
                                <ul>
                                    ${recipe.ingredients.map(ingredient => `<li>${ingredient}</li>`).join('')}
                                </ul>
                                <h4>Instructions:</h4>
                                <ol>
                                    ${recipe.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
                                </ol>
                            </div>
                        </div>
                    `;
                });
            } else {
                recipesHtml += '<p>No recipes generated</p>';
            }
            recipeDisplay.innerHTML = recipesHtml;
        }
    } catch (error) {
        spinner.style.display = 'none';
        recipeDisplay.innerHTML = `<p>Error ${recipeMode === 'find' ? 'finding' : 'generating'} recipe: ${error.message}</p>`;
    }
}

// Add this function if it's not already in your code
function toggleRecipeDetails(recipeId) {
    const recipeContent = document.getElementById(recipeId);
    if (recipeContent) {
        const currentDisplay = recipeContent.style.display;
        recipeContent.style.display = currentDisplay === 'none' ? 'block' : 'none';
    }
}

function toggleCustomCuisineInput() {
    const customCuisineInput = document.getElementById('custom-cuisine');
    customCuisineInput.style.display = document.getElementById('cuisine').value === 'other' ? 'block' : 'none';
    customCuisineInput.style.opacity = document.getElementById('cuisine').value === 'other' ? '1' : '0';
}

