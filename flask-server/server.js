// server.js
const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Failed to connect to MongoDB', err));

// Define Ingredient schema and model
const ingredientSchema = new mongoose.Schema({
    name: String,
    allergens: [String],
    cost: Number,
    cuisine: String,
    mealType: String,
});

const Ingredient = mongoose.model('Ingredient', ingredientSchema);

// Route to search ingredients
app.get('/api/ingredients', async (req, res) => {
    const query = req.query.query;
    if (!query) {
        return res.status(400).json({ error: 'Query parameter is required' });
    }

    try {
        const ingredients = await Ingredient.find({
            name: { $regex: query, $options: 'i' }  // Case-insensitive search
        }).limit(10);
        
        res.json(ingredients);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Error fetching ingredients' });
    }
});

// Route to search recipes based on selected criteria
app.get('/api/recipes', async (req, res) => {
    const { ingredients, allergies, maxCost, cuisine, mealType } = req.query;
    const ingredientList = ingredients ? ingredients.split(',') : [];

    try {
        // Query MongoDB to find matching ingredients
        const query = {
            name: { $in: ingredientList },
            cost: maxCost ? { $lte: parseInt(maxCost) } : { $exists: true },
            cuisine: cuisine || { $exists: true },
            mealType: mealType || { $exists: true },
            allergens: allergies ? { $nin: allergies.split(',') } : { $exists: true },
        };

        const matchingIngredients = await Ingredient.find(query);
        
        res.json(matchingIngredients);
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Error fetching recipes' });
    }
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
