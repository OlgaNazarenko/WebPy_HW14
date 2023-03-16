PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
INSERT INTO alembic_version VALUES('cd2bcd68998d');
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(50), 
	email VARCHAR(150), 
	password VARCHAR(255) NOT NULL, 
	created_at DATETIME, 
	refresh_token VARCHAR(255), confirmed BOOLEAN, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
INSERT INTO users VALUES(1,'Japan','japan@gmail.com','$2b$12$hZ0x/tibbRhi5LI9SyyJUOHTOVg8rEWZz..kEz/2j3NvNR/IxVjny','2023-02-25 12:20:44','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqYXBhbkBnbWFpbC5jb20iLCJpYXQiOjE2Nzc0MjE1MjQsImV4cCI6MTY3ODAyNjMyNCwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.yYScwW16NMalaY3y4vV0gVPXr-yyQFqAzGTI7iOtsa0',NULL);
INSERT INTO users VALUES(2,'Japan','japan@example.com','$2b$12$/JCObckufmknwBPl.yWBf.6VuDd9zCxxQzAVVNQ0aHQMTdwgIvMSm','2023-02-25 14:46:10',NULL,NULL);
INSERT INTO users VALUES(3,'seoul_tokyo','seoul_tokyo@example.com','$2b$12$u1EH7bBBsiWLrYR1.P9IHuzH9t2Oe3sSnJKXNI2Y8qxDAWDMXzYbe','2023-03-02 19:25:19',NULL,0);
INSERT INTO users VALUES(4,'Martin_kot','martin_kot@meta.ua','$2b$12$7lMK3j35KAngZWQ5.z.t6eiqGrdgHACCz5/sS08tDdU.ync7Ul66G','2023-03-02 19:32:14',NULL,0);
INSERT INTO users VALUES(5,'Martin_kot','martin.kot@meta.ua','$2b$12$8ByuT0jij2IDguROUUeGVOX9.TFHufjpgYAgSISnd3ru90MjjryTK','2023-03-02 19:33:15','eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJ0aW4ua290QG1ldGEudWEiLCJpYXQiOjE2Nzc3ODU3OTQsImV4cCI6MTY3ODM5MDU5NCwic2NvcGUiOiJyZWZyZXNoX3Rva2VuIn0.hiBbjDhtwRIt4FOH8p00KcRE_F--gKmdPYcl-L6LODE',1);
CREATE TABLE contacts (
	id INTEGER NOT NULL, 
	name VARCHAR(50) NOT NULL, 
	surname VARCHAR(50) NOT NULL, 
	email VARCHAR(100), 
	mobile INTEGER, 
	date_of_birth DATE, 
	user_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);
INSERT INTO contacts VALUES(1,'Bitter','Brown','brown@gmail.com',123456789,'1999-02-25',1);
INSERT INTO contacts VALUES(2,'James','Song','song@gmail.com',123456789,'1992-03-07',1);
INSERT INTO contacts VALUES(3,'Nicky','Kang','kang@gmail.com',123456789,'1999-03-05',1);
INSERT INTO contacts VALUES(4,'Jin','Huang','huang@gmail.com',123456789,'1999-03-04',1);
INSERT INTO contacts VALUES(5,'Jimin','Jackson','jackson@gmail.com',123456789,'1999-03-06',1);
INSERT INTO contacts VALUES(6,'Nancy','James','Nancy.james@gmail.com',123456789,'1999-03-07',1);
INSERT INTO contacts VALUES(7,'Drew','James','drew.james@gmail.com',123456789,'1999-03-07',1);
INSERT INTO contacts VALUES(8,'Bosch','James','bosch.james@gmail.com',123456789,'1999-03-08',1);
INSERT INTO contacts VALUES(9,'Star','Hong Kong','star@gmail.com',123456789,'1999-03-03',1);
INSERT INTO contacts VALUES(10,'Jenny','Seoul','seoul@example.com',123456789,'1987-02-04',1);
INSERT INTO contacts VALUES(11,'Jenny','Kang','japan@example.com',123456789,'1987-02-04',1);
INSERT INTO contacts VALUES(12,'Kim','Soo-hyun','so-hyun@example.com',123456789,'1987-02-04',1);
INSERT INTO contacts VALUES(13,'Hyun','Bin','bin@example.com',123456789,'1987-02-04',1);
INSERT INTO contacts VALUES(14,'Lee','Min-ho','Min-ho@example.com',123456789,'1987-02-04',1);
INSERT INTO contacts VALUES(15,'Ji Chang','Wook','chang@example.com',123456789,'1987-03-04',1);
INSERT INTO contacts VALUES(16,'Nam','Joo-hyuk','Joo-hyuk@example.com',123456789,'1987-03-04',1);
INSERT INTO contacts VALUES(17,'Song','Hye-kyo','Hye-kyo@example.com',123456789,'1987-03-07',1);
INSERT INTO contacts VALUES(18,'Song','Hyekyo','Hyekyo@example.com',123456789,'1987-03-08',1);
INSERT INTO contacts VALUES(19,'Seo','Kang-joon','Kang-joon@example.com',123456789,'1987-03-08',1);
INSERT INTO contacts VALUES(20,'Hae-in','Hae-in','Hae-in@example.com',123456789,'1987-03-08',1);
INSERT INTO contacts VALUES(21,'Olga','Kang','tobe@example.com',123456789,'2000-03-04',1);
CREATE UNIQUE INDEX ix_contacts_email ON contacts (email);
CREATE INDEX ix_contacts_name ON contacts (name);
CREATE INDEX ix_contacts_surname ON contacts (surname);
COMMIT;
