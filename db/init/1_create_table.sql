create database if not exists posture_correction_db;

use posture_correction_db;

create table if not exists users (
    id int primary key auto_increment,
    username varchar(255) not null,
    password varchar(255) not null,
    email varchar(255) default null,
    neck_to_nose_standard double default null,
    created_at timestamp default current_timestamp
    updated_at timestamp default current_timestamp on update current_timestamp
);

create table if not exists postures (
    id int primary key auto_increment,
    user_id int not null,
    sensor_alpha double not null,
    sensor_beta double not null,
    sensor_gamma double not null,
    face_pitch double not null,
    face_roll double not null,
    face_yaw double not null,
    neck_to_nose double not null,
    standard_distance double not null,
    neck_angle double not null,
    created_at timestamp default current_timestamp
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id)
);