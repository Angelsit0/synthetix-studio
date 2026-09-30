"""Punto de entrada:  python main.py config.json"""
import sys

from synthetix.app import Application

if __name__ == "__main__":
    sys.exit(Application().run(sys.argv))
