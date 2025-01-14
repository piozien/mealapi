-- Dodanie użytkowników
INSERT INTO users (id, email, password, role) VALUES 
('123e4567-e89b-12d3-a456-426614174000', 'admin', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'ADMIN'),  -- hasło: admin123
('123e4567-e89b-12d3-a456-426614174001', 'user1', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'USER'),   -- hasło: admin123
('123e4567-e89b-12d3-a456-426614174002', 'user2', '$2b$12$5Qd/obiEBXIr0HiL3Xm5xusPLOAhL9gsSMcCk0tIxAfAyJGLHYJIG', 'USER');   -- hasło: admin123

-- Dodanie przepisów
INSERT INTO recipes (id, name, description, instructions, category, author, created_at, preparation_time, servings, difficulty, ingredients, steps, tags) VALUES
(1, 'Spaghetti Carbonara', 'Klasyczne włoskie danie z makaronu z sosem na bazie jajek i pancetty', 
'Przygotuj składniki i ugotuj makaron al dente. W międzczasie przygotuj sos...', 'Dania główne', 
'123e4567-e89b-12d3-a456-426614174001', '2023-12-14 12:00:00+00', 30, 4, 'średni',
ARRAY['400g:makaron spaghetti', '200g:pancetta', '4:jajka', '100g:parmezan', 'do smaku:sól', 'do smaku:pieprz'],
ARRAY['Ugotuj makaron', 'Podsmaż pancettę', 'Przygotuj sos z jajek i sera', 'Połącz wszystkie składniki'],
ARRAY['włoskie', 'makaron', 'szybkie']),

(2, 'Brownie czekoladowe', 'Wilgotne i intensywnie czekoladowe ciasto', 
'Rozpuść czekoladę z masłem, dodaj pozostałe składniki...', 'Desery', 
'123e4567-e89b-12d3-a456-426614174002', '2023-12-14 13:00:00+00', 45, 8, 'łatwy',
ARRAY['200g:masło', '200g:czekolada', '200g:cukier', '3:jajka', '120g:mąka'],
ARRAY['Rozpuść czekoladę z masłem', 'Wymieszaj składniki suche', 'Połącz wszystko', 'Piecz 25 minut'],
ARRAY['deser', 'czekolada', 'ciasto']),

(3, 'Sałatka grecka', 'Klasyczna sałatka z pomidorów, ogórków i fety', 
'Pokrój warzywa, dodaj fetę i oliwki...', 'Sałatki', 
'123e4567-e89b-12d3-a456-426614174001', '2023-12-14 14:00:00+00', 15, 2, 'łatwy',
ARRAY['2:pomidory', '1:ogórek', '100g:ser feta', '50g:oliwki czarne', '1:czerwona cebula', 'do smaku:oliwa z oliwek'],
ARRAY['Pokrój warzywa', 'Dodaj fetę i oliwki', 'Skrop oliwą', 'Dopraw solą i pieprzem'],
ARRAY['sałatka', 'wegetariańskie', 'greckie']),

(4, 'Tort czekoladowy', 'Puszysty tort z kremem czekoladowym', 
'Przygotuj ciasto czekoladowe i krem...', 'Desery', 
'123e4567-e89b-12d3-a456-426614174002', '2023-12-14 15:00:00+00', 90, 12, 'średni',
ARRAY['250g:masło', '300g:czekolada deserowa', '250g:cukier', '6:jajka', '200g:mąka', '500ml:śmietana 36%'],
ARRAY['Rozpuść czekoladę z masłem', 'Ubij jajka z cukrem', 'Dodaj mąkę i proszek', 'Upiecz biszkopt', 'Przygotuj krem', 'Przełóż tort kremem'],
ARRAY['deser', 'czekolada', 'tort', 'przyjęcia']);

-- Reset sekwencji dla recipes
ALTER SEQUENCE recipes_id_seq RESTART WITH 5;

-- Reset sekwencji dla ratings
ALTER SEQUENCE ratings_id_seq RESTART WITH 4;

-- Reset sekwencji dla comments
ALTER SEQUENCE comments_id_seq RESTART WITH 5;

-- Dodanie ocen
INSERT INTO ratings (id, author, recipe_id, value, created_at) VALUES
(1, '123e4567-e89b-12d3-a456-426614174001', 1, 5, '2023-12-14 15:00:00+00'),
(2, '123e4567-e89b-12d3-a456-426614174002', 1, 4, '2023-12-14 15:30:00+00'),
(3, '123e4567-e89b-12d3-a456-426614174001', 2, 5, '2023-12-14 16:00:00+00');

-- Dodanie komentarzy
INSERT INTO comments (id, author, recipe_id, created_at, content, rating_id) VALUES
(1, '123e4567-e89b-12d3-a456-426614174001', 1, '2023-12-14 15:00:00+00', 'Świetny przepis! Wyszło dokładnie jak w restauracji.', 1),
(2, '123e4567-e89b-12d3-a456-426614174002', 1, '2023-12-14 15:30:00+00', 'Bardzo dobre, ale dodałbym więcej pieprzu.', 2),
(3, '123e4567-e89b-12d3-a456-426614174001', 2, '2023-12-14 16:00:00+00', 'Najlepsze brownie jakie jadłem!', 3),
(4, '123e4567-e89b-12d3-a456-426614174002', 3, '2023-12-14 16:30:00+00', 'Prosta i smaczna sałatka.', NULL);