-- Tworzenie typów enum
CREATE TYPE user_role AS ENUM ('ADMIN', 'USER');
CREATE TYPE report_reason AS ENUM ('SPAM', 'INAPPROPRIATE', 'INCORRECT', 'OTHER');
CREATE TYPE report_status AS ENUM ('PENDING', 'RESOLVED', 'REJECTED');

-- Tworzenie tabel
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    password VARCHAR,
    role user_role DEFAULT 'USER'
);

CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    name VARCHAR,
    description VARCHAR,
    instructions VARCHAR,
    category VARCHAR,
    author UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE,
    preparation_time INTEGER CHECK (preparation_time > 0),
    servings INTEGER CHECK (servings > 0),
    difficulty VARCHAR,
    average_rating FLOAT DEFAULT 0.0 CHECK (average_rating >= 0 AND average_rating <= 5),
    ingredients VARCHAR[],
    steps VARCHAR[],
    tags VARCHAR[],
    ai_detected FLOAT CHECK (ai_detected >= 0 AND ai_detected <= 1)
);

CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    author UUID REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    value INTEGER,
    created_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    author UUID REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    created_at TIMESTAMP WITH TIME ZONE,
    content VARCHAR,
    rating_id INTEGER REFERENCES ratings(id)
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    reporter_id UUID REFERENCES users(id),
    recipe_id INTEGER REFERENCES recipes(id),
    comment_id INTEGER REFERENCES comments(id),
    reason report_reason,
    description VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE,
    status report_status DEFAULT 'PENDING',
    resolved_by UUID REFERENCES users(id),
    resolution_note VARCHAR,
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Tworzenie indeksów
CREATE INDEX idx_recipes_name ON recipes(name);
CREATE INDEX idx_recipes_category ON recipes(category);
CREATE INDEX idx_recipes_author ON recipes(author);
CREATE INDEX idx_recipes_preparation_time ON recipes(preparation_time);
CREATE INDEX idx_recipes_average_rating ON recipes(average_rating);
