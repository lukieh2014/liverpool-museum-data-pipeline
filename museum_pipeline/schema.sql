
DROP TABLE IF EXISTS request_interaction;
DROP TABLE IF EXISTS rating_interaction;
DROP TABLE IF EXISTS exhibition;
DROP TABLE IF EXISTS request;
DROP TABLE IF EXISTS rating;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS floor;

SET datestyle TO DMY;

CREATE table floor (
    floor_id INT UNIQUE NOT NULL,
    floor_name VARCHAR(100) NOT NULL,
    primary key (floor_id)
);

INSERT INTO floor (floor_id, floor_name) VALUES
(0, 'Vault'),
(1, '1'),
(2, '2'),
(3, '3');

CREATE table department (
    department_id INT UNIQUE NOT NULL,
    department_name VARCHAR(100) NOT NULL,
    primary key (department_id)
);

INSERT INTO department (department_id, department_name) VALUES
(0, 'Entomology'),
(1, 'Geology'),
(2, 'Paleontology'),
(3, 'Zoology'),
(4, 'Ecology');

CREATE table rating (
    rating_id INT UNIQUE NOT NULL,
    rating_desc VARCHAR(100) NOT NULL,
    primary key (rating_id)
);

INSERT INTO rating (rating_id, rating_desc) VALUES
(0, 'Terrible'),
(1, 'Bad'),
(2, 'Neutral'),
(3, 'Good'),
(4, 'Amazing');

CREATE table request (
    request_id INT UNIQUE NOT NULL,
    request_desc VARCHAR(100) NOT NULL,
    primary key (request_id)
);

INSERT INTO request (request_id, request_desc) VALUES
(0, 'Assistance'),
(1, 'Emergency');

CREATE table exhibition (
    exhibition_id INT UNIQUE NOT NULL,
    exhibition_name VARCHAR(100) not null,
    exhibition_desc text,
    department_id int not null,
    floor_id int not null,
    exhibition_start date not null,
    public_id text,
    primary key (exhibition_id),
    foreign key (department_id) REFERENCES department(department_id),
    foreign key (floor_id) REFERENCES floor(floor_id)
);

INSERT INTO exhibition (exhibition_id, exhibition_name, exhibition_desc, department_id, floor_id, exhibition_start, public_id) VALUES
(1, 'Adaptation', 'How insect evolution has kept pace with an industrialised world', 0, 0, '01/07/19', 'EXH_01'),
(0, 'Measureless to Man', 'An immersive 3D experience: delve deep into a previously-inaccessible cave system.', 1, 1, '23/08/21', 'EXH_00'),
(5, 'Thunder Lizards', 'How new research is making scientists rethink what dinosaurs really looked like.', 2, 1, '01/02/23', 'EXH_05'),
(2, 'The Crenshaw Collection', 'An exhibition of 18th Century watercolours, mostly focused on South American wildlife.', 3, 2, '03/03/21', 'EXH_02'),
(4, 'Our Polluted World', 'A hard-hitting exploration of humanitys impact on the environment.', 4, 3, '12/05/21', 'EXH_04'),
(3, 'Cetacean Sensations', 'Whales: from ancient myth to critically endangered.', 3, 1, '01/07/19', 'EXH_03');

CREATE table request_interaction (
    request_interaction_id INT GENERATED ALWAYS AS IDENTITY,
    exhibition_id INT NOT NULL,
    request_id INT NOT NULL,
    event_at TIMESTAMP default CURRENT_TIMESTAMP,
    primary key (request_interaction_id),
    foreign key (exhibition_id) REFERENCES exhibition(exhibition_id),
    foreign key (request_id) REFERENCES request(request_id),
    CONSTRAINT valid_request_value CHECK (
        request_id = 0
        or request_id = 1
    )
);

CREATE table rating_interaction (
    rating_interaction_id INT GENERATED ALWAYS AS IDENTITY,
    exhibition_id INT NOT NULL,
    rating_id INT NOT NULL,
    event_at TIMESTAMP default CURRENT_TIMESTAMP,
    primary key (rating_interaction_id),
    foreign key (exhibition_id) REFERENCES exhibition(exhibition_id),
    foreign key (rating_id) REFERENCES rating(rating_id),
    CONSTRAINT valid_rating_value CHECK (
        rating_id >= 0
        AND rating_id <= 4
    )
);
