# Hitung Tagihan (Electricity Bill Calculator)

A Streamlit-based web application to calculate electricity consumption and costs for household appliances in Indonesia.

## Features

- Calculate electricity consumption for common household appliances
- Predefined list of appliances with typical power consumption values
- Calculate daily, monthly, and yearly electricity costs
- Easy-to-use interface with Streamlit
- Support for multiple devices and usage patterns

## Installation

1. Clone this repository:
```bash
git clone https://github.com/anggakawa/kalkulatorlistrik.git
cd kalkulatorlistrik
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
streamlit run main.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Select appliances from the dropdown menu or add custom devices

4. Enter usage hours and days to calculate electricity consumption and costs

## Dependencies

- Python 3.x
- streamlit==1.31.1
- pandas==2.2.0
- requests==2.31.0

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.