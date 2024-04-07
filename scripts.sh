#!/bin/sh

echo "Choose console command to run"
echo "0 - fastapi uvicorn app"
echo "1 - celery app (4 threads)"
echo "2 - celery app (solo)"
echo "3 - celery app flower"
while :
do
  read -r INT_INPUT
  case $INT_INPUT in
	0)
		uvicorn main:icydota_api --reload --workers 1 --port 3333
		break
		;;
	1)
		celery --app=celery_app worker --concurrency=4 -l INFO -E -P gevent
		break
		;;
	2)
		celery --app=celery_app worker --concurrency=4 -l INFO -E -P solo
		break
		;;
	3)
		celery --app=celery_app flower --basic-auth=mx:ghbdtn
		break
		;;
	*)
		echo "Do not understand. Try again"
		;;
  esac
done
