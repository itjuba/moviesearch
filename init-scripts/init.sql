CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY NOT NULL,
    username VARCHAR NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);



CREATE TABLE movie_ratings (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    movie_id VARCHAR,
    title VARCHAR UNIQUE NOT NULL,
    user_vote VARCHAR,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Define a composite unique constraint for user_id and movie_id
    UNIQUE (user_id, movie_id)
);
