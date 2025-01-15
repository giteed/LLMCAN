#!/usr/bin/env python3
# agents/external_interactions.py
# Version: 1.1.0
# Purpose: Manage interactions with external systems like Tor and ddgr.

import subprocess
import json
import time
import logging

logger = logging.getLogger(__name__)

def check_tor_connection():
    try:
        result = subprocess.run(["systemctl", "is-active", "tor"], capture_output=True, text=True, timeout=10)
        return result.stdout.strip() == "active"
    except subprocess.CalledProcessError:
        return False

def restart_tor():
    try:
        subprocess.run(["systemctl", "restart", "tor"], check=True, timeout=30)
        time.sleep(5)
        logger.info("TOR successfully restarted.")
        return True
    except subprocess.TimeoutExpired:
        logger.error("Timeout while restarting TOR.")
        return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Error restarting TOR: {e}")
        return False

def query_ddgr(search_query, use_tor=False, max_retries=3):
    retries = 0
    while retries < max_retries:
        command = ["torsocks", "ddgr", "--json", search_query] if use_tor else ["ddgr", "--json", search_query]
        try:
            logger.debug(f"Executing command: {' '.join(command)}")
            result = subprocess.check_output(command, universal_newlines=True)
            return json.loads(result)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            logger.error(f"Error during ddgr query: {e}")
            if use_tor:
                logger.info("Restarting TOR due to ddgr error...")
                restart_tor()
            retries += 1
            time.sleep(2)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            break
    logger.error(f"Failed to execute ddgr query after {max_retries} retries.")
    return None
