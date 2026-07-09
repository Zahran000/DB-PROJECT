-- student course registration system
-- schema.sql — run this in mysql workbench to set up the database
-- prepared by Mohammad Burair, Syed Zahran, Maaz Iqbal | fast nuces karachi | 4th semester

create database if not exists registration_db;
use registration_db;

-- student table
create table if not exists student (
    student_id int auto_increment primary key,
    name varchar(100) not null,
    email varchar(100) unique not null,
    password varchar(255) not null,
    semester int not null
);

-- admin table
create table if not exists admin (
    admin_id int auto_increment primary key,
    name varchar(100) not null,
    email varchar(100) unique not null,
    password varchar(255) not null
);

-- course table
create table if not exists course (
    course_id int auto_increment primary key,
    course_name varchar(150) not null,
    credit_hours int not null,
    max_capacity int not null,
    instructor_name varchar(100) not null
);

-- enrollment table (resolves m:n between student and course)
create table if not exists enrollment (
    enrollment_id int auto_increment primary key,
    student_id int not null,
    course_id int not null,
    enrollment_date date not null,
    status varchar(50) default 'enrolled',
    foreign key (student_id) references student(student_id) on delete cascade,
    foreign key (course_id) references course(course_id) on delete cascade,
    unique key unique_enrollment (student_id, course_id)
);

-- seed default admin account (password: admin123)
insert ignore into admin (name, email, password)
values ('system admin', 'admin@fast.edu.pk', 'admin123');

-- seed some sample courses
insert ignore into course (course_name, credit_hours, max_capacity, instructor_name) values
('database systems', 3, 40, 'dr. ali hassan'),
('software design & analysis', 3, 35, 'dr. sara khan'),
('operating systems', 3, 45, 'dr. bilal ahmed'),
('computer networks', 3, 40, 'dr. nadia malik'),
('data structures & algorithms', 3, 50, 'dr. usman tariq');

select * from course;
