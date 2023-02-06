#!/usr/bin/env bash

root@nuclio:~# su - postgres
$ createuser dbusername
$ createdb dbwriter -O dbusername
$ psql -c "alter user postgres with password 'StrongDBPassword'"
$ psql
postgres=# alter user dbusername with password 'dbpassword';
postgres=# GRANT ALL PRIVILEGES ON DATABASE dbwriter TO dbusername;
postgres=# \c dbwriter

postgres=# CREATE SEQUENCE companies_seq START WITH 1;
postgres=# CREATE TABLE companies (
  id            TEXT NOT NULL DEFAULT 'companies_'||nextval('companies_seq'::regclass),
  name          VARCHAR(100) NOT NULL,
  registered    BOOLEAN NOT NULL,
  zipcode       integer NOT NULL,
  country       VARCHAR(100) NOT NULL
);

postgres=# insert into companies (id, name, registered, zipcode, country) values ('default/sample', 'Amazon', true, 11111, 'USA');


kubectl api-resources | grep PgdbWriter
kubectl get pgdbw
kubectl logs -f deployment/pgdb-writer-operator -n dbwriter
kubectl delete -f k8s/applied-datas/first-data.yaml

kubectl scale deployment pgdb-writer-operator -n dbwriter --replicas 0

watch -n1 'PGPASSWORD=dbpassword psql -U dbusername -h 192.168.184.110 -d dbwriter -c "select * from companies;"'
