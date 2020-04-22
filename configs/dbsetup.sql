DROP DATABASE chatroom;
CREATE DATABASE chatroom;
USE CHATROOM;

CREATE TABLE clients (
user_id INT NOT NULL AUTO_INCREMENT,
email varchar(100),
fullname varchar(100),
PRIMARY KEY (user_id)
);

CREATE TABLE users (
user_id INT NOT NULL,
username varchar(50) NOT NULL,
password varchar(255) NOT NULL,
FOREIGN KEY (user_id) REFERENCES clients(user_id)
);

insert into clients (email, fullname) values
('gjermund.f.haugen@gmail.com', 'Gjermund F. Haugen'),
('tomas@valen.moe', 'Tomas Valen'),
('bv_mrcool@hotmail.com', 'Bjorn Victor V. Jorgensen'),
('jorgen@norstelien.com', 'Jorgen Norstelien');

insert into users (user_id, username, password) values
((select user_id from clients where email='gjermund.f.haugen@gmail.com'), 'jerry', '$2b$12$5j4Ce8SPnwfM9FIOtV99C.w5nNLi8fXKXJNVlDmwliX4wpRYpspLq'),
((select user_id from clients where email='jorgen@norstelien.com'), 'jorgen','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde'),
((select user_id from clients where email='bv_mrcool@hotmail.com'), 'bv','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde'),
((select user_id from clients where email='tomas@valen.moe'), 'tomas','$2b$12$5j4Ce8SPnwfM9FIOtV99C.MsUtG5VnkGQ3TSwdvYd2ZCXiI4W5lde');
