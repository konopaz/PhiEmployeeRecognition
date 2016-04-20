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

drop table if exists awards;
create table awards (
    id integer primary key,
    type string not null,
    recipientName string not null,
    recipientEmail string not null,
    creatorEmail string not null,
    date string not null
);
