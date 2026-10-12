USE metopen_db;

-- Password for admin is 'admin123'
INSERT INTO users (username, password_hash, role)
VALUES ('admin', '$2b$12$9S38NK9dMAPIg4TqvHTU4OBeupH6tX5r4J.ERIS9sSAJOHsla0aea', 'admin')
ON DUPLICATE KEY UPDATE role = 'admin';
