#!/bin/sh
rm -f ./tests/test_credentials.py
echo "autotest_user = 'autotest@pve'" >> ./tests/test_credentials.py
echo "autotest_pw = '$AUTOTEST_PW'" >> ./tests/test_credentials.py