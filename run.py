#!/usr/bin/env python3
from snorren import Snorren

if __name__ == '__main__':
    snorren = Snorren(debug='INFO')
    snorren.run_server(host="0.0.0.0")
