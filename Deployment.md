# Raspberry pi Deployment Guide:

- Install the needed packages:

	```sudo apt-get install python3-pip ```

	```sudo apt-get install python3-venv```

	```python3 -m	venv budget_app/venv ```

- Inside the budget_app:

	- Activate the virtual enviroment:

		```source venv/bin/activate ```

	- Install Nginx and Gunicorn:

		```sudo apt-get install nginx```

		```pip install gunicorn```

	- Remove the default Ngnix file:

		```sudo rm /etc/nginx/sites-enabled/default```

	- Create the budget_app nginx config file:

		```sudo nano /etc/nginx/sites-enabled/budget_app```

		- Config file:

				server{
					listen 80;
					server_name [YOUR_IP_ADDRESS];

					location /static {
						alias /budget_app/budget_app/static; # Complete path to static files.

					}

					location / {
						proxy_pass http://localhost:8000;
						include /etc/nginx/proxy_params;
						proxy_redirect off;
					}
				}

	- Install supervisor to handle the gunicorn startup:

		```sudo apt-get install supervisor```

	- Create supervisor config file:

		```sudo nano /etc/supervisor/conf.d/budget_app.conf```
		- Config file:

				[program:budget_app]
				directory=[Directory to budget_app]
				# -w is the number of workers the number of workers is (num_cores x 2) + 1.
				# To see the number of cores in your machine: proc --all
				command=/home/zacpowerr/Documents/Git/budget_app/venv/bin/gunicorn -w 5 main:app # Complete path to venv/bin/gunicorn 
				user=zacpowerr # user
				autostart=true
				autorestart=true
				stopasgroup=true
				killasgroup=true
				stderr_logfile=/var/log/budget_app.err.log
				stdout_logfile=/var/log/budget_app.out.log

	- Create directories to log and error files:

		```sudo mkdir -p /var/log/budget_app```

		```sudo touch /var/log/budget_app.err.log```
		
		```sudo touch /var/log/budget_app.out.log```

	- Restart supervisor:

		```sudo service supervisor restart``` 