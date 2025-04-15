bind = "0.0.0.0:10000"
workers = 4
timeout = 120
wsgi_app = "app:app"
accesslog = "-"
errorlog = "-"
capture_output = True 