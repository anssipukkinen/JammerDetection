# Test Instructions

## Running Tests

To run the tests, execute the following command from the project root directory:

```bash
PYTHONPATH=. python test/test_data_processing_pos.py -v
```

The `PYTHONPATH=.` is required to ensure Python can find the project modules correctly.

## Test Files

The tests use the following data files:
- `agc-test-data.csv`: AGC test data
- `nmea-test-data.csv`: NMEA test data
- `pos-sample-test.data`: Position test data
- `test_output.csv`: Output file for test results

## Test Cases

The test suite includes tests for:
- AGC file parsing
- NMEA file parsing
- Position file parsing
- AGC record matching
- File processing
- Constellation mapping
- SNR validation
