create database if not exists posture_correction_db;

use posture_correction_db;

create table if not exists users (
    id int primary key auto_increment,
    name varchar(255) not null,
    password varchar(255) not null default "",
    email varchar(255) default null,
    token varchar(255) default null,
    is_admin boolean default false,
    standard_posture_id int default null,
    created_at timestamp(3) default current_timestamp(3),
    updated_at timestamp(3) default current_timestamp(3) on update current_timestamp(3)
);

create table if not exists postures (
    id int primary key auto_increment,
    user_id int not null,
    app_id varchar(32) not null,
    file_name varchar(255) default "",
    sensor_alpha double not null,
    sensor_beta double not null,
    sensor_gamma double not null,
    face_pitch double,
    face_roll double,
    face_yaw double,
    nose_x double,
    nose_y double,
    neck_x double,
    neck_y double,
    neck_to_nose double,
    standard_distance double,
    neck_angle double,
    created_at timestamp(3) default current_timestamp(3),
    updated_at timestamp(3) default current_timestamp(3) on update current_timestamp(3),
    foreign key (user_id) references users(id)
);

create table if not exists projects (
    id int primary key auto_increment,
    app_id varchar(32) not null,
    name text not null,
    owner_user_token varchar(255) not null,
    created_at timestamp default current_timestamp,
    updated_at timestamp default current_timestamp
);
