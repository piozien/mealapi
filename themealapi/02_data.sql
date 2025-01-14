-- Adding users
INSERT INTO users (id, email, password, role) VALUES 
('123e4567-e89b-12d3-a456-426614174000', 'admin', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'ADMIN'),  -- password: admin123
('123e4567-e89b-12d3-a456-426614174001', 'user1', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'USER'),   -- password: admin123
('123e4567-e89b-12d3-a456-426614174002', 'user2', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'USER');   -- password: admin123
-- Adding recipes
INSERT INTO recipes (name, description, instructions, category, author, preparation_time, servings, difficulty, ingredients, steps, tags) VALUES
('Spaghetti Carbonara', 'A classic Italian pasta dish with an egg and pancetta-based sauce', 
'Prepare the ingredients and cook the pasta al dente. Meanwhile, prepare the sauce....', 'Main dishes', 
'123e4567-e89b-12d3-a456-426614174001', 30, 4, 'medium',
ARRAY['400g:spaghetti pasta', '200g:pancetta', '4:eggs', '100g:parmesan', 'to taste:salt', 'to taste:pepper'],  
ARRAY['Boil water and cook the pasta', 'Fry the pancetta', 'Mix the eggs with parmesan', 'Combine all ingredients', 'Serve hot'],  
ARRAY['Italian', 'pasta', 'quick']),


('Chocolate Brownie', 'Moist and intensely chocolatey cake',  
'Melt the chocolate with butter, add the remaining ingredients...', 'Desserts',  
'123e4567-e89b-12d3-a456-426614174002', 45, 8, 'easy',  
ARRAY['200g:butter', '200g:chocolate', '200g:sugar', '3:eggs', '120g:flour'],  
ARRAY['Melt the chocolate with butter', 'Mix with sugar', 'Add eggs and flour', 'Bake for 25 minutes'],  
ARRAY['dessert', 'chocolate', 'cake']),


('Greek Salad', 'A classic salad with tomatoes, cucumbers, and feta',  
'Chop the vegetables, add feta and olives...', 'Salads',  
'123e4567-e89b-12d3-a456-426614174001', 15, 2, 'easy',  
ARRAY['2:tomatoes', '1:cucumber', '100g:feta cheese', '50g:black olives', '1:red onion', 'to taste:olive oil'],  
ARRAY['Chop the vegetables into cubes', 'Add crumbled feta', 'Add olives', 'Drizzle with olive oil', 'Season to taste'],  
ARRAY['salad', 'vegetarian', 'Greek']),


('Chocolate Cake', 'A fluffy cake with chocolate cream',  
'Prepare the chocolate cake and cream...', 'Desserts',  
'123e4567-e89b-12d3-a456-426614174002', 90, 12, 'medium',  
ARRAY['250g:butter', '300g:dark chocolate', '250g:sugar', '6:eggs', '200g:flour', '500ml:heavy cream (36%)'],  
ARRAY['Prepare the cake batter', 'Bake the layers', 'Prepare the cream', 'Assemble the cake', 'Decorate'],  
ARRAY['cake', 'chocolate', 'celebrations']);


-- Adding ratings
INSERT INTO ratings (author, recipe_id, value) VALUES
('123e4567-e89b-12d3-a456-426614174001', 1, 5),
('123e4567-e89b-12d3-a456-426614174002', 1, 4),
('123e4567-e89b-12d3-a456-426614174001', 2, 5);

-- Adding comments
INSERT INTO comments (author, recipe_id, content, rating_id) VALUES  
('123e4567-e89b-12d3-a456-426614174001', 1, 'Great recipe! It turned out just like in a restaurant.', 1),  
('123e4567-e89b-12d3-a456-426614174002', 1, 'Very good, but I would add more pepper.', 2),  
('123e4567-e89b-12d3-a456-426614174001', 2, 'The best brownie I’ve ever had!', 3),  
('123e4567-e89b-12d3-a456-426614174002', 3, 'Simple and tasty salad.', NULL);  
