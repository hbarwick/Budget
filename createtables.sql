CREATE DATABASE budget;

USE budget;

create table users(
   username varchar(30) NOT NULL PRIMARY KEY,
   first_name VARCHAR(30),
   last_name VARCHAR(30),
   email VARCHAR(30),
   password VARCHAR(30)
);

create table bills(
   UID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
   user VARCHAR(30) NOT NULL,
   date DATE,
   bill_name VARCHAR(30) NOT NULL,
   monthly_value FLOAT
);

create table income(
   UID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
   user VARCHAR(30) NOT NULL,
   date DATE,
   income_name VARCHAR(30) NOT NULL,
   value FLOAT,
   recurring BOOLEAN
);

create table payments(
   UID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
   user VARCHAR(30) NOT NULL,
   date DATE,
   value FLOAT NOT NULL,
   category VARCHAR(30) NOT NULL,
   extra_details VARCHAR(30) NOT NULL#
);
