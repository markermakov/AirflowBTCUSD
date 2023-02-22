ETL-процесс по выгрузке курса криптовалют

*Процесс создавался и тестировался в MacOS окружении и при заранее установленном и запущенном Docker
Две главные составляющие проекта:
- Airflow DAG ETL.py, в котором происходит подключение к базе и запись полученного результата
- docker-compose файлы, запускающие контейнеры со всеми необходимыми компонентами (airflow, postgre и т.д.)

Чтобы поднять процесс необходимо запустить Docker и выполнить следующие команды (при попытке обернуть все в один условный runner.sh вылезали проблемы, поэтому для простоты и стабильности будет использован императивный ручной ввод команд):
- Перейти в директорию с проектом
  ```console 
  cd ~/directory/AirflowBTCUSD
  
- Подтянуть файл с переменными, создать локальную сеть и запустить docker-compose
    ```console
  source env.env
  docker network create my_net
  docker-compose --env-file ./env.env -f ./docker-compose.yaml up -d
- Выдать права на чтение директорий и добавить переменные с айди юзера в .env файл
    ```console
  chmod -R 777 ./dags ./logs ./plugins
  echo -e "\n" >> env.env
  echo -e "AIRFLOW_UID=$(id -u)" >> env.env
  echo -e "AIRFLOW_GID=0" >> env.env
- Поднять контейнеры с airflow и вызвать финальный docker-compose
  ```console
  docker-compose -f airflow-docker-compose.yaml up airflow-init
  docker-compose -f airflow-docker-compose.yaml up -d
  docker-compose up
Спустя несколько минут, когда установочные процессы завершатся, перейти на http://localhost:8080/, где и появится DAG ETL

Остается только включить DAG, далее он будет выполняться с периодичностью в 3 часа. 

Чтобы затушить процесс, необходимо выполнить эти команды:
```console
docker-compose -f airflow-docker-compose.yaml down --volumes --rmi all
docker-compose -f docker-compose.yaml down --volumes --rmi all
docker network rm my_net
```

Спасибо за внимание!
