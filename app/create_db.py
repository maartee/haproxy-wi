#!/usr/bin/env python3
import cgi
import html
import os
import sys
import funct

mysql_enable = funct.get_config_var('mysql', 'enable')

if mysql_enable == '1':
	mysql_user = funct.get_config_var('mysql', 'mysql_user')
	mysql_password = funct.get_config_var('mysql', 'mysql_password')
	mysql_db = funct.get_config_var('mysql', 'mysql_db')
	mysql_host = funct.get_config_var('mysql', 'mysql_host')
	from mysql.connector import errorcode
	import mysql.connector as sqltool
else:
	fullpath = funct.get_config_var('main', 'fullpath')
	db = fullpath+"/app/haproxy-wi.db"
	import sqlite3 as sqltool
	
def check_db():
	if mysql_enable == '0':
		if os.path.isfile(db):
			if os.path.getsize(db) > 100:
				with open(db,'r', encoding = "ISO-8859-1") as f:
					header = f.read(100)
					if header.startswith('SQLite format 3'):
						return False
					else:
						return True
		else:
			return True
	else:
		con, cur = get_cur()
		sql = """ select id from `groups` where id='1' """
		try:
			cur.execute(sql)
		except sqltool.Error as err:
			print('<div class="alert alert-danger">')
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Something is wrong with your user name or password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			print('</div>')
			return True
		else:
			return False
			con.close()
			
def get_cur():
	try:
		if mysql_enable == '0':
			con = sqltool.connect(db, isolation_level=None)  
		else:
			con = sqltool.connect(user=mysql_user, password=mysql_password,
									host=mysql_host,
									database=mysql_db)	
		cur = con.cursor()
	except sqltool.Error as e:
		print("An error occurred:", e)
	else:
		return con, cur
			
def create_table():
	con, cur = get_cur()
	if mysql_enable == '0':
		sql = """
		CREATE TABLE IF NOT EXISTS user (
			`id`	INTEGER NOT NULL,
			`username`	VARCHAR ( 64 ) UNIQUE,
			`email`	VARCHAR ( 120 ) UNIQUE,
			`password`	VARCHAR ( 128 ),
			`role`	VARCHAR ( 128 ),
			`groups`	VARCHAR ( 120 ),
			PRIMARY KEY(`id`) 
		);
		INSERT INTO user (username, email, password, role, groups) VALUES ('admin','admin@localhost','admin','admin','1'),
		 ('editor','editor@localhost','editor','editor','1'),
		 ('guest','guest@localhost','guest','guest','1');
		CREATE TABLE IF NOT EXISTS `servers` (
			`id`	INTEGER NOT NULL,
			`hostname`	VARCHAR ( 64 ) UNIQUE,
			`ip`	VARCHAR ( 64 ) UNIQUE,
			`groups`	VARCHAR ( 64 ),
			PRIMARY KEY(`id`) 
		);
		CREATE TABLE IF NOT EXISTS `roles_users` (
			`user_id`	INTEGER,
			`role_id`	INTEGER,
			FOREIGN KEY(`user_id`) REFERENCES `user`(`id`),
			FOREIGN KEY(`role_id`) REFERENCES `role`(`id`)
		);
		CREATE TABLE IF NOT EXISTS `role` (
			`id`	INTEGER NOT NULL,
			`name`	VARCHAR ( 80 ) UNIQUE,
			`description`	VARCHAR ( 255 ),
			PRIMARY KEY(`id`) 
		);
		INSERT INTO `role` (name, description) VALUES ('admin','Can do everything'),
		 ('editor','Can edit configs'),
		 ('guest','Read only access');
		
		CREATE TABLE IF NOT EXISTS `groups` (
			`id`	INTEGER NOT NULL,
			`name`	VARCHAR ( 80 ) UNIQUE,
			`description`	VARCHAR ( 255 ),
			PRIMARY KEY(`id`)
		);
		INSERT INTO `groups` (name, description) VALUES ('All','All servers enter in this group');	
		
		CREATE TABLE IF NOT EXISTS `servers` (
			`id`	INTEGER NOT NULL,
			`hostname`	VARCHAR ( 64 ) UNIQUE,
			`ip`	VARCHAR ( 64 ) UNIQUE,
			`groups`	VARCHAR ( 64 ),
			PRIMARY KEY(`id`)
		);		
		CREATE TABLE IF NOT EXISTS `uuid` (
			`user_id`	INTEGER NOT NULL,
			`uuid`	varchar ( 64 )
		);
		CREATE TABLE IF NOT EXISTS `cred` (
			`enable`	INTEGER NOT NULL DEFAULT 1,
			`username`	VARCHAR ( 64 ) NOT NULL,
			`password`	VARCHAR ( 64 ) NOT NULL
		);
		CREATE TABLE IF NOT EXISTS `token` (
			`user_id`	INTEGER,
			`token`	varchar(64),
			`exp`  DATETIME default '0000-00-00 00:00:00'
		);
		insert into cred('enable','username','password') values ('1', 'root','password');
		"""
		try:
			cur.executescript(sql)
		except sqltool.Error as e:
			print("An error occurred:", e)
			return False
		else:
			return True
	else:
		try: 
			for line in open("haproxy-wi.db.sql"):
				cur.execute(line)
		except sqltool.Error as e:
			print('<div class="alert alert-danger">')
			print("An error occurred:", e)
			print('</div>')
			return False
		else:
			return True
	cur.close() 
	con.close()
	
