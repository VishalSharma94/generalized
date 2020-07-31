USER_DB=ricardo
PASSWORD_DB=12345
DB_ENDPOINT=www.db.com
USER_DW=ricardo2
PASSWORD_DW=12345
DW_ENDPOINT=www.dw.com
REDIS_ENDPOINT=www.redis.com
REDIS_PORT=1234
RABBITMQ_HOST=www.rabbit.com
RABBITMQ_PORT=3456
RABBITMQ_USER=rabituser
RABBITMQ_PASSWORD=rabbitpass

REGION=us-west-1
MEMCACHE_CLUSTER=us-prod

CONF_TYPE=rts

if [ $CONF_TYPE = 'tomcat' ]
then
  if [ $ENV = "prod" ]
  then
    echo "============================================================"
    echo " >>>>> using prod.xml"
    cp files/prod.xml context.xml
    echo "============================================================"
  else
    echo "============================================================"
    echo " >>>>> using non-prod.xml"
    cp files/non-prod.xml context.xml
    echo "============================================================"
  fi
  echo "============================================================"
  echo " >>>>> Configuring DB ENDPOINTS"
  sed -i 's/{{USER_DB}}/'$USER_DB'/g' context.xml
  sed -i 's/{{PASSWORD_DB}}/'$PASSWORD_DB'/g' context.xml
  sed -i 's/{{DB_ENDPOINT}}/'$DB_ENDPOINT'/g' context.xml
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring DW ENDPOINTS"
  sed -i 's/{{USER_DW}}/'$USER_DW'/g' context.xml
  sed -i 's/{{PASSWORD_DW}}/'$PASSWORD_DW'/g' context.xml
  sed -i 's/{{DW_ENDPOINT}}/'$DW_ENDPOINT'/g' context.xml
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring REDIS ENDPOINTS"
  sed -i 's/{{REDIS_ENDPOINT}}/'$REDIS_ENDPOINT'/g' context.xml
  sed -i 's/{{REDIS_PORT}}/'$REDIS_PORT'/g' context.xml
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring RABBIT MQ ENDPOINTS"
  sed -i 's/{{RABBITMQ_HOST}}/'$RABBITMQ_HOST'/g' context.xml
  sed -i 's/{{RABBITMQ_PORT}}/'$RABBITMQ_PORT'/g' context.xml
  sed -i 's/{{RABBITMQ_USER}}/'$RABBITMQ_USER'/g' context.xml
  sed -i 's/{{RABBITMQ_PASSWORD}}/'$RABBITMQ_PASSWORD'/g' context.xml
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring Memcache Endpoints"
  MEMCACHENODES=$(aws elasticache describe-cache-clusters --region $REGION --cache-cluster-id $MEMCACHE_CLUSTER --show-cache-node-info | jq -r '.CacheClusters[0].CacheNodes' | jq '.[] | .Endpoint.Address')
  x=1
  for i in $MEMCACHENODES
  do
    RES=$RES'n'$x':'$i':'$MEMPORT','
    RES2=$RES2$i':'$MEMPORT','
    x=$(($x+1))
  done
  NODES1=$(echo $RES2 | sed -e 's/"//g' | sed -e 's/,$//g')
  NODES2=$(echo $RES | sed -e 's/"//g' | sed -e 's/,$//g')
  sed -i 's/{{NODES_LIST1}}/'$NODES1'/g' context.xml
  sed -i 's/{{NODES_LIST2}}/'$NODES2'/g' context.xml
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Moving context.xml --> /opt/tomcat/conf"
  echo "============================================================"
fi

if [ $CONF_TYPE = 'rts' ]
then
  echo "============================================================"
  echo " >>>>> using config.js"
  cp files/rts_conf.js config.js
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring REDIS ENDPOINTS"
  sed -i 's/{{REDIS_ENDPOINT}}/'$REDIS_ENDPOINT'/g' config.js
  sed -i 's/{{REDIS_PORT}}/'$REDIS_PORT'/g' config.js
  echo "============================================================"

  echo "============================================================"
  echo " >>>>> Configuring RABBIT MQ ENDPOINTS"
  sed -i 's/{{RABBITMQ_HOST}}/'$RABBITMQ_HOST'/g' config.js
  sed -i 's/{{RABBITMQ_PORT}}/'$RABBITMQ_PORT'/g' config.js
  sed -i 's/{{RABBITMQ_USER}}/'$RABBITMQ_USER'/g' config.js
  sed -i 's/{{RABBITMQ_PASSWORD}}/'$RABBITMQ_PASSWORD'/g' config.js
  echo "============================================================"
fi