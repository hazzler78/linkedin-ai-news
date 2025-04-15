import multiprocessing

# Gunicorn configuration file
bind = "0.0.0.0:10000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "linkedin_ai_news"

# SSL Configuration (if needed)
# keyfile = "path/to/keyfile"
# certfile = "path/to/certfile"

# Server Mechanics
preload_app = True
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL Configuration
# ssl_version = "TLS"
# cert_reqs = "CERT_NONE"

# Worker Processes
worker_tmp_dir = "/dev/shm"
max_requests = 1000
max_requests_jitter = 50

# Logging Configuration
capture_output = True
enable_stdio_inheritance = True 