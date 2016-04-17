drop table if exists employees;
create table employees (
  id int primary key not null,
  name string not null
);

drop table if exists users;
create table users (
    username string primary key not null,
    password string not null
);
