drop table if exists USUARIO;
create table USUARIO (
  username text primary key,
  password text not null
);

insert into USUARIO (username, password) values ('maria', 'admin1234');
