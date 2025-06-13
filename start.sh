#!/bin/sh

echo "Choose console command to run"
echo "0 - fastapi uvicorn app"
echo "1 - celery app (solo)"
echo "2 - celery app (2 threads (prefork))"
echo "3 - celery app (4 threads)"
echo "4 - celery app (8 threads)"
echo "5 - celery app flower"
echo "6 - celery purge queue"
while :
do
  read -r INT_INPUT
  case $INT_INPUT in
	0)
		uvicorn main:icydota_api --use-colors --log-level 'trace' --reload --workers 2 --port 3333
		break
		;;
	1)
		celery --app=celery_app worker --concurrency=1 -l INFO -E -P solo
		break
		;;
  2)
		celery --app=celery_app worker --concurrency=2 -l INFO -E -P prefork
		break
		;;
  3)
		celery --app=celery_app worker --concurrency=4 -l INFO -E -P gevent
		break
		;;
	4)
		celery --app=celery_app worker --concurrency=8 -l INFO -E -P gevent
		break
		;;
	5)
		celery --app=celery_app flower
		break
		;;
  6)
    celery --app=celery_app purge
		break
		;;
	*)
		echo "Do not understand. Try again"
		;;
  esac
done
