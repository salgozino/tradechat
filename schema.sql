DROP TABLE IF EXISTS comments;
create table comments (
	id integer primary key autoincrement,
	comment text not null,
	user text not null,
	time text not null
);

DROP TABLE IF EXISTS users;
create table users (
	id integer primary key autoincrement,
	name text unique not null,
	password text not null
);