#!/bin/bash -ae

# Sets up a Cloud SQL instance, sets the root password, creates an empty database,
# and sets the database connection info in a database config in Datastore.
#
# Note that this script does *not* set up failover for the database. You can do that manually
# in the environments you want.
#
# creds_account can be provided in cases where the user associated with the service account
# needed to update configuration differs from the account that can update AppEngine for the instance
#
# create_instance can be provided to create the database instance the first time

# Example usage for setting up a database initially:
# tools/setup_database.sh --account dan.rodney@pmi-ops.org --project all-of-us-rdr-staging --create_instance
# Example usage for changing root and rdr/alembic/readonly passwords:
# tools/setup_database.sh --account dan.rodney@pmi-ops.org --project all-of-us-rdr-staging --update_passwords

echo "\n!!! Deprecated Tool !!!  use new style database tool. IE: python -m tools mysql."

CREATE_INSTANCE=
UPDATE_PASSWORDS=
CONTINUE_CREATING_INSTANCE=
USAGE="tools/setup_database.sh --account <ACCOUNT> --project <PROJECT> [--creds_account <ACCOUNT>] [--create_instance | --continue_creating_instance| --update_passwords]"
while true; do
  case "$1" in
    --account) ACCOUNT=$2; shift 2;;
    --creds_account) CREDS_ACCOUNT=$2; shift 2;;
    --project) PROJECT=$2; shift 2;;
    --create_instance) CREATE_INSTANCE=Y; shift 1;;
    --continue_creating_instance) CONTINUE_CREATING_INSTANCE=Y; shift 1;;
    --update_passwords) UPDATE_PASSWORDS=Y; shift 1;;
    -- ) shift; break ;;
    * ) break ;;
  esac
done

if [ -z "${ACCOUNT}" ]
then
  echo "Usage: $USAGE"
  exit 1
fi

if [ -z "${PROJECT}" ]
then
  echo "Usage: $USAGE"
  exit 1
fi

if [ -z "${CREDS_ACCOUNT}" ]
then
  CREDS_ACCOUNT="${ACCOUNT}"
fi

source tools/setup_vars.sh

# Get a randomly generated password
function randpw {
    new_password=$(< /dev/urandom LC_CTYPE=C tr -dc _A-Z-a-z0-9 | head -c${1:-16};echo;)
    }

INSTANCE_NAME=rdrmaindb
FAILOVER_INSTANCE_NAME=rdrbackupdb
# Default to a lightweight config; uses a non-shared CPU, with 1 core and 3.75 GB of memory
# (consider making this something different in production).
MACHINE_TYPE=db-n1-standard-1

source tools/auth_setup.sh

if [ "${CREATE_INSTANCE}" = "Y" ]
then
  gcloud beta sql instances create $INSTANCE_NAME --tier=$MACHINE_TYPE --activation-policy=ALWAYS \
      --backup-start-time 00:00 --failover-replica-name $FAILOVER_INSTANCE_NAME --enable-bin-log \
      --database-version MYSQL_5_7 --project $PROJECT --storage-auto-increase
  sleep 3
fi

if [ "${CREATE_INSTANCE}" = "Y" ] || [ "${CONTINUE_CREATING_INSTANCE}" = "Y" ]
then
    # NOTE (from tanner on 2019-05-24): This command does not seem to trigger a database restart *if* the flag value
    #                                   is already at the correct value.
    #                                   This has not been tested thoroughly and may need to be revisited.
    # NOTE (from tanner on 2019-07-01): This sometimes takes longer than the 3 second sleep. For the next iteration of
    #                                   this tool: only apply this change if needed & add wait loop until ready to
    #                                   continue. In the meantime, this may be disabled
    if gcloud sql instances describe ${INSTANCE_NAME} --project ${PROJECT} | grep log_bin_trust_function_creators; then
        echo "Database flags already set."
    else
        echo "Applying correct database flags..."
        gcloud sql instances patch ${INSTANCE_NAME} --database-flags log_bin_trust_function_creators=on \
            --project $PROJECT
        echo "Waiting for database restart..."
        sleep 3
    fi
