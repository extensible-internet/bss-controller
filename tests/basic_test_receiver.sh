#!/bin/bash

# For sudo later, enter password
sudo echo ''

./pox.py bss-controller &
sleep 2
python3 ext/bss-controller/tests/basic_test_receiver.py
exitcode=$?
sudo pkill -f " \./pox\.py"
sleep 1

if [[ $exitcode != 0 ]]; then
echo "TEST FAILED"
else
echo "TEST PASSED"
fi

exit $exitcode
