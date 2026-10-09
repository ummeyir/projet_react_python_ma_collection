#!/usr/bin/env bash
set -e

cleanup() {
  docker compose down
}

trap cleanup EXIT INT TERM

docker compose up --build -d
npm --prefix web run dev
