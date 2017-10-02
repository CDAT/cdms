export UVCDAT_ANONYMOUS_LOG=False
export PATH=${HOME}/miniconda/bin:${PATH}
echo "CIRCLE CI BRANCH:"$CIRCLE_BRANCH
echo "CI_PULL_REQUESTS"$CI_PULL_REQUESTS
echo "CI_PULL_REQUEST"$CI_PULL_REQUEST
source activate py2
python run_tests.py -v2 -s
RESULT=$?
source activate py3
python run_tests.py -v2 -s
RESULT=$RESULT+$?
if [ $RESULT -eq 0 -a $CIRCLE_BRANCH != "master" ]; then bash ./ci-support/conda_upload.sh ; fi
exit $RESULT
