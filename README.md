work in progress...


## Launch with Docker

- Clone repo
- `cd SWIFT_API/`
- `docker-compose up -d --build`
- Load data: `docker-compose exec web python /app/app/scripts/load_swift_codes.py`
(`data/Interns_2025_SWIFT_CODES.xlsx` by default, can be changed with --file arg)
- Run tests: `docker-compose exec web pytest /app/tests/`
   
   `docker-compose logs -f web`

   `docker-compose stop`
   `docker-compose start`
   
   `docker-compose down -v`