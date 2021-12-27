CREATE TABLE offloading_sites (
   id VARCHAR (255) NOT NULL PRIMARY KEY,
   mips SMALLINT NOT NULL,
   memory SMALLINT NOT NULL,
   storage SMALLINT NOT NULL,
   name VARCHAR (255) NOT NULL,
   url_svc VARCHAR (255) NOT NULL
);

INSERT INTO offloading_sites (id, mips, memory, storage, name, url_svc)
VALUES
 ('Edge Database Server', 5000, 8, 300, 'A', 'http://128.131.169.143:30256/database/'),
 ('Edge Computational Intensive Server', 8000, 8, 150, 'A', 'http://128.131.169.143:30256/comp/'),
 ('Edge Regular Server', 5000, 8, 150, 'A', 'http://128.131.169.143:30256/regular/'),
 ('Cloud Data Center', 12000, 128, 1000, 'A', 'http://128.131.169.143:30256/cloud/'),
 ('Mobile Device', 1000, 8, 16, 'A', 'N/A');




CREATE TABLE network_connections (
   id serial PRIMARY KEY,
   first_site_id VARCHAR (255) NOT NULL,
   second_site_id VARCHAR (255) NOT NULL,
   bandwidth real NOT NULL,
   FOREIGN KEY (first_site_id) REFERENCES offloading_sites (id),
   FOREIGN KEY (second_site_id) REFERENCES offloading_sites (id)
);

INSERT INTO network_connections (first_site_id, second_site_id, bandwidth)
VALUES
 ('Cloud Data Center', 'Edge Database Server', 123000),
 ('Cloud Data Center', 'Edge Computational Intensive Server', 12500),
 ('Cloud Data Center', 'Edge Regular Server', 12500),
 ('Cloud Data Center', 'Mobile Device', 2500),
 ('Edge Database Server', 'Edge Computational Intensive Server', 123000),
 ('Edge Database Server', 'Edge Regular Server', 123000),
 ('Edge Database Server', 'Mobile Device', 2500),
 ('Edge Computational Intensive Server', 'Edge Regular Server', 12500),
 ('Edge Computational Intensive Server', 'Mobile Device', 687.5),
 ('Edge Regular Server', 'Mobile Device', 687.5);




CREATE TABLE mobile_applications (
   id VARCHAR (255) NOT NULL PRIMARY KEY
);

INSERT INTO mobile_applications (id)
VALUES
 ('ANTIVIRUS'), ('CHESS'), ('FACERECOGNIZER'), ('GPS'), ('FACEBOOK');




CREATE TABLE application_tasks (
   id serial PRIMARY KEY,
   name VARCHAR (255) NOT NULL,
   memory SMALLINT NOT NULL,
   offloadability boolean NOT NULL,
   application_id VARCHAR (255) NOT NULL,
   next_tasks TEXT [],
   FOREIGN KEY (application_id) REFERENCES mobile_applications (id)
);

INSERT INTO application_tasks (name, memory, offloadability, application_id, next_tasks)
VALUES
 ('GUI', 1, FALSE, 'ANTIVIRUS', '{"LOAD_LIBRARY", "SCAN_FILE"}'),
 ('LOAD_LIBRARY', 1, TRUE, 'ANTIVIRUS', '{"COMPARE"}'),
 ('SCAN_FILE', 2, TRUE, 'ANTIVIRUS', '{"COMPARE"}'),
 ('COMPARE', 1, TRUE, 'ANTIVIRUS', '{"OUTPUT"}'),
 ('OUTPUT', 1, FALSE, 'ANTIVIRUS', '{}'),
 ('GUI', 1, FALSE, 'FACERECOGNIZER', '{"FIND_MATCH"}'),
 ('FIND_MATCH', 1, TRUE, 'FACERECOGNIZER', '{"INIT", "DETECT_FACE"}'),
 ('INIT', 2, TRUE, 'FACERECOGNIZER', '{"DETECT_FACE"}'),
 ('DETECT_FACE', 1, TRUE, 'FACERECOGNIZER', '{"OUTPUT"}'),
 ('OUTPUT', 1, FALSE, 'FACERECOGNIZER', '{}'),
 ('GUI', 1, FALSE, 'CHESS', '{"UPDATE_CHESS"}'),
 ('UPDATE_CHESS', 1, TRUE, 'CHESS', '{"COMPUTE_MOVE"}'),
 ('COMPUTE_MOVE', 2, TRUE, 'CHESS', '{"OUTPUT"}'),
 ('OUTPUT', 1, FALSE, 'CHESS', '{}'),
 ('FACEBOOK_GUI', 1, FALSE, 'FACEBOOK', '{"GET_TOKEN", "POST_REQUEST"}'),
 ('GET_TOKEN', 1, TRUE, 'FACEBOOK', '{"POST_REQUEST"}'),
 ('POST_REQUEST', 2, TRUE, 'FACEBOOK', '{"PROCESS_RESPONSE"}'),
 ('PROCESS_RESPONSE', 2, TRUE, 'FACEBOOK', '{"FILE_UPLOAD"}'),
 ('FILE_UPLOAD', 2, FALSE, 'FACEBOOK', '"{APPLY_FILTER"}'),
 ('APPLY_FILTER', 2, TRUE, 'FACEBOOK', 'FACEBOOK_POST'),
 ('FACEBOOK_POST', 2, FALSE, 'FACEBOOK', 'OUTPUT'),
 ('OUTPUT', 1, FALSE, 'FACEBOOK', ''),
 ('CONF_PANEL', 1, FALSE, 'GPS', 'CONTROL'),
 ('GPS', 2, FALSE, 'GPS', 'CONTROL'),
 ('CONTROL', 5, TRUE, 'GPS', 'MAPS, PATH_CALC, TRAFFIC'),
 ('MAPS', 5, TRUE, 'GPS', 'PATH_CALC'),
 ('TRAFFIC', 1, TRUE, 'GPS', 'PATH_CALC'),
 ('PATH_CALC', 2, TRUE, 'GPS', 'VOICE_SYNTH, GUI, SPEED_TRAP'),
 ('VOICE_SYNTH', 1, FALSE, 'GPS', ''),
 ('GUI', 1, FALSE, 'GPS', ''),
 ('SPEED_TRAP', 1, FALSE, 'GPS', '');