def update_db_v_2_0_1(**kwargs):
	con, cur = get_cur()
	sql = """
	ALTER TABLE `servers` ADD COLUMN type_ip INTEGER NOT NULL DEFAULT 0;
	"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: type_ip':
				print('Updating... go to version 2.0.1.1<br />')
			else:
				print("An error occurred:", e)
		return False
	else:
		print("DB was update to 2.0.1<br />")
		return True
	cur.close() 
	con.close()

def update_db_v_2_0_1_1(**kwargs):
	con, cur = get_cur()
	sql = """
	ALTER TABLE `servers` ADD COLUMN enable INTEGER NOT NULL DEFAULT 1;
	"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: enable' or e == "1060 (42S21): Duplicate column name 'enable' ":
				print('Updating... go to version 2.0.5<br />')
			else:
				print("An error occurred:", e)
		return False
	else:
		print("DB was update to 2.0.1.1<br />")
		return True
	cur.close() 
	con.close()
	
def update_db_v_2_0_5(**kwargs):
	con, cur = get_cur()
	sql = """
	ALTER TABLE `servers` ADD COLUMN master INTEGER NOT NULL DEFAULT 0;
	"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: master' or e == "1060 (42S21): Duplicate column name 'master' ":
				print('Updating... go to version 2.4<br />')
			else:
				print("An error occurred:", e)
		return False
	else:
		print("DB was update to 2.0.5<br />")
		return True
	cur.close() 
	con.close()
	
def update_db_v_2_4(**kwargs):
	con, cur = get_cur()
	sql = """
	CREATE TABLE IF NOT EXISTS `uuid` (`user_id` INTEGER NOT NULL, `uuid` varchar ( 64 ) );
	"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		print(kwargs.get('silent'))
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: user_id':
				print('Updating... go to version 2.5.3')
			else:
				print("An error occurred:", e)
		return False
	else:
		if kwargs.get('silent') != 1:
			print("DB was update to 2.4 <br />")
		return True
	cur.close() 
	con.close()
	
def update_db_v_2_5_3(**kwargs):
	con, cur = get_cur()
	sql = """
	CREATE TABLE IF NOT EXISTS `cred` (`enable`	INTEGER NOT NULL DEFAULT 1, `username`	VARCHAR ( 64 ) NOT NULL, `password` VARCHAR ( 64 ) NOT NULL );
	"""
	try:    
		cur.execute(sql)		
		con.commit()
	except sqltool.Error as e:
		print(kwargs.get('silent'))
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: enable':
				print('Updating... go to version 2.5.6')
			else:
				print("An error occurred:", e)
		return False
	else:
		if kwargs.get('silent') != 1:
			print("DB was update to 2.5.3<br />")
			sql2 = """
			insert into `cred` (`enable`,`username`,`password`) values ('1', 'root','password');
			"""
			cur.execute(sql2)
			con.commit()
		return True
	cur.close() 
	con.close()

def update_db_v_2_5_6(**kwargs):
	con, cur = get_cur()
	if mysql_enable == '1':
		sql = """
		ALTER TABLE `uuid` ADD COLUMN `exp` timestamp default '0000-00-00 00:00:00';
		"""
	else:
		sql = """
		ALTER TABLE `uuid` ADD COLUMN `exp` DATETIME default '0000-00-00 00:00:00';
		"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: exp' or e == "1060 (42S21): Duplicate column name 'exp' ":
				print('Updating... go to version 2.5.6.1')
			else:
				print("An error occurred:", e)
		return False
	else:
		print("DB was update to 2.5.6.1<br />")
		return True
	cur.close() 
	con.close()

def update_db_v_2_5_6_1(**kwargs):
	con, cur = get_cur()
	if mysql_enable == '1':
		sql = """
		CREATE TABLE IF NOT EXISTS `token` (`user_id` INTEGER, `token` varchar(64), `exp` timestamp default '0000-00-00 00:00:00');
		"""
	else:
		sql = """
		CREATE TABLE IF NOT EXISTS `token` (`user_id` INTEGER, `token` varchar(64), `exp`  DATETIME default '0000-00-00 00:00:00');
		"""
	try:    
		cur.execute(sql)
		con.commit()
	except sqltool.Error as e:
		if kwargs.get('silent') != 1:
			if e.args[0] == 'duplicate column name: token' or e == "1060 (42S21): Duplicate column name 'token' ":
				print('Already updated. No run more. Thx =^.^=')
			else:
				print("An error occurred:", e)
			return False
		else:
			print("DB was update to 2.5.6.1<br />")
			return True
	cur.close() 
	con.close()
	
def update_all():
	update_db_v_2_0_1()
	update_db_v_2_0_1_1()
	update_db_v_2_0_5()
	update_db_v_2_4()
	update_db_v_2_5_3()
	update_db_v_2_5_6()
	update_db_v_2_5_6_1()
	
def update_all_silent():
	update_db_v_2_0_1(silent=1)
	update_db_v_2_0_1_1(silent=1)
	update_db_v_2_0_5(silent=1)
	update_db_v_2_4(silent=1)
	update_db_v_2_5_3(silent=1)
	update_db_v_2_5_6(silent=1)
	update_db_v_2_5_6_1(silent=1)
		