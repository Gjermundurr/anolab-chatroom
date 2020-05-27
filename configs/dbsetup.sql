DROP DATABASE chatroom;
CREATE DATABASE chatroom;
USE chatroom;


CREATE TABLE users (
	USER_NAME VARCHAR(200) NOT NULL,
	PASSWORD  VARCHAR(200) NOT NULL,
	EMAIL_ADDRESS VARCHAR(200) NOT NULL,
	FULL_NAME VARCHAR(200) NOT NULL,
	PRIMARY KEY (USER_NAME)
);

/*
insert into clients (email, fullname) values
('gjermund.f.haugen@gmail.com', 'Gjermund F. Haugen'),
('tomas@valen.moe', 'Tomas Valen'),
('bv_mrcool@hotmail.com', 'Bjorn Victor V. Jorgensen'),
('jorgen@norstelien.com', 'Jorgen Norstelien');

insert into users (username, password, ) values
((select user_id from clients where email='gjermund.f.haugen@gmail.com'), 'jerry', '$2b$12$5j4Ce8SPnwfM9FIOtV99C.w5nNLi8fXKXJNVlDmwliX4wpRYpspLq'),
((select user_id from clients where email='jorgen@norstelien.com'), 'jorgen','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde'),
((select user_id from clients where email='bv_mrcool@hotmail.com'), 'bv','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde'),
((select user_id from clients where email='tomas@valen.moe'), 'tomas','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde');
*/