DROP DATABASE chatroom;
CREATE DATABASE chatroom;
USE chatroom;


CREATE TABLE users (
	USER_NAME VARCHAR(200) NOT NULL,
	PASSWORD  VARCHAR(255) NOT NULL,
	EMAIL_ADDRESS VARCHAR(255) NOT NULL,
	FULL_NAME VARCHAR(255) NOT NULL,
	PRIMARY KEY (USER_NAME)
);

CREATE USER 'sys-select'@'%' IDENTIFIED BY secret;
GRANT select on chatroom.users TO 'sys-select'@'%';