fi

INSTANCE_CONNECTION_NAME=$(gcloud sql instances describe $INSTANCE_NAME | grep connectionName | cut -f2 -d' ')
BACKUP_INSTANCE_NAME=$(gcloud sql instances describe $FAILOVER_INSTANCE_NAME | grep connectionName | cut -f2 -d' ')

if [ ${PROJECT} = 'all-of-us-rdr-sandbox' ]
then
    BACKUP_INSTANCE_NAME=$INSTANCE_CONNECTION_NAME
fi

UPDATE_DB_FILE=/tmp/update_db.sql

function finish {
  cleanup
  rm -f ${UPDATE_DB_FILE}
}
trap finish EXIT

run_cloud_sql_proxy
if [ "${UPDATE_PASSWORDS}" = "Y" ] || [ "${CREATE_INSTANCE}" = "Y" ] || [ "${CONTINUE_CREATING_INSTANCE}" = "Y" ]
  then
 	echo "Updating database user passwords..."
	randpw
	ROOT_PASSWORD=$new_password
	randpw
	RDR_PASSWORD=$new_password
	randpw
	READONLY_PASSWORD=$new_password

  CONNECTION_STRING="mysql+mysqldb://${RDR_DB_USER}:${RDR_PASSWORD}@/$DB_NAME?unix_socket=/cloudsql/$INSTANCE_CONNECTION_NAME&charset=utf8"
  BACKUP_CONNECTION_STRING="mysql+mysqldb://${RDR_DB_USER}:${RDR_PASSWORD}@/$DB_NAME?unix_socket=/cloudsql/$BACKUP_INSTANCE_NAME&charset=utf8"

	echo '{"db_connection_string": "'$CONNECTION_STRING'", ' \
	     ' "backup_db_connection_string": "'$BACKUP_CONNECTION_STRING'", ' \
	     ' "rdr_db_password": "'$RDR_PASSWORD'", ' \
	     ' "root_db_password": "'$ROOT_PASSWORD'", ' \
	     ' "read_only_db_password": "'$READONLY_PASSWORD'", ' \
	     ' "db_connection_name": "'$INSTANCE_CONNECTION_NAME'", '\
	     ' "backup_db_connection_name": "'$BACKUP_INSTANCE_NAME'", '\
	     ' "db_user": "'$RDR_DB_USER'", '\
	     ' "db_name": "'$DB_NAME'" }' > $TMP_DB_INFO_FILE

	echo "Setting root password..."
	gcloud sql users set-password root --host % --instance $INSTANCE_NAME --password $ROOT_PASSWORD

	if [ "${CREATE_INSTANCE}" = "Y" ] || [ "${CONTINUE_CREATING_INSTANCE}" = "Y" ]
    then
		echo "Queueing database creation commands"
		for db_name in "rdr" "metrics" "rdr_tasks"; do
		   cat tools/create_db.sql | envsubst >> $UPDATE_DB_FILE
		   cat tools/grant_permissions.sql | envsubst >> $UPDATE_DB_FILE
		done
	fi

    echo "Queueing password change commands"
    cat tools/update_passwords.sql | envsubst >> $UPDATE_DB_FILE

	echo "applying database changes..."
	mysql -u "$ROOT_DB_USER" -p"$ROOT_PASSWORD" --host 127.0.0.1 --port ${PORT} < ${UPDATE_DB_FILE} && echo "done" || echo "failed - you will likely need to generate passwords"
	echo "Setting database configuration..."
	tools/install_config.sh --key db_config --config ${TMP_DB_INFO_FILE} --instance $INSTANCE --update --creds_file ${CREDS_FILE}
else
	echo "Setting permissions for database"
	for db_name in "rdr" "metrics" "rdr_tasks"; do
	   cat tools/grant_permissions.sql | envsubst >> $UPDATE_DB_FILE
	done
	get_db_password $ROOT_DB_USER
	mysql -u "$ROOT_DB_USER" -p"${PASSWORD}" --host 127.0.0.1 --port ${PORT} < ${UPDATE_DB_FILE}
fi

echo "Done."

