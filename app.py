import time
import threading
import logging
from flask import Flask

# Configure standard application logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global list to hold leaked memory data in RAM
leaked_memory = []

def leak_memory():
    """
    Simulates a memory leak.
    Starts with ~100MB, adds ~3MB per second.
    Reaches ~1GB in 5 minutes (300 seconds).
    """
    logger.info("Initializing memory leak background process...")
    
    try:
        # Initial 100MB allocation using bytearray
        leaked_memory.append(bytearray(100 * 1024 * 1024))
        logger.info("Allocated initial 100MB.")
    except MemoryError:
        logger.error("Failed initial memory allocation.")

    # 3MB chunks per second
    chunk_size = 3 * 1024 * 1024 
    
    while True:
        time.sleep(1)
        try:
            leaked_memory.append(bytearray(chunk_size))
            
            # Log memory status every 10 seconds to avoid spamming the console
            if len(leaked_memory) % 10 == 0:
                current_mb = 100 + (len(leaked_memory) - 1) * 3
                logger.info(f"App running. Current memory footprint: ~{current_mb} MB")
                
        except MemoryError:
            logger.error("CRITICAL: Out of memory!")
            break

@app.route('/')
def home():
    logger.info("Received request on root endpoint '/'")
    return "Microservice is running (and leaking memory!)", 200

@app.route('/health')
def health():
    # Standard health check endpoint for Kubernetes
    logger.info("Health check pinged")
    return "OK", 200

if __name__ == '__main__':
    # Start the memory leak in a separate background thread
    leak_thread = threading.Thread(target=leak_memory, daemon=True)
    leak_thread.start()
    
    # Run server on 0.0.0.0 to allow external connections (Bandit scan will flag this, which is expected)
    logger.info("Starting web server on 0.0.0.0:8080...")
    app.run(host='0.0.0.0', port=8080)