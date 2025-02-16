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
    
    // Don't scroll when selecting ingredients
}

function clearSearch() {
    const searchBox = document.getElementById('ingredient-search');
    searchBox.value = '';
    filterIngredients();
    searchBox.focus();
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
    // Create a new ingredient button directly
    const container = document.getElementById('selected-ingredients-container');
    const existingIngredients = Array.from(document.querySelectorAll('.selected-ingredient-button'))
        .map(btn => btn.textContent.toLowerCase());
    
    // Capitalize first letter of each word
    const formattedSuggestion = suggestion.split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    
    // Only add if not already selected (case-insensitive check)
    if (!existingIngredients.includes(suggestion.toLowerCase())) {
        const button = document.createElement('button');
        button.className = 'selected-ingredient-button';
        button.textContent = formattedSuggestion;
        button.onclick = () => removeIngredient(formattedSuggestion);
        container.appendChild(button);
        
        // Also update the selected ingredients list
        const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-item.selected'))
            .map(item => item.textContent);
        selectedIngredients.push(formattedSuggestion);
    }

    // Hide suggestions and clear search
    searchSuggestionsContainer.style.display = 'none';
    clearSearch();
    return true;
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
    const container = document.getElementById('selected-ingredients-container');
    
    // Get currently selected ingredients from both sources
    const selectedFromList = Array.from(document.querySelectorAll('.ingredient-item.selected'))
        .map(item => item.textContent);
    const selectedFromSuggestions = Array.from(document.querySelectorAll('.selected-ingredient-button'))
        .map(btn => btn.textContent);
    
    // Combine and deduplicate ingredients (case-insensitive)
    const allIngredients = [...new Set([...selectedFromList, ...selectedFromSuggestions].map(ing => ing.toLowerCase()))]
        .map(ing => ing.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' '));
    
    if (allIngredients.length > 0) {
        container.innerHTML = allIngredients.map(ingredient => 
            `<button class="selected-ingredient-button" onclick="removeIngredient('${ingredient}')">${ingredient}</button>`
        ).join('');
    } else {
        container.innerHTML = '';
    }

    // Store all selected ingredients in a data attribute for easy access
    container.setAttribute('data-selected-ingredients', JSON.stringify(allIngredients));
}

function removeIngredient(ingredientName) {
    // Remove from selected ingredients display
    const button = Array.from(document.getElementsByClassName('selected-ingredient-button'))
        .find(btn => btn.textContent === ingredientName);
    if (button) {
        button.remove();
    }

    // Deselect from ingredient list if it exists there
    const ingredient = findIngredientElement(ingredientName);
    if (ingredient) {
        deselectIngredient(ingredient);
    }
}

function unselectAllIngredients() {
    // Clear selected ingredients from the list
    document.querySelectorAll('.ingredient-item.selected').forEach(item => {
        deselectIngredient(item);
    });
    
    // Clear selected ingredients container
    const container = document.getElementById('selected-ingredients-container');
    container.innerHTML = '';
    container.setAttribute('data-selected-ingredients', '[]');
}

async function generateRecipe() {
    const container = document.getElementById('selected-ingredients-container');
    const selectedButtons = container.getElementsByClassName('selected-ingredient-button');
    const selectedIngredients = Array.from(selectedButtons).map(btn => btn.textContent);

    const selectedCuisine = document.getElementById('cuisine').value;
    const customCuisine = document.getElementById('custom-cuisine').value;
    const cuisine = selectedCuisine === 'other' ? customCuisine : selectedCuisine;
    const mealType = document.getElementById('meal-type').value;
    const recipeMode = document.getElementById('recipe-mode').value;
    const modelProvider = document.getElementById('model-provider').value;

    const recipeDisplay = document.getElementById('recipe-display');
    const spinner = document.getElementById('loading-spinner');
    const generateBtn = document.getElementById('generate-btn');
    const cancelBtn = document.getElementById('cancel-btn');

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

        generateBtn.disabled = true;
        cancelBtn.style.display = 'inline-block';

        const controller = new AbortController();
        currentRequest = controller;

        const response = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ...requestData,
                model_provider: modelProvider
            }),
            signal: controller.signal
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const result = await response.json();

        spinner.style.display = 'none';

        if (recipeMode === 'find') {
            let recipesHtml = '<h3>Found Recipes</h3>';
            if (Array.isArray(result.recipes) && result.recipes.length > 0) {
                result.recipes.forEach((recipe, index) => {
                    // Handle instructions
                    const instructionsArray = typeof recipe.instructions === 'string' 
                        ? recipe.instructions
                            .split(/[.!?]\s+/)
                            .filter(instruction => instruction.trim().length > 0)
                            .map(instruction => instruction.trim())
                        : [recipe.instructions];

                    // Handle ingredients
                    const ingredientsArray = Array.isArray(recipe.ingredients)
                        ? recipe.ingredients
                        : typeof recipe.ingredients === 'string'
                            ? recipe.ingredients.split(',').map(i => i.trim()).filter(i => i.length > 0)
                            : [];

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
            
            // Hide cancel button and re-enable generate button when done
            document.getElementById('cancel-btn').style.display = 'none';
            document.getElementById('generate-btn').disabled = false;
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

let currentRequest = null;

function toggleCustomCuisineInput() {
    const customCuisineInput = document.getElementById('custom-cuisine');
    customCuisineInput.style.display = document.getElementById('cuisine').value === 'other' ? 'block' : 'none';
    customCuisineInput.style.opacity = document.getElementById('cuisine').value === 'other' ? '1' : '0';
}

function updateModelSelection() {
    const recipeMode = document.getElementById('recipe-mode').value;
    const modelSelection = document.getElementById('model-selection');
    modelSelection.style.display = recipeMode === 'generate' ? 'block' : 'none';
}

function cancelGeneration() {
    if (currentRequest) {
        currentRequest.abort();
        currentRequest = null;
    }
    document.getElementById('loading-spinner').style.display = 'none';
    document.getElementById('generate-btn').disabled = false;
    document.getElementById('cancel-btn').style.display = 'none';
}

// Add event listener for recipe mode change
document.getElementById('recipe-mode').addEventListener('change', updateModelSelection);

