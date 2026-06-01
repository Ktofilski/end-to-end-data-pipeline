# Crypto Analytics Pipeline

## Overview

This project extracts cryptocurrency market data from the CoinGecko API, stores raw data in MongoDB, transforms it, and loads it into PostgreSQL for analytics and visualization.

## Architecture

CoinGecko API
- MongoDB (raw layer)
- PostgreSQL (analytics layer)

## Tech Stack

- Python
- Pandas
- MongoDB
- PostgreSQL
- Docker
- SQLAlchemy

## Features

- Automated data ingestion
- Historical data storage
- Duplicate prevention using PostgreSQL constraints
- Analytics-ready data model