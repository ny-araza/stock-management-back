### DEMARER LE SERVEUR MYSQLD
```bash
    bin/mysqld_safe --defaults-file=$HOME/goinfre/my.cnf &
```

### DEMARER LE SERVEUR MYSQL
```bash
/home/ny-araza/goinfre/mysql/bin/mysql \
  --defaults-file=$HOME/goinfre/my.cnf \
  -u root -p
```

### configurer le chemin du pkg pour l'insallation de mysqlclient
  + find ~/goinfre/mysql -name "*.pc"
  + export PKG_CONFIG_PATH=$HOME/goinfre/mysql/lib/pkgconfig:$PKG_CONFIG_PATH  
  *tester si le pkg trouve bien le fichier: pkg-config --exists mysqlclient && echo "OK"*
  + modifier le chemin dans le fichier '.pc'
  + par: /home/ny-araza/goinfre/mysql
  + recharger le pkg: export PKG_CONFIG_PATH=$HOME/goinfre/mysql/lib/pkgconfig
  + installer mysql client: pip install mysqlclient