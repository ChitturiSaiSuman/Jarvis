#!/usr/bin/python3

import datetime
import logging
import time

import requests

logging.basicConfig(filename='example.log', level=logging.DEBUG)

class Nebula:
    status_map = {
        requests.codes.ok: "Up and running!", # 200
        requests.codes.not_found: "Not found on the server", # 404
        requests.codes.forbidden: "Forbidden to access", # 403
        requests.codes.internal_server_error: "Encountered an internal server error", # 500
        'Unknown': "Returned an unexpected status code!",
    }

    def get(url: str) -> tuple:
        try:
            response = requests.get(url)
            if response.status_code in Nebula.status_map:
                return (response.status_code, response.reason, Nebula.status_map[response.status_code])
            else:
                return (response.status_code, response.reason, Nebula.status_map['Unknown'])

        except Exception as e:
            return e

    class StatusObserver:
        def __init__(self, url: str, expected_status: int) -> None:
            self.url = url
            self.expected_status = expected_status

        def stalk(self, interval=10, timeout=3600) -> str:
            resp = Nebula.get(self.url)
            reachable = not isinstance(resp, Exception)
            if not reachable:
                message = "Error! Couldn't send http request to the specified URL."
                message += '\n'
                message += f"Error Message: {Nebula.get(self.url)}"
                return message
            logging.info(f"Got response {resp}")

            message = None
            start_time = datetime.datetime.now()
            attempt_count = 0

            while (datetime.datetime.now() - start_time).seconds < timeout:
                attempt_count += 1
                response = requests.get(self.url)
                if response.status_code == self.expected_status:
                    message = "Status code match detected after {} attempts. The website is functioning as expected.".format(attempt_count)
                    break
                time.sleep(interval)
            else:
                message = "The monitoring process has ended without success. The website did not respond with the expected status code after {} attempts and {} seconds of waiting.".format(attempt_count, timeout)

            return message


if __name__ == '__main__':
    url = "https://www.comcast.com"
    expected_code = 200
    observer = Nebula.StatusObserver(url, expected_code)
    print(observer.stalk())