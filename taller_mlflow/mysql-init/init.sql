-- Crea la tabla en la base de datos "mydatabase"
CREATE TABLE IF NOT EXISTS penguins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    species VARCHAR(100),
    island VARCHAR(100),
    culmen_length_mm FLOAT(10,2),
    culmen_depth_mm FLOAT(10,2),
    flipper_length_mm INT,
    body_mass_g INT,
    sex VARCHAR(100)
);

-- Otorga a 'admin' el privilegio FILE (si aún no lo has hecho)
GRANT FILE ON *.* TO 'admin'@'%';
FLUSH PRIVILEGES;

-- Carga los datos desde el archivo CSV, especificando las columnas a cargar
LOAD DATA INFILE '/var/lib/mysql-files/penguins_size.csv'
INTO TABLE penguins
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@species, @island, @culmen_length_mm, @culmen_depth_mm, @flipper_length_mm, @body_mass_g, @sex)
SET species = NULLIF(@species, 'NA'),
    island = NULLIF(@island, 'NA'),
    culmen_length_mm = NULLIF(@culmen_length_mm, 'NA'),
    culmen_depth_mm = NULLIF(@culmen_depth_mm, 'NA'),
    flipper_length_mm = NULLIF(@flipper_length_mm, 'NA'),
    body_mass_g = NULLIF(@body_mass_g, 'NA'),
    sex = NULLIF(@sex, 'NA');

