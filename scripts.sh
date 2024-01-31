#!/bin/sh

echo "Choose console command to run"
echo "0 - fastapi uvicorn app"
echo "1 - celery app"
echo "2 - celery app flower"
while :
do
  read -r INT_INPUT
  case $INT_INPUT in
	0)
		uvicorn main:app --reload
		break
		;;
	1)
		celery --app=celery_app worker -l INFO -E
		break
		;;
	2)
		celery --app=celery_app flower
		break
		;;
	*)
		echo "Do not understand. Try again"
		;;
  esac
done
