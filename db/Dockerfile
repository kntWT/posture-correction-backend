FROM mariadb:lastest

COPY init/*.sql /docker-entrypoint-initdb.d/
COPY my.cnf /etc/mysql/conf.d/my.cnf

CMD ["mysqld", "--character-set-server=utf8mb4", "--collation-server=utf8mb4_unicode_ci", "--default-authentication-plugin=mysql_native_password", "--innodb-use-native-aio=0"]
