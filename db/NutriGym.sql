CREATE DATABASE IF NOT EXISTS NUTRIGYM;

USE NUTRIGYM;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    age INT NULL,
    weight FLOAT NULL
);

-- Nutrition Table
CREATE TABLE IF NOT EXISTS nutrition (
    id INT AUTO_INCREMENT PRIMARY KEY,
    gym_hours INT NOT NULL,
    gym_time ENUM('morning', 'afternoon', 'evening') NOT NULL,
    calories INT,
    protein INT,
    carbs INT,
    fats INT
);

-- Recipes Table
CREATE TABLE IF NOT EXISTS recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    type ENUM('breakfast', 'salad', 'smoothie') NOT NULL,
    ingredients TEXT,
    instructions TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Default Breakfast Recipes
INSERT INTO recipes (user_id, name, type, ingredients, instructions, is_approved) VALUES
(NULL, 'Oatmeal Bowl', 'breakfast', 'Oats, Milk, Honey, Banana', 'Mix oats with milk, cook, top with honey and banana.', TRUE),
(NULL, 'Egg White Omelette', 'breakfast', 'Egg whites, Spinach, Tomato, Onion', 'Whisk egg whites, add veggies, cook in pan.', TRUE),
(NULL, 'Greek Yogurt Parfait', 'breakfast', 'Greek yogurt, Berries, Granola, Honey', 'Layer yogurt, berries, granola, drizzle honey.', TRUE),
(NULL, 'Avocado Toast', 'breakfast', 'Whole grain bread, Avocado, Lemon, Salt', 'Toast bread, mash avocado, spread, season.', TRUE),
(NULL, 'Peanut Butter Banana Toast', 'breakfast', 'Bread, Peanut butter, Banana', 'Spread peanut butter on toast, top with banana.', TRUE);

-- Default Salad Recipes
INSERT INTO recipes (user_id, name, type, ingredients, instructions, is_approved) VALUES
(NULL, 'Greek Salad', 'salad', 'Tomatoes, Cucumber, Feta, Olives, Olive oil', 'Chop veggies, mix, add feta and olives, drizzle oil.', TRUE),
(NULL, 'Quinoa Salad', 'salad', 'Quinoa, Chickpeas, Bell pepper, Lemon', 'Cook quinoa, mix with other ingredients.', TRUE),
(NULL, 'Caesar Salad', 'salad', 'Romaine, Croutons, Parmesan, Caesar dressing', 'Toss all ingredients together.', TRUE),
(NULL, 'Spinach Strawberry Salad', 'salad', 'Spinach, Strawberries, Almonds, Balsamic', 'Mix spinach, sliced strawberries, almonds, drizzle balsamic.', TRUE),
(NULL, 'Chickpea Salad', 'salad', 'Chickpeas, Tomato, Cucumber, Lemon, Parsley', 'Mix all ingredients, season to taste.', TRUE);

-- Default Smoothie Recipes
INSERT INTO recipes (user_id, name, type, ingredients, instructions, is_approved) VALUES
(NULL, 'Berry Blast Smoothie', 'smoothie', 'Mixed berries, Yogurt, Honey, Ice', 'Blend all ingredients until smooth.', TRUE),
(NULL, 'Green Power Smoothie', 'smoothie', 'Spinach, Banana, Apple, Water', 'Blend all ingredients until smooth.', TRUE),
(NULL, 'Mango Lassi', 'smoothie', 'Mango, Yogurt, Honey, Cardamom', 'Blend mango with yogurt, honey, and cardamom.', TRUE),
(NULL, 'Peanut Butter Banana Smoothie', 'smoothie', 'Banana, Peanut butter, Milk, Honey', 'Blend all ingredients until smooth.', TRUE),
(NULL, 'Pineapple Coconut Smoothie', 'smoothie', 'Pineapple, Coconut milk, Banana, Ice', 'Blend all ingredients until smooth.', TRUE); 

SELECT User, Host, authentication_string, plugin
  FROM mysql.user
  WHERE User = 'root';
  
show tables;

describe users;

ALTER TABLE USERS ADD age INT NULL;
ALTER TABLE USERS ADD weight FLOAT NULL;
ALTER TABLE USERS ADD gender ENUM('Male', 'Female', 'Other');
ALTER TABLE USERS ADD goal ENUM('lose','gain','maintain');

ALTER TABLE USERS
CHANGE COLUMN GENDER gender ENUM('Male', 'Female', 'Other') NULL;

COMMIT;



