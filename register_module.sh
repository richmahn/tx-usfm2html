#!/usr/bin/env bash

API_URL=$1

curl --header "Content-Type: application/json" -X POST --data @functions/register/module.json $API_URL

